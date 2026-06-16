#!/usr/bin/env python3
"""
Send test predictions to microloan-xgboost model
This will populate TrustyAI with logged predictions for bias monitoring
"""

import requests
import json
import pandas as pd
import numpy as np
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load sample data
print("Loading test data...")
df = pd.read_csv('../data/application_train.csv') if os.path.exists('../data/application_train.csv') else pd.read_csv('data/application_train.csv')

# Same preprocessing as training
numeric_features = [
    'AMT_INCOME_TOTAL', 'AMT_CREDIT', 'AMT_ANNUITY', 'AMT_GOODS_PRICE',
    'DAYS_BIRTH', 'DAYS_EMPLOYED', 'REGION_POPULATION_RELATIVE', 'CNT_FAM_MEMBERS'
]
binary_features = ['FLAG_MOBIL', 'FLAG_EMAIL', 'FLAG_WORK_PHONE']
categorical_features = [
    'NAME_INCOME_TYPE', 'NAME_EDUCATION_TYPE', 'NAME_FAMILY_STATUS',
    'NAME_HOUSING_TYPE', 'OCCUPATION_TYPE'
]

print("Preprocessing...")
df['AMT_INCOME_TOTAL'] = df['AMT_INCOME_TOTAL'].fillna(df.groupby('OCCUPATION_TYPE')['AMT_INCOME_TOTAL'].transform('median'))
df['AMT_ANNUITY'] = df['AMT_ANNUITY'].fillna(df.groupby('NAME_INCOME_TYPE')['AMT_ANNUITY'].transform('median'))
df['AMT_GOODS_PRICE'] = df['AMT_GOODS_PRICE'].fillna(df.groupby(pd.cut(df['AMT_CREDIT'], bins=10))['AMT_GOODS_PRICE'].transform('median'))

for col in numeric_features:
    if df[col].isnull().sum() > 0:
        df[col].fillna(df[col].median(), inplace=True)

X = df[numeric_features + binary_features + categorical_features].copy()
X_encoded = pd.get_dummies(X, columns=categorical_features, drop_first=True)

# Sample data for testing
num_samples = 100
X_sample = X_encoded.sample(n=num_samples, random_state=42)

print(f"\n{'='*60}")
print(f"Sending {num_samples} predictions to populate TrustyAI")
print(f"{'='*60}\n")

# Model endpoint
MODEL_URL = "https://microloan-xgboost-a-rh-department.apps.cluster-94v2k.94v2k.sandbox393.opentlc.com/v2/models/microloan-xgboost/infer"

# Send predictions in batches
batch_size = 10
success_count = 0
error_count = 0

for i in range(0, num_samples, batch_size):
    batch = X_sample.iloc[i:i+batch_size]
    
    # Create KServe V2 payload
    payload = {
        "inputs": [{
            "name": "predict",
            "shape": [len(batch), len(X_sample.columns)],
            "datatype": "FP64",
            "data": batch.values.tolist()
        }]
    }
    
    try:
        response = requests.post(
            MODEL_URL,
            json=payload,
            verify=False,
            timeout=30
        )
        
        if response.status_code == 200:
            success_count += len(batch)
            print(f"✓ Batch {i//batch_size + 1}/{(num_samples + batch_size - 1)//batch_size}: {len(batch)} predictions sent")
        else:
            error_count += len(batch)
            print(f"✗ Batch {i//batch_size + 1}: Failed (HTTP {response.status_code})")
            
    except Exception as e:
        error_count += len(batch)
        print(f"✗ Batch {i//batch_size + 1}: Error - {e}")

print(f"\n{'='*60}")
print(f"Summary:")
print(f"  ✓ Successful: {success_count}/{num_samples}")
print(f"  ✗ Failed: {error_count}/{num_samples}")
print(f"{'='*60}\n")

if success_count > 0:
    print("Next steps:")
    print("1. Verify TrustyAI received the data:")
    print("   bash verify_trustyai_data.sh")
    print("")
    print("2. Configure bias monitoring via OpenShift AI Dashboard")
    print("   Settings → Bias monitoring → Create bias metric")
