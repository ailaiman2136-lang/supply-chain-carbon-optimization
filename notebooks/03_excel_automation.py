import pandas as pd
import os

# Set paths
data_dir = "../data" if os.path.exists("../data") else "data"
analytics_file = f"{data_dir}/analytics/route_carbon_summary.csv"
correlation_file = f"{data_dir}/analytics/metric_correlations.csv"
output_excel = f"{data_dir}/analytics/Supply_Chain_Carbon_Optimization_Report.xlsx"

# Load the datasets we calculated in Phase 3
df_routes = pd.read_csv(analytics_file)
df_corr = pd.read_csv(correlation_file)

# Create an automated Excel writer using the XlsxWriter engine for advanced formatting
with pd.ExcelWriter(output_excel, engine='xlsxwriter') as writer:
    # 1. Write the main dataframes to separate sheets
    df_routes.to_excel(writer, sheet_name='Route Optimization Metrics', index=False)
    df_corr.to_excel(writer, sheet_name='Statistical Correlations')
    
    # Get the workbook and sheet objects to apply professional corporate styles
    workbook  = writer.book
    worksheet = writer.sheets['Route Optimization Metrics']
    
    # Define corporate design themes (Dark Navy headers, soft grey borders)
    header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'fg_color': '#1F4E79',
        'font_color': 'white',
        'border': 1
    })
    
    # Financial/Numeric format with commas and two decimals
    num_format = workbook.add_format({'num_format': '#,##0.00'})
    
    # Apply the dark navy styling across the header row
    for col_num, value in enumerate(df_routes.columns.values):
        worksheet.write(0, col_num, value, header_format)
        
    # Apply automated column width scaling so text never gets cropped or cut off
    for i, col in enumerate(df_routes.columns):
        max_len = max(df_routes[col].astype(str).map(len).max(), len(col)) + 3
        worksheet.set_column(i, i, max_len)
        
    # Apply formatting to numeric tracks (Delays, Fuel, Cost, Carbon fields)
    worksheet.set_column('D:G', None, num_format)
    
    # 2. Inject Automated Conditional Formatting (Data Bars) to highlight carbon hotspots
    # This visually points out the absolute worst-performing routes instantly
    num_rows = len(df_routes)
    worksheet.conditional_format(1, 6, num_rows, 6, {
        'type': 'data_bar',
        'bar_color': '#FFC7CE', # Soft crimson red bar
        'bar_solid': True
    })

print("SUCCESS: Automated Excel Executive Report generated successfully!")
print(f"File location: {output_excel}")
