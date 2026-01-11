// static/js/dashboard.js
document.addEventListener('DOMContentLoaded', async () => {
    const statusEl = document.getElementById('connection-status');
    let socket;
    const dashboardGrid = document.querySelector('.dashboard-grid');

    const updateStatus = (isConnected, message = '') => {
        if (isConnected) {
            statusEl.textContent = 'CONNECTED';
            statusEl.className = 'status-connected';
            console.log('Socket.IO Connected!');
        } else {
            statusEl.textContent = 'DISCONNECTED';
            statusEl.className = 'status-disconnected';
            console.error('Socket.IO Disconnected.', message);
        }
    };

    const connectSocket = (token) => {
        // Connect to the socket with the token
        socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port, {
            extraHeaders: {
                "Authorization": `Bearer ${token}`
            }
        });

        socket.on('connect', () => {
            updateStatus(true);
        });

        socket.on('disconnect', () => {
            updateStatus(false);
        });

        socket.on('connect_error', (err) => {
            updateStatus(false, err.message);
        });

        // Listen for feedback from the server
        socket.on('response', (data) => {
            console.log('Server response:', data);
        });

        // Listen for telemetry data
        socket.on('telemetry', (data) => {
            document.getElementById('cpu-temp').textContent = data.cpu_temp.toFixed(1);
            document.getElementById('battery').textContent = data.battery.toFixed(0);
        });
    };

    // Read token from the data attribute on the page
    const token = dashboardGrid.dataset.token;
    if (token) {
        connectSocket(token);
    } else {
        console.error('Authentication token not found on page.');
        updateStatus(false, 'Auth token missing');
    }

    // Make sendCommand globally accessible
    window.sendCommand = (action, value = 0) => {
        if (socket && socket.connected) {
            socket.emit('command', { action, value });
        } else {
            console.error('Cannot send command. Socket is not connected.');
        }
    };
});