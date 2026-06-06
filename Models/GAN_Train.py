
# GAN Anomaly Detection Model

import json
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.inspection import permutation_importance

# ==========================================================
# LOAD DATASET
# ==========================================================

with open("Dataset1_Train.json", "r") as f:
    data = json.load(f)

# ==========================================================
# FEATURE ENGINEERING
# ==========================================================

features_list = []
labels = []

for entry in data:

    events = entry["Events"]

    if not events:
        continue

    label = int(entry["Label"])

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
            (x_coords[i] - x_coords[i-1])**2 +
            (y_coords[i] - y_coords[i-1])**2
        )

    features_list.append({
        "num_events": len(events),
        "avg_speed": np.mean(speeds) if speeds else 0,
        "max_speed": np.max(speeds) if speeds else 0,
        "min_speed": np.min(speeds) if speeds else 0,
        "std_speed": np.std(speeds) if speeds else 0,
        "avg_acceleration": np.mean(accelerations) if accelerations else 0,
        "max_acceleration": np.max(accelerations) if accelerations else 0,
        "min_acceleration": np.min(accelerations) if accelerations else 0,
        "std_acceleration": np.std(accelerations) if accelerations else 0,
        "avg_idle_time": np.mean(idle_times) if idle_times else 0,
        "max_idle_time": np.max(idle_times) if idle_times else 0,
        "min_idle_time": np.min(idle_times) if idle_times else 0,
        "std_idle_time": np.std(idle_times) if idle_times else 0,
        "prop_correction": np.mean(corrections) if corrections else 0,
        "prop_accel_detected": np.mean(accel_det) if accel_det else 0,
        "prop_decel_detected": np.mean(decel_det) if decel_det else 0,
        "total_duration": ((timestamps[-1]-timestamps[0])/1000) if len(timestamps)>1 else 0,
        "total_distance": total_distance
    })

    labels.append(label)

df = pd.DataFrame(features_list)
df["label"] = labels

# ==========================================================
# TRAIN ONLY WITH HUMANS
# ==========================================================

human_df = df[df["label"] == 1].drop(columns=["label"])

X_train, _ = train_test_split(
    human_df,
    test_size=0.20,
    random_state=42
)

X_test_features = df.drop(columns=["label"])
y_test = df["label"].values

# ==========================================================
# SCALING
# ==========================================================

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test_features)

# ==========================================================
# GAN
# ==========================================================

class Generator(nn.Module):
    def __init__(self, latent_dim, feature_dim):
        super().__init__()
        self.model = nn.Sequential(
            nn.Linear(latent_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Linear(128, feature_dim)
        )

    def forward(self, z):
        return self.model(z)

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

feature_dim = X_train_scaled.shape[1]
latent_dim = 32

G = Generator(latent_dim, feature_dim)
D = Discriminator(feature_dim)

criterion = nn.BCELoss()

opt_G = optim.Adam(G.parameters(), lr=0.0002)
opt_D = optim.Adam(D.parameters(), lr=0.0002)

X_train_tensor = torch.FloatTensor(X_train_scaled)

epochs = 3000
batch_size = 32

for epoch in range(epochs):

    idx = np.random.randint(0, X_train_tensor.size(0), batch_size)
    real = X_train_tensor[idx]

    real_y = torch.ones((batch_size, 1)) * 0.9
    fake_y = torch.zeros((batch_size, 1)) + 0.1

    z = torch.randn(batch_size, latent_dim)
    fake = G(z)

    g_loss = criterion(D(fake), real_y)

    opt_G.zero_grad()
    g_loss.backward()
    opt_G.step()

    real_loss = criterion(D(real), real_y)
    fake_loss = criterion(D(fake.detach()), fake_y)

    d_loss = (real_loss + fake_loss) / 2

    opt_D.zero_grad()
    d_loss.backward()
    opt_D.step()

# ==========================================================
# CLASSIFIER
# ==========================================================

class GANClassifier:

    def __init__(self, discriminator):
        self.D = discriminator

    def anomaly_score(self, X):
        with torch.no_grad():
            X = torch.FloatTensor(X)
            return (1 - self.D(X)).numpy().flatten()

model = GANClassifier(D)

scores = model.anomaly_score(X_test_scaled)

human_scores = scores[y_test == 1]
bot_scores = scores[y_test == 0]

threshold = (np.mean(human_scores) + np.mean(bot_scores)) / 2

y_pred = np.where(scores > threshold, 0, 1)

# ==========================================================
# EVALUATION
# ==========================================================

print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred, target_names=["Bot","Human"]))
print(confusion_matrix(y_test, y_pred))

# ==========================================================
# FEATURE IMPORTANCE
# ==========================================================

class GANPredictorWrapper:

    def __init__(self, gan_classifier, threshold):
        self.gan_classifier = gan_classifier
        self.threshold = threshold

    def fit(self, X, y=None):
        return self

    def predict(self, X):
        scores = self.gan_classifier.anomaly_score(X)
        return np.where(scores > self.threshold, 0, 1)

wrapper = GANPredictorWrapper(model, threshold)

result = permutation_importance(
    wrapper,
    X_test_scaled,
    y_test,
    n_repeats=20,
    random_state=42,
    scoring="accuracy"
)

importance_df = pd.DataFrame({
    "Feature": X_test_features.columns,
    "Importance": result.importances_mean
})

importance_df = importance_df.sort_values(
    by="Importance",
    ascending=False
)

print("\n=== GAN FEATURE IMPORTANCE ===")
print(importance_df.to_string(index=False))

# ==========================================================
# SAVE
# ==========================================================

torch.save(G.state_dict(), "GAN_generator.pth")
torch.save(D.state_dict(), "GAN_discriminator.pth")
joblib.dump(scaler, "GAN_scaler.pkl")
