import datetime
from bs4 import BeautifulSoup
import serial
import tkinter as tk
from tkinter import ttk
from tkinter import StringVar
import time 

ser = serial.Serial('COM3', 9600)  # Replace 'COM3' with the actual COM port where your Arduino is connected

shd = {
    "NIT1": {"ProfName": [], "Schedule_Time": []},
    "NIT2": {"ProfName": [], "Schedule_Time": []},
    "NIT3": {"ProfName": [], "Schedule_Time": []},
    "MTC1": {"ProfName": [], "Schedule_Time": []},
    "MTC2": {"ProfName": [], "Schedule_Time": []},
}

def update_schedule():
    current_time = datetime.datetime.now()
    print(f"Current Time: {current_time.strftime('%I:%M %p')}")

    current_time_str = current_time.strftime("%H:%M:%S")

    for room, data in shd.items():
        new_schedule_time = []
        new_prof_name = []

        for scheduled_time, prof_name in zip(data["Schedule_Time"], data["ProfName"]):
            end_time_str = datetime.datetime.strptime(scheduled_time.split(" to ")[1], "%I:%M %p").strftime("%H:%M:%S")

            if end_time_str >= current_time_str:
                new_schedule_time.append(scheduled_time)
                new_prof_name.append(prof_name)

        data["Schedule_Time"] = new_schedule_time
        data["ProfName"] = new_prof_name

    # Now call print_schedule_table to update the HTML after removing past schedules
    print_schedule_table(current_time)


def remove_passed_schedules_from_html(current_time):
    # Open the existing HTML file
    with open("schedule.html", "r") as html_file:
        soup = BeautifulSoup(html_file, 'html.parser')

    # Find the schedule table in the HTML
    schedule_table = soup.find("table")

    # Create a list to keep track of rows to be removed from the HTML
    rows_to_remove = []

    for index, row in enumerate(schedule_table.find_all("tr")[1:]):  # Skip the header row
        time_sch_td = row.find("td", id="time_sch")

        if time_sch_td is not None:
            schedule_time = time_sch_td.get_text()
            time_parts = schedule_time.split(" to ")

            if len(time_parts) == 2:
                start_time_str, end_time_str = time_parts
                start_time = datetime.datetime.strptime(start_time_str, "%I:%M %p").strftime("%H:%M:%S")
                end_time = datetime.datetime.strptime(end_time_str, "%I:%M %p").strftime("%H:%M:%S")

                if end_time < current_time.strftime("%H:%M:%S"):
                    rows_to_remove.append(index)

    # Remove rows with schedules that have passed from the HTML
    for index in reversed(rows_to_remove):  # Remove rows in reverse order to avoid index issues
        schedule_table.find_all("tr")[index + 1].decompose()  # Add 1 to the index to account for header row

    # Update the HTML file with removed schedules
    with open("schedule.html", "w") as updated_html_file:
        updated_html_file.write(soup.prettify())


