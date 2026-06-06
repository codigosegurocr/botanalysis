let mouseDataRequest = {
    userId: "user123",
    events: []
};

let lastMousePosition = { x: 0, y: 0 };
let lastSpeed = 0;
let lastDirection = 0;
let lastTime = null; // ⬅️ Cambiado para inicializar vacío
let startTime = Date.now();
const maxEvents = 150;
const keepRatio = 0.5;

document.addEventListener('mousemove', function (event) {
    const now = Date.now();
    const idleTime = lastTime !== null ? ((now - lastTime) / 1000) : 0;

    const deltaX = event.clientX - lastMousePosition.x;
    const deltaY = event.clientY - lastMousePosition.y;
    const distance = Math.sqrt(deltaX ** 2 + deltaY ** 2);
    const timeElapsed = lastTime !== null ? ((now - lastTime) / 1000 || 0.001) : 0.001;
    const speed = distance / timeElapsed;
    const acceleration = (speed - lastSpeed) / timeElapsed;
    const direction = Math.atan2(deltaY, deltaX);

    const curvatureDetected = Math.abs(direction - lastDirection) > Math.PI / 4;
    const accelerationDetected = acceleration > 2;
    const decelerationDetected = acceleration < -2 && speed < 0.5;

    if ((deltaX !== 0 || deltaY !== 0) && mouseDataRequest.events.length < maxEvents) {
        const mouseEvent = {
            timestamp: now,
            x: event.clientX,
            y: event.clientY,
            deltaX: deltaX,
            deltaY: deltaY,
            distance: distance,
            direction: direction,
            timeElapsed: timeElapsed,
            speed: speed,
            acceleration: acceleration,
            curvatureDetected: curvatureDetected,
            accelerationDetected: accelerationDetected,
            decelerationDetected: decelerationDetected,
            idleTime: idleTime
        };

        if (Math.random() <= keepRatio) {
            mouseDataRequest.events.push(mouseEvent);
        }

        lastMousePosition = { x: event.clientX, y: event.clientY };
        lastSpeed = speed;
        lastDirection = direction;
    }

    lastTime = now; // ⬅️ Se actualiza al final del evento
});

document.addEventListener('click', function (event) {
    const now = Date.now();
    const idleTime = lastTime !== null ? ((now - lastTime) / 1000) : 0;

    mouseDataRequest.events.push({
        timestamp: now,
        x: event.clientX,
        y: event.clientY,
        deltaX: 0,
        deltaY: 0,
        distance: 0,
        direction: 0,
        timeElapsed: 0,
        speed: 0,
        acceleration: 0,
        curvatureDetected: false,
        accelerationDetected: false,
        decelerationDetected: false,
        idleTime: idleTime
    });

    lastTime = now;
});

document.getElementById('submit-button').addEventListener('click', () => {
    if (mouseDataRequest.events.length > 0) {
        const inicio = mouseDataRequest.events[0];
        const fin = mouseDataRequest.events[mouseDataRequest.events.length - 1];

        mouseDataRequest.x_start = inicio.x;
        mouseDataRequest.y_start = inicio.y;
        mouseDataRequest.x_end = fin.x;
        mouseDataRequest.y_end = fin.y;
    }
    mouseDataRequest.label = 1;
    mouseDataRequest.tiempo_total = (Date.now() - startTime) / 1000;

    document.getElementById('username').value = '';
    document.getElementById('password').value = '';

    fetch('/Account/CaptureMouseDataRF', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(mouseDataRequest)
    })
        .then(response => response.json())
        .then(data => console.log('✅ Datos enviados correctamente:', data))
        .catch(error => console.error('❌ Error al enviar:', error));
});
