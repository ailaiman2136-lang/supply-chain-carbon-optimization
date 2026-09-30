import pandas as pd
import numpy as np
import os

# Set paths
data_dir = "../data" if os.path.exists("../data") else "data"

# 1. Load Data
df_customer = pd.read_csv(f"{data_dir}/customer.csv")
df_logistics = pd.read_csv(f"{data_dir}/logistics_performance.csv")
df_shipment = pd.read_csv(f"{data_dir}/shipment.csv")

# 2. Clean Shipment Data
# Fill missing status based on a safe assumption or 'Unknown'
df_shipment['delivery_status'] = df_shipment['delivery_status'].fillna('Unknown')

# Fix corrupted strings in the numeric column (coerce 'On-Time' to NaN, then fill with column median)
df_shipment['customs_clearance_time_days'] = pd.to_numeric(df_shipment['customs_clearance_time_days'], errors='coerce')
median_clearance = df_shipment['customs_clearance_time_days'].median()
df_shipment['customs_clearance_time_days'] = df_shipment['customs_clearance_time_days'].fillna(median_clearance)

# Clean whitespace out of string fields
df_shipment['O_Country'] = df_shipment['O_Country'].str.strip()
df_shipment['D_Country'] = df_shipment['D_Country'].str.strip()

# 3. Handle Dates
df_shipment['date'] = pd.to_datetime(df_shipment['date'], errors='coerce')
df_logistics['date'] = pd.to_datetime(df_logistics['date'], errors='coerce')

# 4. Map Shipments to Regions for accurate Merging
# Map countries to their respective broader corporate logistics regions
region_map = {
    'USA': 'North America', 'Mexico': 'North America',
    'Germany': 'Europe', 'UK': 'Europe', 'Netherlands': 'Europe', 'Finland': 'Europe', 'Turkey': 'Europe',
    'India': 'Asia-Pacific', 'China': 'Asia-Pacific', 'Japan': 'Asia-Pacific', 
    'Vietnam': 'Asia-Pacific', 'South Korea': 'Asia-Pacific', 'Bangladesh': 'Asia-Pacific', 
    'Taiwan': 'Asia-Pacific', 'Thailand': 'Asia-Pacific', 'Indonesia': 'Asia-Pacific', 'Philippines': 'Asia-Pacific'
}
df_shipment['region'] = df_shipment['O_Country'].map(region_map).fillna('Other')

# 5. Merge Data
# Merge core shipment information with daily regional logistics and fuel performance
df_master = pd.merge(df_shipment, df_logistics, on=['date', 'region'], how='left')

# Drop any unmapped country error rows to ensure accurate model metrics
df_master = df_master[~df_master['D_Country'].str.isnumeric()]

# Save the clean dataset
os.makedirs(f"{data_dir}/processed", exist_ok=True)
df_master.to_csv(f"{data_dir}/processed/cleaned_master_logistics.csv", index=False)

print("🚀 Success! Data pipeline executed cleanly.")
print(f"Master dataset saved with {df_master.shape[0]} rows and {df_master.shape[1]} columns.")
