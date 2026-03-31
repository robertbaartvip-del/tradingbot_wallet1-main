import pandas as pd

# Example dataframe
data = [
{"start_time": "2024-12-06 12:15:03", "end_time": "2024-12-06 12:36:03", "side": "short", "entry_price": 235.14, "end_price": 234.02, "balance": 103.07598685},
{"start_time": "2024-12-06 16:00:00", "end_time": "2024-12-06 17:33:02", "side": "long", "entry_price": 232.27, "end_price": 238.87, "balance": 119.461562},
{"start_time": "2024-12-06 17:39:02", "end_time": "2024-12-06 19:00:02", "side": "long", "entry_price": 238.98, "end_price": 239.17, "balance": 110.97210458},
{"start_time": "2024-12-06 19:06:02", "end_time": "2024-12-06 20:30:02", "side": "long", "entry_price": 239.63, "end_price": 239.5, "balance": 105.09914462},
{"start_time": "2024-12-06 20:42:02", "end_time": "2024-12-06 20:51:02", "side": "long", "entry_price": 239.27, "end_price": 238.43, "balance": 100.02965179},
{"start_time": "2024-12-06 22:03:02", "end_time": "2024-12-06 22:12:02", "side": "long", "entry_price": 238.6504878, "end_price": 237.55, "balance": 99.44808169},
{"start_time": "2024-12-06 22:18:02", "end_time": "2024-12-06 23:00:02", "side": "long", "entry_price": 237.93, "end_price": 237.59, "balance": 96.92163049},
{"start_time": "2024-12-07 00:00:00", "end_time": "2024-12-07 00:42:02", "side": "long", "entry_price": 236.4, "end_price": 236.13, "balance": 102.04162853},
{"start_time": "2024-12-07 00:48:02", "end_time": "2024-12-07 01:27:02", "side": "long", "entry_price": 236.22, "end_price": 235.36, "balance": 84.0728719},
{"start_time": "2024-12-07 01:36:02", "end_time": "2024-12-07 03:12:02", "side": "long", "entry_price": 235.67, "end_price": 235.45, "balance": 79.23376094},
{"start_time": "2024-12-07 03:30:02", "end_time": "2024-12-07 05:51:02", "side": "long", "entry_price": 234.93, "end_price": 235.46, "balance": 69.00990573},
{"start_time": "2024-12-07 05:57:02", "end_time": "2024-12-07 06:12:02", "side": "long", "entry_price": 235.62, "end_price": 234.95, "balance": 65.10888903},
{"start_time": "2024-12-07 06:51:03", "end_time": "2024-12-07 07:00:04", "side": "short", "entry_price": 236.07047619, "end_price": 236.1, "balance": 56.8514292},
{"start_time": "2024-12-07 08:00:00", "end_time": "2024-12-07 08:00:06", "side": "short", "entry_price": 236.44, "end_price": 236.42, "balance": 63.44324059},
{"start_time": "2024-12-07 08:30:02", "end_time": "2024-12-07 10:21:02", "side": "long", "entry_price": 235.79, "end_price": 237.47, "balance": 69.40600999},
{"start_time": "2024-12-07 10:36:02", "end_time": "2024-12-07 11:00:04", "side": "short", "entry_price": 238.47, "end_price": 238.66, "balance": 71.71299399},
{"start_time": "2024-12-07 11:27:03", "end_time": "2024-12-07 11:42:02", "side": "short", "entry_price": 239.02, "end_price": 239.24, "balance": 69.21237798},
{"start_time": "2024-12-07 12:12:02", "end_time": "2024-12-07 12:54:03", "side": "long", "entry_price": 237.94, "end_price": 238.12, "balance": 68.01441664},
{"start_time": "2024-12-07 13:12:02", "end_time": "2024-12-07 13:27:02", "side": "short", "entry_price": 237.96, "end_price": 238.33, "balance": 65.44539479},
{"start_time": "2024-12-07 14:06:02", "end_time": "2024-12-07 14:33:02", "side": "short", "entry_price": 238.79, "end_price": 239.59, "balance": 68.324618},
{"start_time": "2024-12-07 15:06:02", "end_time": "2024-12-07 15:45:02", "side": "short", "entry_price": 242.55, "end_price": 240.78, "balance": 74.49170885},
{"start_time": "2024-12-07 16:39:03", "end_time": "2024-12-07 17:18:02", "side": "long", "entry_price": 239.94, "end_price": 240.6, "balance": 105.85429858},
{"start_time": "2024-12-07 17:48:02", "end_time": "2024-12-07 17:54:02", "side": "long", "entry_price": 241.17, "end_price": 240.14, "balance": 99.95270427},
{"start_time": "2024-12-06 11:54:03", "end_time": "2024-12-06 12:54:03", "side": "long", "entry_price": 2.2635, "end_price": 2.2719, "balance": 106.10396089},
{"start_time": "2024-12-06 13:03:04", "end_time": "2024-12-06 14:18:03", "side": "long", "entry_price": 2.2728, "end_price": 2.2886, "balance": 111.40278354},
{"start_time": "2024-12-06 14:36:03", "end_time": "2024-12-06 14:51:03", "side": "short", "entry_price": 2.3172, "end_price": 2.3289, "balance": 105.27298088},
{"start_time": "2024-12-06 15:03:03", "end_time": "2024-12-06 15:12:03", "side": "short", "entry_price": 2.3255, "end_price": 2.3648, "balance": 87.34848426},
{"start_time": "2024-12-06 16:00:00", "end_time": "2024-12-06 16:06:03", "side": "short", "entry_price": 2.3634, "end_price": 2.352, "balance": 91.2041202},
{"start_time": "2024-12-06 16:48:03", "end_time": "2024-12-06 17:18:03", "side": "short", "entry_price": 2.3941, "end_price": 2.3904, "balance": 91.64648955},
{"start_time": "2024-12-06 18:12:02", "end_time": "2024-12-06 18:42:02", "side": "long", "entry_price": 2.3712, "end_price": 2.3545, "balance": 110.72643623},
{"start_time": "2024-12-06 19:12:02", "end_time": "2024-12-06 19:42:02", "side": "long", "entry_price": 2.3484, "end_price": 2.3409, "balance": 106.17221712},
{"start_time": "2024-12-06 20:42:02", "end_time": "2024-12-06 21:12:02", "side": "short", "entry_price": 2.4021, "end_price": 2.3873, "balance": 105.58522774},
{"start_time": "2024-12-06 22:03:02", "end_time": "2024-12-06 23:18:02", "side": "long", "entry_price": 2.37532938, "end_price": 2.4181, "balance": 114.41808479},
{"start_time": "2024-12-07 00:00:00", "end_time": "2024-12-07 00:12:02", "side": "long", "entry_price": 2.3991, "end_price": 2.4017, "balance": 112.68810999},
{"start_time": "2024-12-07 00:30:02", "end_time": "2024-12-07 00:36:02", "side": "short", "entry_price": 2.4226, "end_price": 2.4418, "balance": 103.72108883},
{"start_time": "2024-12-07 00:54:02", "end_time": "2024-12-07 01:06:02", "side": "short", "entry_price": 2.4498, "end_price": 2.4785, "balance": 88.7746815},
{"start_time": "2024-12-07 01:21:02", "end_time": "2024-12-07 02:09:02", "side": "short", "entry_price": 2.4824, "end_price": 2.4716, "balance": 87.1846562},
{"start_time": "2024-12-07 02:54:02", "end_time": "2024-12-07 03:12:02", "side": "long", "entry_price": 2.4518, "end_price": 2.4386, "balance": 80.70165044},
{"start_time": "2024-12-07 03:30:02", "end_time": "2024-12-07 03:42:02", "side": "long", "entry_price": 2.4286, "end_price": 2.4185, "balance": 73.41875387},
{"start_time": "2024-12-07 04:06:02", "end_time": "2024-12-07 05:06:02", "side": "long", "entry_price": 2.4174, "end_price": 2.4207, "balance": 73.6833185},
{"start_time": "2024-12-07 05:15:02", "end_time": "2024-12-07 05:21:02", "side": "long", "entry_price": 2.4235, "end_price": 2.4121, "balance": 67.87671195},
{"start_time": "2024-12-07 05:27:02", "end_time": "2024-12-07 06:12:02", "side": "long", "entry_price": 2.4106, "end_price": 2.4134, "balance": 65.71855785},
{"start_time": "2024-12-07 06:42:02", "end_time": "2024-12-07 06:51:02", "side": "short", "entry_price": 2.4288, "end_price": 2.4432, "balance": 58.69884225},
{"start_time": "2024-12-07 07:00:04", "end_time": "2024-12-07 07:36:02", "side": "short", "entry_price": 2.439, "end_price": 2.4175, "balance": 64.55493617},
{"start_time": "2024-12-07 08:00:00", "end_time": "2024-12-07 10:27:02", "side": "long", "entry_price": 2.398, "end_price": 2.4238, "balance": 79.60871146},
{"start_time": "2024-12-07 10:33:02", "end_time": "2024-12-07 10:51:02", "side": "long", "entry_price": 2.4261, "end_price": 2.4141, "balance": 73.03017229},
{"start_time": "2024-12-07 11:00:04", "end_time": "2024-12-07 12:36:03", "side": "long", "entry_price": 2.4264, "end_price": 2.4272, "balance": 68.40052081},
{"start_time": "2024-12-07 12:45:02", "end_time": "2024-12-07 13:36:02", "side": "long", "entry_price": 2.4334, "end_price": 2.4537, "balance": 73.2340359},
{"start_time": "2024-12-07 16:00:00", "end_time": "2024-12-07 17:03:02", "side": "long", "entry_price": 2.442, "end_price": 2.5176, "balance": 103.64987413},
{"start_time": "2024-12-07 17:21:02", "end_time": "2024-12-07 18:00:02", "side": "long", "entry_price": 2.5229, "end_price": 2.4905, "balance": 86.51233382},

]

