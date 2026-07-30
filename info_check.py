import pandas as pd

df = pd.read_csv("positions.csv")

print(df.dtypes)
# print("Duplicate FENs:", df["fen"].duplicated().sum())
# print(df.shape)
# print(df.columns)
# print(df["phase"].value_counts())
# print(df["result"].value_counts())
# print(df.isnull().sum())