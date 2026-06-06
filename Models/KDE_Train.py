# KDE Model Training
import json
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KernelDensity
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# ==========================================================
# LOAD DATASET
# ==========================================================

try:
    with open('Dataset1_Train.json', 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    print("Error")
    exit()

# ==========================================================
# FEATURE ENGINEERING
# ==========================================================

features_list = []
labels = []

for entry in data:

    events = entry['Events']
    label = int(entry['Label'])

    if not events:
        continue

    timestamps = [e['Timestamp'] for e in events]
    speeds = [e['Speed'] for e in events]
    accelerations = [e['Acceleration'] for e in events]

    corrections = [1 if e['Correction'] else 0 for e in events]

    acceleration_detected = [
        1 if e['AccelerationDetected'] else 0
        for e in events
    ]

    deceleration_detected = [
        1 if e['DecelerationDetected'] else 0
        for e in events
    ]

    idle_times = [e['IdleTime'] for e in events]

    x_coords = [e['X'] for e in events]
    y_coords = [e['Y'] for e in events]

    total_distance = 0

    for i in range(1, len(x_coords)):
        total_distance += np.sqrt(
            (x_coords[i] - x_coords[i-1])**2 +
            (y_coords[i] - y_coords[i-1])**2
        )

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
    labels.append(label)

# ==========================================================
# DATAFRAME
# ==========================================================

df = pd.DataFrame(features_list)

X = df
y = np.array(labels)

print(pd.Series(y).value_counts().sort_index())

# ==========================================================
# SPLIT + SCALING
# ==========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ==========================================================
# KDE TRAINING
# ==========================================================

X_train_human = X_train_scaled[y_train == 1]
X_train_bot = X_train_scaled[y_train == 0]

param_grid = {
    'bandwidth': np.logspace(-1, 1, 20)
}

grid = GridSearchCV(
    KernelDensity(kernel='gaussian'),
    param_grid,
    cv=5
)

grid.fit(X_train_human)

best_bandwidth = grid.best_params_['bandwidth']

kde_human = KernelDensity(
    kernel='gaussian',
    bandwidth=best_bandwidth
)

kde_bot = KernelDensity(
    kernel='gaussian',
    bandwidth=best_bandwidth
)

kde_human.fit(X_train_human)
kde_bot.fit(X_train_bot)

# ==========================================================
# PREDICTION
# ==========================================================

human_scores = kde_human.score_samples(X_test_scaled)
bot_scores = kde_bot.score_samples(X_test_scaled)

y_pred = np.where(human_scores > bot_scores, 1, 0)

# ==========================================================
# EVALUATION
# ==========================================================

print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(classification_report(
    y_test,
    y_pred,
    target_names=['Bot', 'Human']
))
print(confusion_matrix(y_test, y_pred))

# ==========================================================
# FEATURE IMPORTANCE
# ==========================================================

baseline_accuracy = accuracy_score(y_test, y_pred)

feature_importance = []

for i, feature in enumerate(X.columns):

    X_perm = X_test_scaled.copy()
    np.random.shuffle(X_perm[:, i])

    human_perm = kde_human.score_samples(X_perm)
    bot_perm = kde_bot.score_samples(X_perm)

    y_perm = np.where(
        human_perm > bot_perm,
        1,
        0
    )

    perm_accuracy = accuracy_score(
        y_test,
        y_perm
    )

    feature_importance.append({
        'Feature': feature,
        'Importance': baseline_accuracy - perm_accuracy
    })

importance_df = pd.DataFrame(feature_importance)
importance_df = importance_df.sort_values(
    by='Importance',
    ascending=False
)

print("\\n=== IMPORTANCE ===")
print(importance_df)

# ==========================================================
# SAVE
# ==========================================================

joblib.dump(kde_human, "KDE_human.pkl")
joblib.dump(kde_bot, "KDE_bot.pkl")
joblib.dump(scaler, "KDE_scaler.pkl")

print("KDE models saved")