def print_schedule_table(current_time):
    # Create an HTML table header
    table = """<table style="width:100%">
                <tr>
                    <th>Room Name</th>
                    <th>Professor Name</th>
                    <th class="time_sch">Schedule Time</th>
                    <th class="status">Status</th>
                </tr>"""

    for room, data in shd.items():
        current_time_str = current_time.strftime("%H:%M:%S")

        # Create a list of schedule items with their start times and index
        schedule_items = [(i, scheduled_time) for i, scheduled_time in enumerate(data["Schedule_Time"])]

        # Sort the schedule items based on the proximity of their start times to the current time
        schedule_items.sort(key=lambda x: datetime.datetime.strptime(x[1].split(" to ")[0], "%I:%M %p"))

        next_class_time = None
        status = []  # Initialize status list

        if schedule_items:
            for i, scheduled_time in schedule_items:
                scheduled_start, scheduled_end = scheduled_time.split(" to ")

                if current_time_str >= datetime.datetime.strptime(scheduled_start, "%I:%M %p").strftime("%H:%M:%S") and \
                        current_time_str <= datetime.datetime.strptime(scheduled_end, "%I:%M %p").strftime("%H:%M:%S"):
                    status.append(f"Ongoing ({scheduled_start} to {scheduled_end})")

                elif current_time_str < datetime.datetime.strptime(scheduled_start, "%I:%M %p").strftime("%H:%M:%S"):
                    next_class_time = f"{scheduled_start} to {scheduled_end}"
                    status.append(f"Next class ({next_class_time})")

        if not status and schedule_items:
            status.append(f"No upcoming classes")
            next_class_time = f"{schedule_items[0][1]}"

        # Add table rows for each room and its schedule
        table += f"""<tr>
                      <td>{room}</td>
                      <td class=profname>{'<br>'.join([data['ProfName'][i] for i, _ in schedule_items])}</td>
                      <td id=time_sch>{'<br>'.join([scheduled_time for _, scheduled_time in schedule_items])}</td>
                      <td time_schd>{'<br>'.join(status)}</td>
                    </tr>"""

    # Close the table tag
    table += "</table>"

    with open("schedule.html", "w") as html_file:
        html_file.write(f"""<!DOCTYPE html>
<html>
<head>
    <link rel="icon" type="image/x-icon" href="T.png">
    <link rel="stylesheet" href="styles.css">
    <title>PalSU Scheduler</title>
    <link href="https://fonts.googleapis.com/css?family=Poppins:300,400,500,600,700" rel="stylesheet">
</head>

<body>
<div class="header">
    <div class="logos-container">
        <img class="logo" src="left_logo.png" alt="Left Logo">
        <img class="logo" src="T.png" alt="T Logo">
        <img class="logo" src="right_logo.png" alt="Right Logo">
    </div>        
    <br>
    <br>
    <br>
    <h1>PSU Scheduler - Information Technology BUILDING (IT)</h1>
</div>

<div class="time-and-date">
    <div id="time"></div>
    <div id="day"></div>
    <div id="date"></div>
</div>

<div class="main-content">
    <div class="schedule">
        {table} <!-- Include the generated table -->
    </div>
</div>


<script src="script.js"></script>
    
</body>
</html>
""")

def check_schedule_conflict(room_schedule, start_time, end_time):
    for scheduled_time in room_schedule["Schedule_Time"]:
        scheduled_start, scheduled_end = scheduled_time.split(" to ")

        existing_start_time = datetime.datetime.strptime(scheduled_start, "%I:%M %p").strftime("%H:%M:%S")
        existing_end_time = datetime.datetime.strptime(scheduled_end, "%I:%M %p").strftime("%H:%M:%S")

        if (start_time <= existing_end_time and end_time >= existing_start_time) or \
           (start_time >= existing_start_time and end_time <= existing_end_time):
            return True

    return False

