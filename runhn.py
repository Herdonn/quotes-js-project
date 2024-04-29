import pandas as pd
import scrapy

df = pd.read_csv("scrapy/quotes-js-project/test.csv")
tuple_list = list(zip(df.phrase, df.href))
for phrase, href in tuple_list:
    print(phrase, href)
 