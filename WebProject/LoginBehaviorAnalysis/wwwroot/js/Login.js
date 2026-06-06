let mouseDataRequest = {
    userId: "user123",
    events: [],
    label: 0
};

let lastMousePosition = { x: 0, y: 0 };
let lastSpeed = 0;
let lastTime = Date.now();
let idleTime = 0;
let idleTimer = null;
const maxEvents = 100;
const moveThreshold = 5;
let accelerationDetected = false;
let decelerationDetected = false;

// Porcentaje de eventos a guardar (75%)
const keepRatio = 0.2;

// Captura de movimiento del mouse
document.addEventListener('mousemove', function (event) {
    const deltaX = event.clientX - lastMousePosition.x;
    const deltaY = event.clientY - lastMousePosition.y;
    const distance = Math.sqrt(deltaX ** 2 + deltaY ** 2);
    const timeElapsed = (Date.now() - lastTime) / 1000;
    const speed = distance / timeElapsed;
    const acceleration = (speed - lastSpeed) / timeElapsed;
    const velocity = speed;
    const directionChange = Math.atan2(deltaY, deltaX);

    // Aceleración Inicial
    if (!accelerationDetected && acceleration > 2) {
        accelerationDetected = true;
    }

    // Desaceleración Final (antes de un clic)
    if (!decelerationDetected && acceleration < -2 && speed < 0.5) {
        decelerationDetected = true;
    }

    // Corrección de Trayectoria (pequeños ajustes al final)
    let correction = false;
    if (Math.abs(directionChange) < 0.1 && distance < 10) {
        correction = true;
    }

    // Solo capturar eventos si el movimiento es significativo
    if ((deltaX !== 0 || deltaY !== 0) && mouseDataRequest.events.length < maxEvents) {
        let mouseEvent = {
            timestamp: Date.now(),
            type: 'mousemove',
            x: event.clientX,
            y: event.clientY,
            speed: speed,
            acceleration: acceleration,
            velocity: velocity,
            correction: correction,
            accelerationDetected: accelerationDetected,
            decelerationDetected: decelerationDetected,
            idleTime: getIdleTime() // Obtener el tiempo de inactividad
        };

        // **Reducir eventos al 75%**
        if (Math.random() <= keepRatio) {
            mouseDataRequest.events.push(mouseEvent);
        }

        lastMousePosition = { x: event.clientX, y: event.clientY };
        lastSpeed = speed;
    }

    // **Actualizar lastTime en cada movimiento**
    lastTime = Date.now();
    resetIdleTimer();
});

// Captura de clics (incluye desaceleración final)
document.addEventListener('click', function (event) {
    if (mouseDataRequest.events.length < maxEvents) {
        let mouseEvent = {
            timestamp: Date.now(),
            type: 'click',
            x: event.clientX,
            y: event.clientY,
            button: getButtonName(event.button),
            accelerationDetected: accelerationDetected,
            decelerationDetected: decelerationDetected,
            idleTime: getIdleTime() // Obtener el tiempo de inactividad
        };

        // **Guardar siempre los clics**
        mouseDataRequest.events.push(mouseEvent);

        // Reiniciar detecciones
        accelerationDetected = false;
        decelerationDetected = false;
    }

    // **Actualizar lastTime al hacer clic**
    lastTime = Date.now();
    resetIdleTimer();
});

// Función para obtener el nombre del botón del mouse
function getButtonName(buttonCode) {
    switch (buttonCode) {
        case 0: return 'left';
        case 1: return 'middle';
        case 2: return 'right';
        default: return '';
    }
}

// Función para obtener el tiempo de inactividad
function getIdleTime() {
    idleTime = Math.floor((Date.now() - lastTime) / 1000);
    return idleTime;
}

// Reiniciar el temporizador de inactividad
function resetIdleTimer() {
    if (idleTimer) clearTimeout(idleTimer);

    idleTimer = setTimeout(() => {
        lastTime = Date.now();
    }, 5000);
}

// Enviar datos al hacer clic en el botón de submit
document.getElementById('submit-button').addEventListener('click', () => {
    if (mouseDataRequest.events.length > maxEvents) {
        mouseDataRequest.events = mouseDataRequest.events.slice(0, maxEvents);
    }
    document.getElementById('username').value = '';
    document.getElementById('password').value = '';

    fetch('/Account/CaptureMouseData', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(mouseDataRequest)
    })
        .then(response => response.json())
        .then(data => {
            console.log('Data sent successfully:', data);
        })
        .catch(error => {
            console.error('Error sending data:', error);
        });
});
