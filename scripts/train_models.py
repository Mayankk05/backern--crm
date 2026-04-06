import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib
import os

# Paths
DATA_DIR = "clinical_data"
MODEL_DIR = "ml_models"
os.makedirs(MODEL_DIR, exist_ok=True)

def train_cardiac_model():
    print("\n--- Tuning & Training Cardiac Model (70k rows) ---")
    file_path = os.path.join(DATA_DIR, "cardio_train.csv")
    df = pd.read_csv(file_path, sep=';')
    df['age_years'] = df['age'] / 365.25
    features = ['age_years', 'gender', 'height', 'weight', 'ap_hi', 'ap_lo', 'cholesterol', 'gluc', 'smoke', 'alco', 'active']
    X = df[features]
    y = df['cardio']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    param_grid = {
        'n_estimators': [100, 200, 300],
        'max_depth': [10, 15, 20],
        'min_samples_leaf': [2, 4, 8]
    }
    
    rf = RandomForestClassifier(class_weight='balanced', random_state=42, n_jobs=-1)
    grid_search = GridSearchCV(rf, param_grid, cv=3, scoring='f1', verbose=1)
    grid_search.fit(X_train_scaled, y_train)
    
    model = grid_search.best_estimator_
    print(f"Best Params: {grid_search.best_params_}")
    
    y_pred = model.predict(X_test_scaled)
    print(f"Improved Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print(f"Improved F1 Score: {f1_score(y_test, y_pred):.4f}")
    
    joblib.dump(model, os.path.join(MODEL_DIR, "cardiac_model.pkl"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "cardiac_scaler.pkl"))
    print("Saved optimized cardiac_model.pkl")

def train_renal_model():
    print("\n--- Tuning & Training Renal Model ---")
    df = pd.read_csv(os.path.join(DATA_DIR, "chronic_kidney_disease.csv"))
    df['class'] = df['class'].str.strip()
    df['target'] = (df['class'] == 'ckd').astype(int)
    features = ['age', 'bp', 'bu', 'sc', 'al']
    for col in features:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    X = df[features].fillna(df[features].median())
    y = df['target']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [None, 5, 10],
        'min_samples_split': [2, 5]
    }
    
    rf = RandomForestClassifier(class_weight='balanced', random_state=42)
    grid_search = GridSearchCV(rf, param_grid, cv=5, scoring='accuracy')
    grid_search.fit(X_train, y_train)
    
    model = grid_search.best_estimator_
    y_pred = model.predict(X_test)
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    joblib.dump(model, os.path.join(MODEL_DIR, "renal_model.pkl"))

def train_metabolic_model():
    print("\n--- Tuning & Training Metabolic Model (100k rows) ---")
    df = pd.read_csv(os.path.join(DATA_DIR, "diabetes_prediction_dataset.csv"))
    le = LabelEncoder()
    df['gender_encoded'] = le.fit_transform(df['gender'])
    features = ['age', 'gender_encoded', 'bmi', 'HbA1c_level', 'blood_glucose_level']
    X = df[features]
    y = df['diabetes']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [10, 15],
        'min_samples_leaf': [1, 2]
    }
    
    rf = RandomForestClassifier(class_weight='balanced', random_state=42, n_jobs=-1)
    grid_search = GridSearchCV(rf, param_grid, cv=3, scoring='f1')
    grid_search.fit(X_train, y_train)
    
    model = grid_search.best_estimator_
    y_pred = model.predict(X_test)
    print(f"Improved Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print(f"Improved F1 Score: {f1_score(y_test, y_pred):.4f}")
    joblib.dump(model, os.path.join(MODEL_DIR, "metabolic_model.pkl"))

if __name__ == "__main__":
    train_cardiac_model()
    train_renal_model()
    train_metabolic_model()

if __name__ == "__main__":
    train_cardiac_model()
    train_renal_model()
    train_metabolic_model()
