import os
import pandas as pd
from ucimlrepo import fetch_ucirepo

# Ensure clinical_data directory exists
os.makedirs("clinical_data", exist_ok=True)

def fetch_and_save(dataset_id, name):
    print(f"Fetching {name} (ID: {dataset_id})...")
    try:
        # fetch dataset 
        dataset = fetch_ucirepo(id=dataset_id) 
        
        # data (as pandas dataframes) 
        X = dataset.data.features 
        y = dataset.data.targets 
        
        # Combine features and targets
        df = pd.concat([X, y], axis=1)
        
        # Save to CSV
        filename = f"clinical_data/{name.lower().replace(' ', '_')}.csv"
        df.to_csv(filename, index=False)
        print(f"Successfully saved {name} to {filename}")
        
        # Print metadata and variable info
        print(f"\nMetadata for {name}:")
        print(dataset.metadata)
        print(f"\nVariables for {name}:")
        print(dataset.variables)
        print("-" * 50)
        
    except Exception as e:
        print(f"Error fetching {name}: {e}")

if __name__ == "__main__":
    # Fetch all 3 datasets
    fetch_and_save(45, "Heart Disease")
    fetch_and_save(336, "Chronic Kidney Disease")
    fetch_and_save(529, "Early Stage Diabetes Risk Prediction")
