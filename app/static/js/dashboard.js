// static/js/dashboard.js
document.addEventListener('DOMContentLoaded', async () => {
    const statusEl = document.getElementById('connection-status');
    let socket;

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
            query: { token }
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

    // Fetch JWT and then connect
    try {
        const response = await fetch('/token');
        if (!response.ok) {
            throw new Error(`Failed to fetch token: ${response.statusText}`);
        }
        const data = await response.json();
        connectSocket(data.access_token);
    } catch (error) {
        console.error('Could not authenticate and connect to WebSocket.', error);
        updateStatus(false, 'Auth failed');
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