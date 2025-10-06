# backend/train_mission_model.py
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

def generate_training_data(num_samples=5000):
    """Generate realistic training data for asteroid mission planning."""
    np.random.seed(42)
    
    data = []
    
    for i in range(num_samples):
        # Realistic parameter ranges based on known NEOs and mission studies
        lti_days = np.random.uniform(30, 3650)
        delta_v = np.random.uniform(0.0001, 0.1)
        asteroid_mass_kg = 10 ** np.random.uniform(6, 14)
        
        # Determine mission type based on physics and mission constraints
        if lti_days < 365:
            if asteroid_mass_kg < 1e9:
                mission_type = "Earth-Vehicle_Rapid-Kinetic"
            else:
                mission_type = "Earth-Vehicle_Nuclear-Disruption"
        else:
            if delta_v < 0.005:
                if asteroid_mass_kg < 1e10:
                    mission_type = "Cislunar-Depot_Enhanced-Kinetic"
                else:
                    mission_type = "Cislunar-Depot_Nuclear-Deflection"
            else:
                mission_type = "Earth-Vehicle_Heavy-Kinetic"
        
        data.append([lti_days, delta_v, asteroid_mass_kg, mission_type])
    
    return pd.DataFrame(data, columns=['lti_days', 'delta_v', 'asteroid_mass_kg', 'mission_type'])

def train_mission_planner_model():
    """Train and save the mission planning ML model."""
    print("🚀 Generating training data for mission planner...")
    
    df = generate_training_data(10000)
    X = df[['lti_days', 'delta_v', 'asteroid_mass_kg']]
    y = df['mission_type']
    
    # Log transform mass for better model performance
    X['asteroid_mass_log'] = np.log10(X['asteroid_mass_kg'])
    X = X[['lti_days', 'delta_v', 'asteroid_mass_log']]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Training set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")
    print(f"Mission types: {y.unique()}")
    
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        class_weight='balanced'
    )
    
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"✅ Model trained successfully!")
    print(f"📊 Test Accuracy: {accuracy:.3f}")
    print("\n📈 Classification Report:")
    print(classification_report(y_test, y_pred))
    
    os.makedirs('ml_models', exist_ok=True)
    model_path = 'ml_models/mission_planner_model.pkl'
    joblib.dump(model, model_path)
    
    feature_info = {
        'feature_names': X.columns.tolist(),
        'classes': model.classes_.tolist(),
        'training_date': pd.Timestamp.now().isoformat()
    }
    joblib.dump(feature_info, 'ml_models/model_metadata.pkl')
    
    print(f"💾 Model saved to: {model_path}")
    
    # Test with examples
    print("\n🧪 Testing with realistic examples:")
    test_cases = [
        [180, 0.001, 1e8],
        [1000, 0.01, 1e11],
        [30, 0.05, 1e12],
    ]
    
    for i, (lti, dv, mass) in enumerate(test_cases):
        features = np.array([[lti, dv, np.log10(mass)]])
        prediction = model.predict(features)[0]
        confidence = np.max(model.predict_proba(features)[0]) * 100
        print(f"Case {i+1}: → {prediction} ({confidence:.1f}% confidence)")
    
    return model, accuracy

if __name__ == '__main__':
    train_mission_planner_model()