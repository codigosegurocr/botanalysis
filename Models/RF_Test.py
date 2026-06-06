
import json
import numpy as np
import pandas as pd
import joblib

# ========================
# Cargar modelo optimizado
# ========================
# Este modelo espera estrictamente un DataFrame con las 8 variables del entrenamiento
model = joblib.load("random_forest_model_robusto.pkl")

# ========================
# Cargar JSON de prueba (sin etiquetas)
# ========================
with open("mouse_data_bt2.json", "r", encoding="utf-8") as f:
    test_data = json.load(f)

# ========================
# 🔹 Función de extracción 
# ========================
def extract_features(entry):
    events = entry["Events"]
    num_events = len(events)

    if num_events == 0:
        # Control de seguridad por si llega una ráfaga vacía
        return {k: 0 for k in [
            "avg_acceleration", "prop_correction", "avg_speed", "std_acceleration",
            "prop_accel_detected", "total_distance", "avg_delta_y", "std_speed"
        ]}

    # Extracción de las listas crudas desde los micro-eventos
    speeds = [e["Speed"] for e in events]
    accels = [e["Acceleration"] for e in events]
    deltas_y = [e["DeltaY"] for e in events]
    distances = [e["Distance"] for e in events]

    # Diccionario estricto con el Top 8 
    return {
        "avg_acceleration":     np.mean(accels),
        "prop_correction":      sum(e["CurvatureDetected"] for e in events) / num_events,
        "avg_speed":            np.mean(speeds),
        "std_acceleration":     np.std(accels),
        "prop_accel_detected":  sum(e["AccelerationDetected"] for e in events) / num_events,
        "total_distance":       np.sum(distances),
        "avg_delta_y":          np.mean([abs(dy) for dy in deltas_y]),
        "std_speed":            np.std(speeds)
    }

# ========================
# Procesar entradas y estructurar DataFrame
# ========================
X_test = pd.DataFrame([extract_features(entry) for entry in test_data])

# ========================
# Predecir y calcular confianza probabilística
# ========================
predictions = model.predict(X_test)
probs = model.predict_proba(X_test)

print(f"\n Resultados de predicción para {len(X_test)} entradas:")
for i, (pred, prob) in enumerate(zip(predictions, probs)):
    tipo = "Humano" if pred == 1 else "Bot"
    # prob[pred] extrae la probabilidad asignada a la clase ganadora
    confianza = round(prob[pred] * 100, 2)
    print(f"Entrada {i+1}: {tipo} ({confianza}% confianza)")

# ========================
# Guardar resultados en JSON estructurado
# ========================
output = [
    {
        "ID_Entrada": i + 1,
        "Prediccion": int(pred),
        "Tipo": "Humano" if pred == 1 else "Bot",
        "Confianza (%)": round(prob[pred] * 100, 2)
    }
    for i, (pred, prob) in enumerate(zip(predictions, probs))
]

with open("predicciones_robusto.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print("\nResultados guardados con éxito en 'predicciones_robusto.json'")
