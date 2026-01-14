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

    // --- Control Logic ---

    // --- Keyboard State & Mapping ---
    let pressedKeys = []; // Tracks currently pressed movement keys
    const keyActionMap = {
        'ArrowUp': 'forward',
        'ArrowDown': 'backward',
        'ArrowLeft': 'left',
        'ArrowRight': 'right'
    };

    // --- Mouse & Touch Controls ---
    const controlButtons = {
        'btn-forward': 'forward',
        'btn-backward': 'backward',
        'btn-left': 'left',
        'btn-right': 'right',
    };

    // This helper prevents mouse/touch release from stopping the rover
    // if a keyboard key is still held down.
    const stopMovementOnRelease = () => {
        if (pressedKeys.length === 0) {
            sendCommand('stop');
        }
    };

    for (const [buttonId, action] of Object.entries(controlButtons)) {
        const button = document.getElementById(buttonId);
        if (button) {
            // Mouse events
            button.addEventListener('mousedown', () => sendCommand(action));
            button.addEventListener('mouseup', stopMovementOnRelease);
            button.addEventListener('mouseleave', stopMovementOnRelease);

            // Touch events for mobile
            button.addEventListener('touchstart', (e) => {
                e.preventDefault(); // Prevents firing mouse events as well
                sendCommand(action);
            });
            button.addEventListener('touchend', stopMovementOnRelease);
        }
    }

    // The dedicated stop button should always stop the rover and clear key state.
    const stopButton = document.getElementById('btn-stop');
    if (stopButton) {
        stopButton.addEventListener('click', () => {
            pressedKeys = [];
            sendCommand('stop');
        });
    }

    // --- Keyboard Event Listeners ---
    document.addEventListener('keydown', (event) => {
        const action = keyActionMap[event.key];
        // Check if it's a mapped control key and not already pressed
        if (action && !pressedKeys.includes(event.key)) {
            event.preventDefault(); // Prevent browser scrolling
            pressedKeys.unshift(event.key); // Add to the front as the most recent
            sendCommand(action);
        }
    });

    document.addEventListener('keyup', (event) => {
        const action = keyActionMap[event.key];
        if (action) {
            event.preventDefault();
            // Remove the released key from the array
            pressedKeys = pressedKeys.filter(key => key !== event.key);

            if (pressedKeys.length === 0) {
                // If no more keys are down, stop the rover
                sendCommand('stop');
            } else {
                // Otherwise, revert to the action of the last-pressed key
                const lastAction = keyActionMap[pressedKeys[0]];
                sendCommand(lastAction);
            }
        }
    });
});