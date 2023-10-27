import datetime
from bs4 import BeautifulSoup
import serial

ser = serial.Serial('COM3', 9600)  # Replace 'COM3' with the actual COM port where your Arduino is connected

shd = {
    "room1": {"ProfName": [], "Schedule_Time": []},
    "room2": {"ProfName": [], "Schedule_Time": []},
    "room3": {"ProfName": [], "Schedule_Time": []},
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
                    <th>Schedule Time</th>
                    <th>Status</th>
                </tr>"""

    for room, data in shd.items():
        current_time_str = current_time.strftime("%H:%M:%S")

        # Create a list of schedule items with their start times and index
        schedule_items = [(i, scheduled_time) for i, scheduled_time in enumerate(data["Schedule_Time"])]


        # Sort the schedule items based on the proximity of their start times to the current time
        schedule_items.sort(key=lambda x: datetime.datetime.strptime(x[1].split(" to ")[0], "%I:%M %p"))

        next_class_time = None
        status = []  # Initialize status list

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
    <meta http-equiv="refresh" content="5">
    <link rel="icon" type="image/x-icon" href="T.jpg">
    <title>PSU</title>

    <style>
        .tm{{
            margin-top: 60px;
            margin-bottom: 100px;
            display: flex;
            color: white;
        }}
        .center {{
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 8%;
        }}

        img {{
            border-radius: 100%;
        }}

        body {{
            background-image: url("1.png");
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-size: 100% 100%;
        }}

        table, th, td, tr{{
            border-spacing: 30px;
            font-size: large;
        }}
        th {{
            border: 10px solid rgb(255, 136, 0);
            opacity: 0.8;
            border-radius: 10px;
            border-collapse: collapse;
            padding-top: 5px;
            padding-bottom: 5px;
            padding-left: 5px;
            padding-right: 5px;
            background-color: rgb(255, 136, 0);
        }}
        td {{
            border: 1px solid rgba(255, 136, 0, 0.58);
            opacity: 0.8;
            border-collapse: collapse;
            padding-left: 5px;
            padding-top: 5px;
            padding-bottom: 5px;
            padding-right: 5px;
            background-color: rgba(255, 136, 0, 0.58);
        }}

        #time {{
            font-size: 50px;
            color: #fefefe;
        }}
        #day {{
            color: white;
            font-size: 25px;
            font-weight: bold;
        }}
        #date {{
            color: white;
            font-size: 30px;
        }}
    </style>
</head>
<body>
<div class="tm">
    <h1><center>PSU Schedule</center></h1>
    <img src="T.jpg" alt="Logo" width="50" height="80" class="center">
    <div class="im">
        <div id="time"></div>
        <div id="day"></div>
        <div id="date"></div>
    </div>
</div>
{table}
<script>
    function updateTime() {{
        const timeLabel = document.getElementById('time');
        const dayLabel = document.getElementById('day');
        const dateLabel = document.getElementById('date');
        
        const now = new Date();

        const timeString = now.toLocaleTimeString([], {{ hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true }});
        const dayString = now.toLocaleDateString('en-US', {{ weekday: 'long' }});
        const dateString = now.toLocaleDateString('en-US', {{ year: 'numeric', month: 'long', day: 'numeric' }});

        timeLabel.textContent = timeString;
        dayLabel.textContent = dayString;
        dateLabel.textContent = dateString;
    }}

    updateTime(); // Call the function to set initial values.

    // Update the time every second
    setInterval(updateTime, 1000);
</script>
</body>
</html>""")

def check_schedule_conflict(room_schedule, start_time, end_time):
    for scheduled_time in room_schedule["Schedule_Time"]:
        scheduled_start, scheduled_end = scheduled_time.split(" to ")

        existing_start_time = datetime.datetime.strptime(scheduled_start, "%I:%M %p").strftime("%H:%M:%S")
        existing_end_time = datetime.datetime.strptime(scheduled_end, "%I:%M %p").strftime("%H:%M:%S")

        if (start_time <= existing_end_time and end_time >= existing_start_time) or \
           (start_time >= existing_start_time and end_time <= existing_end_time):
            return True

    return False

def add_schedule():
    print("Scan your RFID card!")
    uid_data = ser.readline().decode().strip()
    if uid_data == "Bryan Etoquilla":
        uid_data = "Bryan Etoquilla"
        print("Recognized")

        while True:
            while True:  # Loop to enter room name
                room_name = input("Enter room (or type 'exit' to quit): ")
                if room_name == "exit":
                    return  # Exit the function
                if room_name in shd:
                    break  # Room name is valid, exit the room name loop
                else:
                    print("Room not found in the schedule. Please enter a valid room name.")

            while True: 
                # Loop to add multiple schedules for the same room
                user_input = input("Enter your Time schedule (e.g., 1:00 PM to 5:00 PM): ")

                try:
                    user_start, user_end = user_input.split(" to ")
                    start_time = datetime.datetime.strptime(user_start, "%I:%M %p").strftime("%H:%M:%S")
                    end_time = datetime.datetime.strptime(user_end, "%I:%M %p").strftime("%H:%M:%S")

                    current_time = datetime.datetime.now().strftime("%H:%M:%S")

                    if end_time < start_time:
                        start_time, end_time = end_time, start_time

                    if start_time < current_time:
                        print("Error: The schedule you entered is in the past relative to the current time.")
                        continue  # Continue the loop to enter another schedule

                except ValueError:
                    print("Invalid input format. Please use the format '1:00 PM to 5:00 PM.'")
                    continue  # Continue the loop to enter another schedule

                room_schedule = shd[room_name]

                if check_schedule_conflict(room_schedule, start_time, end_time):
                    print(f"Conflict: The room {room_name} is already scheduled during that time.")
                    continue  # Continue the loop to enter another schedule

                new_schedule_item = {"ProfName": uid_data, "Schedule_Time": f"{user_start} to {user_end}"}
                room_schedule["Schedule_Time"].append(new_schedule_item["Schedule_Time"])
                room_schedule["ProfName"].append(new_schedule_item["ProfName"])

                sorted_indices = sorted(range(len(room_schedule["Schedule_Time"])), key=lambda i: datetime.datetime.strptime(room_schedule["Schedule_Time"][i].split(" to ")[0], "%I:%M %p"))
                room_schedule["Schedule_Time"] = [room_schedule["Schedule_Time"][i] for i in sorted_indices]
                room_schedule["ProfName"] = [room_schedule["ProfName"][i] for i in sorted_indices]

                shd[room_name] = room_schedule
                print(f"Schedule added for {room_name} with {uid_data} from {user_start} to {user_end}.")

                print_schedule_table(datetime.datetime.now())
                while True:
                    another_schedule = input("Do you want to add another schedule? (y/n): ").lower()

                    if another_schedule == "y":
                        room_name = input("Enter room (or type 'exit' to quit): ")
                        if room_name in shd:
                            break 
                        elif room_name == "exit":
                            return  # Exit the function
                        # Room name is valid, exit the room name loop
                        else:
                            print("Room not found in the schedule. Please enter a valid room name.")
                    elif another_schedule == "n":
                        return
                    else:
                        print("Invalid output!!!")
                    
                    

while True:
    update_schedule()
    add_schedule()
    
