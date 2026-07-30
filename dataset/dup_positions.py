import pandas as pd

df = pd.read_csv("positions.csv")

original = len(df)

df = df.drop_duplicates(subset="fen")

unique = len(df)

df.to_csv("positions_unique.csv", index=False)

print(f"Original positions : {original}")
print(f"Unique positions   : {unique}")
print(f"Duplicates removed : {original - unique}")