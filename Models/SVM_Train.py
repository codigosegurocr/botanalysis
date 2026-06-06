# Model SVM

import json
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)
from sklearn.inspection import permutation_importance

# ==========================================================
# LOAD DATASET
# ==========================================================

try:
    with open('Dataset1_Train.json', 'r') as f:
        data = json.load(f)

    print("Dataset1_Train.json cargado correctamente")

except FileNotFoundError:
    print("Error: archivo no encontrado")
    exit()

# ==========================================================
# FEATURE ENGINEERING
# ==========================================================

features_list = []
labels = []

for entry in data:

    events = entry['Events']

    if not events:
        continue

    label = int(entry['Label'])

    timestamps = [e['Timestamp'] for e in events]

    speeds = [e['Speed'] for e in events]

    accelerations = [
        e['Acceleration']
        for e in events
    ]

    corrections = [
        1 if e['Correction'] else 0
        for e in events
    ]

    acceleration_detected = [
        1 if e['AccelerationDetected'] else 0
        for e in events
    ]

    deceleration_detected = [
        1 if e['DecelerationDetected'] else 0
        for e in events
    ]

    idle_times = [
        e['IdleTime']
        for e in events
    ]

    x_coords = [e['X'] for e in events]
    y_coords = [e['Y'] for e in events]

    total_distance = 0

    for i in range(1, len(x_coords)):

        total_distance += np.sqrt(
            (x_coords[i] - x_coords[i - 1]) ** 2 +
            (y_coords[i] - y_coords[i - 1]) ** 2
        )

    feature_set = {

        'num_events': len(events),

        'avg_speed':
            np.mean(speeds) if speeds else 0,

        'max_speed':
            np.max(speeds) if speeds else 0,

        'min_speed':
            np.min(speeds) if speeds else 0,

        'std_speed':
            np.std(speeds) if speeds else 0,

        'avg_acceleration':
            np.mean(accelerations)
            if accelerations else 0,

        'max_acceleration':
            np.max(accelerations)
            if accelerations else 0,

        'min_acceleration':
            np.min(accelerations)
            if accelerations else 0,

        'std_acceleration':
            np.std(accelerations)
            if accelerations else 0,

        'avg_idle_time':
            np.mean(idle_times)
            if idle_times else 0,

        'max_idle_time':
            np.max(idle_times)
            if idle_times else 0,

        'min_idle_time':
            np.min(idle_times)
            if idle_times else 0,

        'std_idle_time':
            np.std(idle_times)
            if idle_times else 0,

        'prop_correction':
            np.mean(corrections)
            if corrections else 0,

        'prop_accel_detected':
            np.mean(acceleration_detected)
            if acceleration_detected else 0,

        'prop_decel_detected':
            np.mean(deceleration_detected)
            if deceleration_detected else 0,

        'total_duration':
            (
                timestamps[-1] - timestamps[0]
            ) / 1000
            if len(timestamps) > 1
            else 0,

        'total_distance':
            total_distance
    }

    features_list.append(feature_set)
    labels.append(label)

# ==========================================================
# DATAFRAME
# ==========================================================

df = pd.DataFrame(features_list)

X = df
y = np.array(labels)

# ==========================================================
# TRAIN TEST SPLIT
# ==========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# ==========================================================
# SCALE
# ==========================================================

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ==========================================================
# TRAIN SVM
# ==========================================================

svm = SVC(
    kernel='rbf',
    C=10,
    gamma='scale',
    probability=True,
    random_state=42
)

print("\\nTraining start...")

svm.fit(X_train_scaled, y_train)

print("Training finished")

# ==========================================================
# EVALUATION
# ==========================================================

y_pred = svm.predict(X_test_scaled)

print("\\n--- SVM Model Evaluation Results ---")

print(
    f"Accuracy: "
    f"{accuracy_score(y_test, y_pred):.4f}"
)

print("\\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            'Bot',
            'Human'
        ]
    )
)

print("\\nConfusion Matrix:")

print(
    confusion_matrix(
        y_test,
        y_pred
    )
)

# ==========================================================
# FEATURE IMPORTANCE
# ==========================================================

result = permutation_importance(
    svm,
    X_test_scaled,
    y_test,
    n_repeats=20,
    random_state=42,
    scoring='accuracy'
)

importance_df = pd.DataFrame({
    'Feature': X.columns,
    'Importance': result.importances_mean
})

importance_df = (
    importance_df
    .sort_values(
        by='Importance',
        ascending=False
    )
)

print("\\n=== FEATURE IMPORTANCE ===")

print(
    importance_df.to_string(
        index=False
    )
)

# ==========================================================
# SAVE MODEL
# ==========================================================

joblib.dump(
    svm,
    "SVM_model.pkl"
)

joblib.dump(
    scaler,
    "SVM_scaler.pkl"
)

print("\\nModelo guardado como:")
print("SVM_model.pkl")
print("SVM_scaler.pkl")
