import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import json
import os

os.makedirs('ml_pipeline/models/saved', exist_ok=True)

print("="*50)
print("🤖 GRIDGUARD ML MODEL TRAINING")
print("="*50)

print("\n📊 Generating training data...")
np.random.seed(42)

data = []
for i in range(10000):
    hour = i % 24
    if 6 <= hour <= 9:
        power = 3000 + np.random.normal(0, 300)
    elif 17 <= hour <= 21:
        power = 4000 + np.random.normal(0, 400)
    else:
        power = 2000 + np.random.normal(0, 200)
    
    power = max(0, power)
    voltage = 230 + np.random.normal(0, 5)
    current = power / voltage
    is_anomaly = 1 if i % 20 == 0 else 0
    
    if is_anomaly:
        theft_type = np.random.choice(['drop', 'spike', 'voltage'])
        if theft_type == 'drop':
            power = power * 0.3
        elif theft_type == 'spike':
            power = power * 3
        else:
            voltage = voltage * 0.7
    
    data.append({
        'hour': hour, 
        'day': i % 7, 
        'power': power, 
        'voltage': voltage,
        'current': current, 
        'power_factor': 0.95, 
        'is_anomaly': is_anomaly
    })

df = pd.DataFrame(data)
print(f"✅ Generated {len(df)} samples")
print(f"   Anomaly rate: {df['is_anomaly'].mean()*100:.1f}%")

print("\n🔧 Engineering features...")
features = ['hour', 'day', 'power', 'voltage', 'current', 'power_factor']
X = df[features]
X['power_voltage_ratio'] = X['power'] / (X['voltage'] + 1)
X['hour_sin'] = np.sin(2 * np.pi * X['hour'] / 24)
X['hour_cos'] = np.cos(2 * np.pi * X['hour'] / 24)
print(f"   Features: {len(X.columns)}")

print("\n📏 Scaling features...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print("\n🌲 Training Isolation Forest...")
model = IsolationForest(contamination=0.05, random_state=42)
model.fit(X_scaled)

print("\n💾 Saving models...")
joblib.dump(model, 'ml_pipeline/models/saved/isolation_forest.pkl')
joblib.dump(scaler, 'ml_pipeline/models/saved/scaler.pkl')

feature_names = list(X.columns)
with open('ml_pipeline/models/saved/feature_names.json', 'w') as f:
    json.dump(feature_names, f, indent=2)

print("\n✅ Models saved successfully!")
print(f"   Location: ml_pipeline/models/saved/")
print("\n" + "="*50)
print("✅ TRAINING COMPLETE!")
print("="*50)
