#dataframe = it is a tabular data structure with rows and column(2-d)
import pandas as pd

data = {"Name": ["Joe","Spongebob","Patric","Squidward"],
        "Age":[30,23,25,34]}

df = pd.DataFrame(data, index=["Employee 1","Employee 2","Employee 3","Employee 4"])
print(df)

print(df.loc["Employee 1"]) # searching the data for a particular employee

# add a new column
df["Job"] = ["UI/UX","Doctor","Cook","N/A"]
print(df)

# add a new row
new_row = pd.DataFrame([{"Name":"Sandy", "Age":29, "Job":"Crewmate"}],index=["Employee 5"])
df = pd.concat([df,new_row])
print(df)