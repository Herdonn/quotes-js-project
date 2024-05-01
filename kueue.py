import pandas as pd

df = pd.read_csv("test.csv")

df = df[~df.phrase.str.contains("hackernoon", case=False)]
df = df.drop_duplicates(subset = 'phrase')
print(df)