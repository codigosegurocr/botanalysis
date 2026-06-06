#Modelo MLP Pruebas
import json
import numpy as np
import pandas as pd
import joblib

# 🔹 Cargar modelo y escalador previamente entrenados
model = joblib.load("MLP_model.pkl")
scaler = joblib.load("MLP_scaler.pkl")

# 🔹 Cargar datos sin etiquetas
with open("Model_1_Test_Data_Bot.json", "r", encoding="utf-8") as f:
    data = json.load(f)

features_list = []
original_entries = []

for entry in data:
    events = entry["Events"]
    if not events:
        continue

    timestamps = [e['Timestamp'] for e in events]
    speeds = [e['Speed'] for e in events]
    accelerations = [e['Acceleration'] for e in events]
    velocities = [e['Velocity'] for e in events]
    corrections = [1 if e['Correction'] else 0 for e in events]
    acceleration_detected = [1 if e['AccelerationDetected'] else 0 for e in events]
    deceleration_detected = [1 if e['DecelerationDetected'] else 0 for e in events]
    idle_times = [e['IdleTime'] for e in events]
    x_coords = [e['X'] for e in events]
    y_coords = [e['Y'] for e in events]

    total_distance = 0
    for i in range(1, len(x_coords)):
        total_distance += np.sqrt((x_coords[i] - x_coords[i-1])**2 + (y_coords[i] - y_coords[i-1])**2)

    feature_set = {
        'num_events': len(events),
        'avg_speed': np.mean(speeds) if speeds else 0,
        'max_speed': np.max(speeds) if speeds else 0,
        'min_speed': np.min(speeds) if speeds else 0,
        'std_speed': np.std(speeds) if speeds else 0,
        'avg_acceleration': np.mean(accelerations) if accelerations else 0,
        'max_acceleration': np.max(accelerations) if accelerations else 0,
        'min_acceleration': np.min(accelerations) if accelerations else 0,
        'std_acceleration': np.std(accelerations) if accelerations else 0,
        'avg_idle_time': np.mean(idle_times) if idle_times else 0,
        'max_idle_time': np.max(idle_times) if idle_times else 0,
        'min_idle_time': np.min(idle_times) if idle_times else 0,
        'std_idle_time': np.std(idle_times) if idle_times else 0,
        'prop_correction': np.mean(corrections) if corrections else 0,
        'prop_accel_detected': np.mean(acceleration_detected) if acceleration_detected else 0,
        'prop_decel_detected': np.mean(deceleration_detected) if deceleration_detected else 0,
        'total_duration': (timestamps[-1] - timestamps[0]) / 1000 if len(timestamps) > 1 else 0,
        'total_distance': total_distance
    }

    features_list.append(feature_set)
    original_entries.append(entry)

# 🔹 Preparar los datos para el modelo
df = pd.DataFrame(features_list)
X_scaled = scaler.transform(df)

# 🔹 Realizar predicciones
predictions = model.predict(X_scaled)

# 🔹 Mostrar resultados
for i, pred in enumerate(predictions):
    tipo = "Bot" if pred == 0 else "Humano"
    print(f"Entrada {i+1}: {tipo}")

# 🔹 Guardar resultados en archivo
output = []
for i, pred in enumerate(predictions):
    output.append({
        "Prediccion": int(pred),
        "Tipo": "Bot" if pred == 0 else "Human"
    })

with open("MLP_predicciones.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print("\n✅ Predicciones guardadas en 'MLP_predicciones.json'")
