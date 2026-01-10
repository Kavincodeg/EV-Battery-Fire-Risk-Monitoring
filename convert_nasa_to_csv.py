import scipy.io
import pandas as pd
import os
import numpy as np

input_folder = "data/nasa_raw"
output_file = "data/nasa_battery_data.csv"

records = []

for file in os.listdir(input_folder):
    if not file.endswith(".mat"):
        continue

    print(f"Processing {file} ...")
    mat = scipy.io.loadmat(os.path.join(input_folder, file))

    battery = mat["battery"][0][0]
    cycles = battery["cycle"][0]

    for cycle in cycles:
        # Extract cycle type safely
        cycle_type = cycle["type"]

        if isinstance(cycle_type, np.ndarray):
            cycle_type = cycle_type.item()

        if cycle_type != "discharge":
            continue

        data = cycle["data"][0][0]

        voltage = data["Voltage_measured"][0]
        current = data["Current_measured"][0]
        temperature = data["Temperature_measured"][0]
        capacity = float(data["Capacity"][0][0])

        for v, c, t in zip(voltage, current, temperature):
            records.append([v, c, t, capacity])

# Convert to DataFrame
df = pd.DataFrame(
    records,
    columns=["Voltage", "Current", "Temperature", "Capacity"]
)

df.to_csv(output_file, index=False)

print("\nNASA dataset converted successfully!")
print("Saved as:", output_file)
print("Total records:", len(df))
