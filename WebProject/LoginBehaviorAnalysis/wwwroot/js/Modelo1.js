let mouseDataRequest = {
    username: '',
    events: []
};

let lastX = -1;
let lastY = -1;
let lastTimestamp = Date.now();
let lastSpeed = 0;

document.addEventListener("DOMContentLoaded", function () {
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");
    const submitButton = document.getElementById("submit-button");

    if (!usernameInput || !passwordInput || !submitButton) return;

    document.addEventListener("mousemove", function (e) {
        const now = Date.now();
        const timeElapsed = now - lastTimestamp;

        const dx = e.clientX - lastX;
        const dy = e.clientY - lastY;
        const distance = Math.sqrt(dx * dx + dy * dy);
        const speed = timeElapsed > 0 ? distance / timeElapsed : 0;
        const acceleration = timeElapsed > 0 ? (speed - lastSpeed) / timeElapsed : 0;

        const curvature = (dx !== 0 && dy !== 0);
        const correction = (Math.sign(dx) !== Math.sign(lastX) || Math.sign(dy) !== Math.sign(lastY));

        const idleTime = now - lastTimestamp;

        mouseDataRequest.events.push({
            Type: "mousemove",
            X: e.clientX,
            Y: e.clientY,
            Timestamp: now,
            Speed: speed,
            Acceleration: acceleration,
            Velocity: distance,
            CurvatureDetected: curvature,
            Correction: correction,
            AccelerationDetected: acceleration > 0.1,
            DecelerationDetected: acceleration < -0.1,
            IdleTime: idleTime
        });

        lastX = e.clientX;
        lastY = e.clientY;
        lastTimestamp = now;
        lastSpeed = speed;
    });

    document.addEventListener("click", function (e) {
        mouseDataRequest.events.push({
            Type: "click",
            X: e.clientX,
            Y: e.clientY,
            Timestamp: Date.now()
        });
    });

    submitButton.addEventListener("click", function () {
        mouseDataRequest.username = usernameInput.value;

        // ✅ No enviar si no hay eventos
        if (mouseDataRequest.events.length === 0) {
            console.warn("❌ No se enviaron datos: no hay eventos.");
            return;
        }

        const maxEvents = 300;
        if (mouseDataRequest.events.length > maxEvents) {
            mouseDataRequest.events = mouseDataRequest.events.slice(0, maxEvents);
        }

        console.log("✅ Enviando", mouseDataRequest.events.length, "eventos...");

        fetch("/Account/CaptureMouseDataMod1", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(mouseDataRequest)
        }).then(response => {
            if (response.ok) {
                console.log("✅ Datos enviados correctamente.");
            } else {
                console.error("❌ Error al enviar datos.");
            }
        }).catch(error => {
            console.error("❌ Error en el fetch:", error);
        });
    });
});
