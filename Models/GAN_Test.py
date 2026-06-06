import json
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import joblib

# ==========================================
# FEATURE EXTRACTION
# ==========================================

def extract_features(entry):

    events = entry["Events"]

    timestamps = [e["Timestamp"] for e in events]
    speeds = [e["Speed"] for e in events]
    accelerations = [e["Acceleration"] for e in events]

    corrections = [1 if e["Correction"] else 0 for e in events]
    accel_det = [1 if e["AccelerationDetected"] else 0 for e in events]
    decel_det = [1 if e["DecelerationDetected"] else 0 for e in events]
    idle_times = [e["IdleTime"] for e in events]

    x_coords = [e["X"] for e in events]
    y_coords = [e["Y"] for e in events]

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
        "prop_accel_detected": np.mean(accel_det),
        "prop_decel_detected": np.mean(decel_det),

        "total_duration":
            (timestamps[-1] - timestamps[0]) / 1000
            if len(timestamps) > 1 else 0,

        "total_distance": total_distance
    }

# ==========================================
# DISCRIMINATOR
# ==========================================

class Discriminator(nn.Module):

    def __init__(self, feature_dim):
        super().__init__()

        self.model = nn.Sequential(
            nn.Linear(feature_dim, 128),
            nn.LeakyReLU(0.2),
            nn.Linear(128, 64),
            nn.LeakyReLU(0.2),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.model(x)

# ==========================================
# LOAD FILE
# ==========================================

with open("mouse_data_bot2.json", "r") as f:
    data = json.load(f)

# ==========================================
# BUILD FEATURES
# ==========================================

rows = []

for session in data:
    rows.append(extract_features(session))

X = pd.DataFrame(rows)

# ==========================================
# LOAD SCALER
# ==========================================

scaler = joblib.load("GAN_scaler.pkl")

X_scaled = scaler.transform(X)

# ==========================================
# LOAD DISCRIMINATOR
# ==========================================

feature_dim = X_scaled.shape[1]

D = Discriminator(feature_dim)

D.load_state_dict(
    torch.load(
        "GAN_discriminator.pth",
        map_location=torch.device("cpu")
    )
)

D.eval()

# ==========================================
# PREDICTION
# ==========================================

with torch.no_grad():

    X_tensor = torch.FloatTensor(X_scaled)

    discriminator_score = (
        D(X_tensor)
        .numpy()
        .flatten()
    )

    anomaly_score = 1 - discriminator_score

# ==========================================
# THRESHOLD
# ==========================================
# AJUSTA ESTE VALOR
# ==========================================

threshold = 0.50

predictions = np.where(
    anomaly_score > threshold,
    0,
    1
)

# ==========================================
# RESULTS
# ==========================================

for i in range(len(predictions)):

    print(f"\nSession {i+1}")

    print(
        f"Discriminator Score: "
        f"{discriminator_score[i]:.4f}"
    )

    print(
        f"Anomaly Score: "
        f"{anomaly_score[i]:.4f}"
    )

    print(
        "Prediction:",
        "Human"
        if predictions[i] == 1
        else "Bot"
    )
