function updateTime() {
    const timeLabel = document.getElementById('time');
    const dayLabel = document.getElementById('day');
    const dateLabel = document.getElementById('date');
    
    const now = new Date();

    const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true });
    const dayString = now.toLocaleDateString('en-US', { weekday: 'long' });
    const dateString = now.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });

    timeLabel.textContent = timeString;
    dayLabel.textContent = dayString;
    dateLabel.textContent = dateString;
}

updateTime(); // Call the function to set initial values.

// Update the time every second
setInterval(updateTime, 1000);


document.addEventListener('DOMContentLoaded', function() {
    var statusCells = document.getElementsByClassName('status');

    for (var i = 0; i < statusCells.length; i++) {
        var statusCell = statusCells[i];

        if (statusCell.classList.contains('scheduled')) {
            statusCell.style.color = 'red';
        } else if (statusCell.classList.contains('available')) {
            statusCell.style.color = 'green';
        }
    }
});

