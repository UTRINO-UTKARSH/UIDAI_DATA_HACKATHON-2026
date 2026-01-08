import pandas as pd
df = pd.read_csv("cleaned-dataset/aadhar_enrollment_deduped.csv")
# print(df.mean()) # this gives error since we can't find mean of non-numeric column

#the below will be applied for whole dataset
# print(df.mean(numeric_only=True))
# print(df.sum(numeric_only=True))
# print(df.min(numeric_only=True))
# print(df.max(numeric_only=True))
# print(df.count())# counting the value in each column not adidng them

#single column
# print(df["age_5_17"].mean())
# print(df["age_5_17"].sum())
# print(df["age_5_17"].min())
# print(df["age_5_17"].max())
# print(df["age_5_17"].count())

#GROUP BY FUNCTION
#used to group the dataframe into diffrent group of same data
print(df.groupby("state")["age_0_5"].mean())
print("\n")
print(df.groupby("state")["age_0_5"].sum())
print(df.groupby("state")["age_0_5"].count())
 #it is an object, it gives series to work with