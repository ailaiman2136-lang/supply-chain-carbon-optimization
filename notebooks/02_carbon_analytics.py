import pandas as pd
import numpy as np
import os

# Set paths
data_dir = "../data" if os.path.exists("../data") else "data"
processed_file = f"{data_dir}/processed/cleaned_master_logistics.csv"

# Load our cleaned master dataset
df = pd.read_csv(processed_file)

print("--- Data Loaded for Carbon & Delay Analytics ---")

# 1. Fill missing logistics values safely
# If a shipment didn't map to a specific logistics date, use fallback medians
df['delay_hours_avg'] = df['delay_hours_avg'].fillna(df['delay_hours_avg'].median())
df['fuel_price_usd_per_barrel'] = df['fuel_price_usd_per_barrel'].fillna(df['fuel_price_usd_per_barrel'].median())

# 2. Business Logic Calculations
# Let's assume standard corporate carrier values for a baseline container ship:
# - Baseline fuel burn rate: 5 barrels of fuel per hour of transit/idle time.
# - Carbon intensity factor: 0.43 metric tons of CO2 produced per barrel of marine fuel burned.

df['estimated_fuel_waste_barrels'] = df['delay_hours_avg'] * 5
df['excess_fuel_cost_usd'] = df['estimated_fuel_waste_barrels'] * df['fuel_price_usd_per_barrel']
df['excess_carbon_emissions_mt'] = df['estimated_fuel_waste_barrels'] * 0.43

# 3. Aggregate Route Metrics for our Executive Dashboard
route_summary = df.groupby(['origin', 'destination', 'region']).agg(
    total_shipments=('shipment_id', 'count'),
    avg_delay_hours=('delay_hours_avg', 'mean'),
    total_fuel_waste_barrels=('estimated_fuel_waste_barrels', 'sum'),
    total_excess_cost_usd=('excess_fuel_cost_usd', 'sum'),
    total_carbon_waste_mt=('excess_carbon_emissions_mt', 'sum')
).reset_index()

# Sort by the most problematic routes (highest financial & environmental waste)
route_summary = route_summary.sort_values(by='total_excess_cost_usd', ascending=False)

# 4. Statistical Correlation Matrix
# This calculates the mathematical relationship between delays, fuel costs, and value
correlation_matrix = df[['delay_hours_avg', 'estimated_fuel_waste_barrels', 'excess_fuel_cost_usd', 'value', 'freight_cost']].corr()

# Save analytics outputs
os.makedirs(f"{data_dir}/analytics", exist_ok=True)
route_summary.to_csv(f"{data_dir}/analytics/route_carbon_summary.csv", index=False)
correlation_matrix.to_csv(f"{data_dir}/analytics/metric_correlations.csv")

print("SUCCESS: Analytics pipeline executed cleanly without terminal breaks.")
print(f"Top high-waste route: {route_summary['origin'].iloc[0]} to {route_summary['destination'].iloc[0]}")
print(f"Total excess carbon emissions calculated: {df['excess_carbon_emissions_mt'].sum():,.2f} Metric Tons")
