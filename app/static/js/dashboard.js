// Fetch stats every 2 seconds
function updateStats() {
    fetch('/api/telemetry')
        .then(response => response.json())
        .then(data => {
            document.getElementById('cpu-temp').innerText = data.cpu_temp;
            document.getElementById('battery').innerText = data.battery;
        })
        .catch(err => console.error('Error fetching telemetry:', err));
}

function sendCommand(cmd) {
    console.log("Sending command:", cmd);
    // Future: fetch('/api/command', {method: 'POST', body: JSON.stringify({command: cmd})})
}

// Connect using the Socket.io library
// Note: We pass the token in the 'auth' or query params
const socket = io({
    query: {
        token: localStorage.getItem('access_token') // Assumes you stored your JWT here
    }
});

socket.on('connect', () => {
    console.log("Connected to Rover via Socket.io!");
});

socket.on('response', (data) => {
    console.log("Server says:", data);
});

function sendCommand(actionName, val = 0) {
    // We 'emit' a 'command' event as defined in our Python code
    socket.emit('command', { action: actionName, value: val });
}

setInterval(updateStats, 2000);
updateStats(); // Run once on load