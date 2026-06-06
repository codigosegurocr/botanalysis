# ==========================================
# Random Forest
# ==========================================

import json
import numpy as np
import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import (
    train_test_split,
    RandomizedSearchCV,
    cross_val_score
)
from sklearn.utils import shuffle
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score
)

# ==========================================
# Cargar dataset
# ==========================================

with open("Dataset1_Train.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for record in data:
    record["Label"] = int(record.get("Label", 1))

# ==========================================
# Extracción de características
# (MISMAS DEL MLP)
# ==========================================

def extract_features(entry):

    events = entry["Events"]

    if not events:
        return None

    timestamps = [e["Timestamp"] for e in events]
    speeds = [e["Speed"] for e in events]
    accelerations = [e["Acceleration"] for e in events]

    corrections = [
        1 if e["Correction"] else 0
        for e in events
    ]

    acceleration_detected = [
        1 if e["AccelerationDetected"] else 0
        for e in events
    ]

    deceleration_detected = [
        1 if e["DecelerationDetected"] else 0
        for e in events
    ]

    idle_times = [
        e["IdleTime"]
        for e in events
    ]

    x_coords = [
        e["X"]
        for e in events
    ]

    y_coords = [
        e["Y"]
        for e in events
    ]

    total_distance = 0

    for i in range(1, len(x_coords)):
        total_distance += np.sqrt(
            (x_coords[i] - x_coords[i - 1]) ** 2 +
            (y_coords[i] - y_coords[i - 1]) ** 2
        )

    return {

        "num_events": len(events),

        "avg_speed": np.mean(speeds),
        "max_speed": np.max(speeds),
        "min_speed": np.min(speeds),
        "std_speed": np.std(speeds),

        "avg_acceleration": np.mean(accelerations),
        "max_acceleration": np.max(accelerations),
        "min_acceleration": np.min(accelerations),
        "std_acceleration": np.std(accelerations),

        "avg_idle_time": np.mean(idle_times),
        "max_idle_time": np.max(idle_times),
        "min_idle_time": np.min(idle_times),
        "std_idle_time": np.std(idle_times),

        "prop_correction": np.mean(corrections),

        "prop_accel_detected":
            np.mean(acceleration_detected),

        "prop_decel_detected":
            np.mean(deceleration_detected),

        "total_duration":
            (timestamps[-1] - timestamps[0]) / 1000
            if len(timestamps) > 1 else 0,

        "total_distance": total_distance,

        "Label": entry["Label"]
    }

# ==========================================
# Construcción del DataFrame
# ==========================================

rows = []

for entry in data:

    row = extract_features(entry)

    if row is not None:
        rows.append(row)

df = pd.DataFrame(rows)

df = shuffle(df, random_state=42)

X = df.drop(columns=["Label"])
y = df["Label"]

print("\nDistribución de etiquetas:")
print(y.value_counts().sort_index())

# ==========================================
# Optimización Random Forest
# ==========================================

param_dist = {
    "n_estimators": [100, 150, 200, 250, 300],
    "max_depth": [10, 15, 20, 25, None],
    "min_samples_split": [2, 5, 10],
    "min_samples_leaf": [1, 2, 4]
}

base_model = RandomForestClassifier(
    random_state=42,
    class_weight="balanced"
)

random_search = RandomizedSearchCV(
    estimator=base_model,
    param_distributions=param_dist,
    n_iter=20,
    cv=5,
    scoring="accuracy",
    n_jobs=-1,
    random_state=42
)

print("\nBuscando mejores hiperparámetros...")

random_search.fit(X, y)

best_model = random_search.best_estimator_

print("\nMejores hiperparámetros:")
print(random_search.best_params_)

# ==========================================
# Validación cruzada
# ==========================================

cv_scores = cross_val_score(
    best_model,
    X,
    y,
    cv=5,
    scoring="accuracy"
)

print("\n=== VALIDACIÓN CRUZADA ===")
print("Accuracy por fold:")
print(cv_scores)

print(
    f"\nAccuracy promedio: "
    f"{np.mean(cv_scores):.4f}"
)

print(
    f"Desviación estándar: "
    f"{np.std(cv_scores):.4f}"
)

# ==========================================
# Entrenamiento final
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

best_model.fit(X_train, y_train)

y_pred = best_model.predict(X_test)

# ==========================================
# Evaluación
# ==========================================

print("\n=== EVALUACIÓN FINAL ===")

print(
    f"Accuracy: "
    f"{accuracy_score(y_test, y_pred):.4f}"
)

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        y_pred,
        target_names=["Bot", "Human"]
    )
)

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# ==========================================
# Importancia de variables
# ==========================================

importance_df = pd.DataFrame({
    "Feature": X.columns,
    "Importance": best_model.feature_importances_
})

importance_df = importance_df.sort_values(
    by="Importance",
    ascending=False
)

print("\n=== IMPORTANCIA DE VARIABLES ===")
print(importance_df.to_string(index=False))

# ==========================================
# Guardar modelo
# ==========================================

joblib.dump(
    best_model,
    "random_forest_model_mlp_features.pkl"
)

print(
    "\nModelo guardado como:"
    " random_forest_model_mlp_features.pkl"
)