def run_tikenter():
    root = tk.Tk()
    root.title("Add Schedule")

    # Increase the font size for labels and buttons
    root.option_add("*Font", "helvetica 18")

    # Create a frame to hold the content
    frame = ttk.Frame(root)

    # Room Entry
    room_label = ttk.Label(frame, text="Select Room:")
    room_label.grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)

    room_options = list(shd.keys())
    room_var = tk.StringVar(value=room_options[0])

    room_combobox = ttk.Combobox(frame, textvariable=room_var, values=room_options, state="readonly")
    room_combobox.grid(row=0, column=1, columnspan=2, padx=10, pady=5)

    # Schedule Entry
    schedule_label = ttk.Label(frame, text="Select Start Time:")
    schedule_label.grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)

    time_options = [
    "{:d}:{:02d} {}".format(h if h != 0 else 12, m, "AM" if (h < 12 or h == 24) else "PM") 
    for h in range(1, 13)
    for m in range(0, 60, 2)
] + [
    "{:d}:{:02d} {}".format(h if h != 0 else 12, m, "PM" if h < 12 else "AM") 
    for h in range(1, 13)
    for m in range(0, 60, 2)
]

    start_time_var = StringVar(value=time_options[0])
    end_time_var = StringVar(value=time_options[0])

    start_time_combobox = ttk.Combobox(frame, textvariable=start_time_var, values=time_options, state="readonly")
    start_time_combobox.grid(row=1, column=1, columnspan=2, padx=10, pady=5)

    end_time_label = ttk.Label(frame, text="Select End Time:")
    end_time_label.grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)

    end_time_combobox = ttk.Combobox(frame, textvariable=end_time_var, values=time_options, state="readonly")
    end_time_combobox.grid(row=2, column=1, columnspan=2, padx=10, pady=5)

    validation_label = ttk.Label(frame, text="", foreground="red")
    validation_label.grid(row=3, column=0, columnspan=3, pady=5)

    def submit_schedule():
        room_name = room_var.get().strip()
        start_time = start_time_var.get().strip()
        end_time = end_time_var.get().strip()

        if room_name in shd:
            try:
                user_start, user_end = start_time, end_time
                start_time = datetime.datetime.strptime(user_start, "%I:%M %p").strftime("%H:%M:%S")
                end_time = datetime.datetime.strptime(user_end, "%I:%M %p").strftime("%H:%M:%S")

                current_time = datetime.datetime.now().strftime("%H:%M:%S")

                if end_time < start_time:
                    start_time, end_time = end_time, start_time

                if start_time < current_time:
                    validation_label.config(text="Error: The schedule you entered is in the past relative to the current time.")
                    return

                room_schedule = shd[room_name]

                if check_schedule_conflict(room_schedule, start_time, end_time):
                    validation_label.config(text=f"Conflict: The room {room_name} is already scheduled during that time.")
                    return

                new_schedule_item = {"ProfName": "Bryan Etoquilla", "Schedule_Time": f"{user_start} to {user_end}"}
                room_schedule["Schedule_Time"].append(new_schedule_item["Schedule_Time"])
                room_schedule["ProfName"].append(new_schedule_item["ProfName"])

                sorted_indices = sorted(range(len(room_schedule["Schedule_Time"])), key=lambda i: datetime.datetime.strptime(room_schedule["Schedule_Time"][i].split(" to ")[0], "%I:%M %p"))
                room_schedule["Schedule_Time"] = [room_schedule["Schedule_Time"][i] for i in sorted_indices]
                room_schedule["ProfName"] = [room_schedule["ProfName"][i] for i in sorted_indices]

                shd[room_name] = room_schedule
                print(f"Schedule added for {room_name} with Bryan Etoquilla from {user_start} to {user_end}.")

                print_schedule_table(datetime.datetime.now())

                # Clear the input fields and validation label
                room_combobox.set(room_options[0])
                start_time_combobox.set(time_options[0])
                end_time_combobox.set(time_options[0])
                validation_label.config(text="")
            except ValueError:
                validation_label.config(text="Invalid input format. Please use the format '1:00 PM to 5:00 PM.'")
        else:
            validation_label.config(text="Room not found in the schedule. Please enter a valid room name.")

    # Increase the button size
    submit_button = ttk.Button(frame, text="Submit", command=submit_schedule, style="TButton")
    submit_button.grid(row=4, column=0, columnspan=3, pady=20)

    clear_button = ttk.Button(frame, text="Clear", command=lambda: [room_combobox.set(room_options[0]), start_time_combobox.set(time_options[0]), end_time_combobox.set(time_options[0]), validation_label.config(text="")], style="TButton")
    clear_button.grid(row=5, column=0, columnspan=3, pady=20)

    # Create a custom style to increase the button size
    style = ttk.Style()
    style.configure("TButton", padding=10, font=("Helvetica", 18))

    # Pack the frame to make it adjust to the content
    frame.pack(padx=10, pady=10)

    root.mainloop()

def update_html_schedule():
    current_time = datetime.datetime.now()
    print_schedule_table(current_time)

def add_schedule_with_gui():
    print("Scan your RFID card!")
    uid_data = ser.readline().decode().strip()
    if uid_data == "Bryan Etoquilla":
        uid_data = "Bryan Etoquilla"
        print("Recognized")
        run_tikenter()

        # Update the HTML schedule after GUI operation
        update_html_schedule()

while True:
    update_schedule()
    add_schedule_with_gui()
