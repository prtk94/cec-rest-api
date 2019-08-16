import pandas as pd
import numpy as np

months=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

year_data= []
for i in months:
	print(f"reading excel for solar data in month {i}")
	month_df = pd.read_excel(f"Datasets/Solar {i}.xlsx")
	print(f"file read: Datasets/Solar {i}.xlsx")
	month_df.set_index('Unnamed: 0',inplace=True)
	solar_data = month_df[136.05].iloc[6]
	print(f"fetched data => {solar_data}")
	year_data.append(solar_data)

print("full data:")
print(year_data)
