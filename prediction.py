import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose
import sqlite3

# Connect to the database and retrieve the flight data
conn = sqlite3.connect('flightsDatatest.db')
c = conn.cursor()
c.execute('SELECT * FROM flights')
data = c.fetchall()
conn.close()

# Convert data into a Pandas DataFrame
df = pd.DataFrame(data, columns=['Date', 'flight_name', 'flight_duration', 'departure_time', 'arrival_time', 'stops', 'price'])

# Convert the date column to a Pandas DateTime index
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)

# Convert price column to float type
df['price'] = df['price'].str.replace(',', '').astype(float)

df_grouped = df.groupby(df.index)['price'].mean().to_frame()

# Perform seasonal decomposition on the data to identify trends and seasonal patterns
result = seasonal_decompose(df_grouped['price'], model='multiplicative', period=3)

# Retrieve the seasonal, trend and residual components of the decomposition
seasonal = result.seasonal
trend = result.trend
residual = result.resid

# Fill NaN values in seasonal and trend components using interpolation
seasonal = seasonal.interpolate()
trend = trend.interpolate()

# Make a prediction for the next 3 days based on the seasonal and trend components
last_date = df_grouped.index[-1]
prediction = pd.DataFrame(index=pd.date_range(start=last_date, periods=3, freq='D'), columns=['price'])
prediction['price'] = trend.iloc[-1] * seasonal.iloc[-3:].values

# Print the predicted prices
print(prediction)
