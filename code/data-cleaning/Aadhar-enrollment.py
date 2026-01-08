import pandas as pd
#LOADING THE FILE FOR PHASE 1(CONVERTING THESE FILE FROM PINCODE-LEVEL TO DISTRICT LEVEL AND ARRANGING THEM STATE WISE) for pan-india anaylsis
file_path1 = "data/aadhar-enrollment-complete-dataset/api_data_aadhar_enrolment_0_500000.csv"
file_path2 = "data/aadhar-enrollment-complete-dataset/api_data_aadhar_enrolment_500000_1000000.csv"
file_path3 = "data/aadhar-enrollment-complete-dataset/api_data_aadhar_enrolment_1000000_1006029.csv"

# converting to dataFrames
df1 = pd.read_csv(file_path1)
df2 = pd.read_csv(file_path2)
df3 = pd.read_csv(file_path3) 
df = pd.concat([df1,df2,df3],ignore_index=True) # ignore_index = True reset index
# removing duplication correctly 

df = (
    df.groupby(['date','state','district','pincode'], as_index=False)
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
print(df.isna().sum()) #if retrun 0 then nothing missing
print(df.dtypes)
print(df.shape)
print("No. of rows which are exact copies of previous is: ",df.duplicated().sum())
print(df.head())
print(df.tail())
print(df.columns.tolist()) #return the column name 
print('\n')
print(df.sample(10, random_state=42))
print(df.describe())

# export to new file
#df.to_csv("aadhar_enrollment_deduped.csv", index=False)
