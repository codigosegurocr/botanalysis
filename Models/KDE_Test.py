# ==========================================================
# KDE TEST
# ==========================================================

import json
import numpy as np
import pandas as pd
import joblib

from sklearn.neighbors import KernelDensity

# ==========================================================
# CARGAR MODELOS
# ==========================================================

kde_human = joblib.load("KDE_human.pkl")
kde_bot = joblib.load("KDE_bot.pkl")
scaler = joblib.load("KDE_scaler.pkl")
feature_names = joblib.load("KDE_features.pkl")

print("Modelos cargados correctamente")

# ==========================================================
# CARGAR DATASET DE PRUEBA
# ==========================================================

with open(
    "Dataset1_Test.json",
    "r",
    encoding="utf-8"
) as f:
    data = json.load(f)

# ==========================================================
# FEATURE ENGINEERING
# (idéntico al entrenamiento)
# ==========================================================

features_list = []

for user_session in data:

    events = user_session["Events"]

    if not events:
        continue

    speeds = [
        event["Speed"]
        for event in events
        if event["Type"] == "mousemove"
    ]

    accelerations = [
        event["Acceleration"]
        for event in events
        if event["Type"] == "mousemove"
    ]

    idle_times = [
        event["IdleTime"]
        for event in events
    ]

    corrections = [
        1
        for event in events
        if event["Correction"] == True
    ]

    acceleration_detected = [
        1
        for event in events
        if event["Type"] == "mousemove"
        and event["AccelerationDetected"] == True
    ]

    deceleration_detected = [
        1
        for event in events
        if event["Type"] == "mousemove"
        and event["DecelerationDetected"] == True
    ]

    x_coords = [
        event["X"]
        for event in events
        if event["Type"] == "mousemove"
    ]

    y_coords = [
        event["Y"]
        for event in events
        if event["Type"] == "mousemove"
    ]

    delta_xs = [
        x_coords[i] - x_coords[i - 1]
        for i in range(1, len(x_coords))
    ]

    delta_ys = [
        y_coords[i] - y_coords[i - 1]
        for i in range(1, len(y_coords))
    ]

    distances = [
        np.sqrt(dx**2 + dy**2)
        for dx, dy in zip(delta_xs, delta_ys)
    ]

    features = {
        'num_events': len(events),
        'avg_speed': np.mean(speeds) if speeds else 0,
        'std_speed': np.std(speeds) if speeds else 0,
        'max_speed': np.max(speeds) if speeds else 0,
        'avg_acceleration': np.mean(accelerations) if accelerations else 0,
        'std_acceleration': np.std(accelerations) if accelerations else 0,
        'max_acceleration': np.max(accelerations) if accelerations else 0,
        'total_idle_time': sum(idle_times) if idle_times else 0,
        'num_corrections': sum(corrections),
        'accel_detected_ratio':
            sum(acceleration_detected) / len(events)
            if len(events) > 0 else 0,
        'decel_detected_ratio':
            sum(deceleration_detected) / len(events)
            if len(events) > 0 else 0,
        'avg_delta_x':
            np.mean(delta_xs) if delta_xs else 0,
        'avg_delta_y':
            np.mean(delta_ys) if delta_ys else 0,
        'avg_distance_per_event':
            np.mean(distances) if distances else 0,
        'total_distance':
            sum(distances) if distances else 0
    }

    features_list.append(features)

# ==========================================================
# DATAFRAME
# ==========================================================

df = pd.DataFrame(features_list)

# Asegurar mismo orden que entrenamiento
df = df[feature_names]

# ==========================================================
# ESCALAR
# ==========================================================

X_scaled = scaler.transform(df)

# ==========================================================
# PREDICCIONES KDE
# ==========================================================

human_scores = kde_human.score_samples(
    X_scaled
)

bot_scores = kde_bot.score_samples(
    X_scaled
)

predictions = np.where(
    human_scores > bot_scores,
    1,
    0
)

# ==========================================================
# RESULTADOS
# ==========================================================

for i, pred in enumerate(predictions):

    tipo = (
        "Humano"
        if pred == 1
        else "Bot"
    )

    print(
        f"Registro {i+1}: "
        f"{tipo}"
    )

# ==========================================================
# GUARDAR RESULTADOS
# ==========================================================

output = []

for pred in predictions:

    output.append({
        "Prediccion": int(pred),
        "Tipo":
            "Humano"
            if pred == 1
            else "Bot"
    })

with open(
    "KDE_predicciones.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        output,
        f,
        indent=2,
        ensure_ascii=False
    )

print(
    "\nPredicciones guardadas en KDE_predicciones.json"
)