# Create the dataframe
df = pd.DataFrame(data)

# Convert the 'end_time' column to datetime format for sorting
df['end_time'] = pd.to_datetime(df['end_time'])

# Sort the dataframe by 'end_time'
df = df.sort_values(by='end_time')

# Define the function to calculate win
def calculate_win(row):
    if row['side'] == 'long':
        return 1 if row['end_price'] > row['entry_price'] else 0
    elif row['side'] == 'short':
        return 1 if row['entry_price'] > row['end_price'] else 0
    return 0

# Apply the function to create the 'win' column
df['win'] = df.apply(calculate_win, axis=1)

# Calculate the profit by subtracting the balance of the previous row from the current one
df['profit'] = df['balance'].diff().fillna(0)

# Add a 'symbol' column based on price ranges
def determine_symbol(row):
    if 200 <= row['entry_price'] <= 300 or 200 <= row['end_price'] <= 300:
        return 'SOL'
    elif 2 <= row['entry_price'] <= 3 or 2 <= row['end_price'] <= 3:
        return 'XRP'
    return 'Unknown'  # Default case if no match

# Apply the function to create the 'symbol' column
df['symbol'] = df.apply(determine_symbol, axis=1)

# Calculate the summary table
summary = df.groupby('symbol').agg(
    total=('symbol', 'size'),
    win=('win', 'sum'),
    win_rate=('win', lambda x: x.sum() / x.size if x.size > 0 else 0),
    profit=('profit', 'sum')
).reset_index()

# Reorganize the summary to have SOL and XRP as columns, and total, win, win_rate, profit as rows
summary_table = summary.set_index('symbol').T

# Save both the detailed data and the summary table to an Excel file
with pd.ExcelWriter('trading_data_with_summary.xlsx') as writer:
    df.to_excel(writer, sheet_name='Data', index=False)
    summary_table.to_excel(writer, sheet_name='Summary')

# Display the dataframe and summary table
print(df)
print(summary_table)
