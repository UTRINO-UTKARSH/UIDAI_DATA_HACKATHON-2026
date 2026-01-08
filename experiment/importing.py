import pandas as pd
df = pd.read_csv("data/cleaned-dataset/aadhar_enrollment_deduped.csv")
# df = pd.read_json(file_path.json)
# print(df)# this shows the overview of our file
print(df.head())
print(df.loc[:,"state"])# getting every data of the column named "state"
# print(df.to_string()) # DON'T RUN FOR LARGE FILES, it will give every thing
