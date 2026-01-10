import pandas as pd
#LOADING THE FILE FOR PHASE 1(CONVERTING THESE FILE FROM PINCODE-LEVEL TO DISTRICT LEVEL AND ARRANGING THEM STATE WISE) for pan-india anaylsis
file_path1 = "data/raw/aadhar-enrollment-complete-dataset/api_data_aadhar_enrolment_0_500000.csv"
file_path2 = "data/raw/aadhar-enrollment-complete-dataset/api_data_aadhar_enrolment_500000_1000000.csv"
file_path3 = "data/raw/aadhar-enrollment-complete-dataset/api_data_aadhar_enrolment_1000000_1006029.csv"
file_path4 = "data/cleaned-dataset/aadhar_enrolment_full_cleaned.csv"
df9 = pd.read_csv(file_path4)
print(df9.shape)
# converting to dataFrames
df1 = pd.read_csv(file_path1)
df2 = pd.read_csv(file_path2)
df3 = pd.read_csv(file_path3) 
df = pd.concat([df1,df2,df3],ignore_index=True) # ignore_index = True reset index
# removing duplication correctly 
df = df[~df['state'].str.match(r'^\d+$', na=False)]

df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['state'] = df['state'].str.strip().str.lower()
df['district'] = df['district'].str.strip().str.lower()
df['pincode'] = pd.to_numeric(df['pincode'], errors='coerce')

for col in ['age_0_5','age_5_17','age_18_greater']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# df = df.dropna(subset=['date','state','district'])

df = (
    df.groupby(['date','state','district'], as_index=False)
      .agg({
          'age_0_5': 'sum',
          'age_5_17': 'sum',
          'age_18_greater': 'sum'
      })
)

# rows = df.shape[0]
#column = df.shape[1]
# df.info() tells the status of data and it's clean
print('\n')

#null test
# print(df.isna().sum()) #if retrun 0 then nothing missing
# print(df.dtypes)
print(df.shape)
# print("No. of rows which are exact copies of previous is: ",df.duplicated().sum())
# print(df.head())
# print(df.tail())
# print(df.columns.tolist()) #return the column name 
# print('\n')
# print(df.sample(10, random_state=42))
# print(df.describe())
# export to new file
# df.to_csv("aadhar_enrollment_deduped.csv", index=False)
print(df.shape)
print(df.groupby('state')['district'].nunique())

print(df.columns.tolist()) #return the column name
#renaming columns do it in very last, after completely analysising the
# df.rename(columns={"age_0_5":"Age (0-5)","age_5_17":"Age (5-17)","age_18_greater":"Age 18+"},inplace=True)
