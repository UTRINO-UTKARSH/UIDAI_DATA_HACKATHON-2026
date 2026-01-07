import pandas as pd
data =[100,22,193,1000,200]
series = pd.Series(data, index=["a","b","c","d","e"])
print(series)
print(series.loc["a"]) # TO access a values in a series we use it's index/key to get the value,here "loc" is loaction by lable property, here any thing can be lable
print(series.iloc[2]) # it is integer-location-based/ we use number as lables

# now if we want values which are greater the 200
print(series[series>=200])

# now using it with dict

cal = {"Day 1": 603, "Day 2":3000, "Day 3":1200}
series = pd.Series(cal), #Since we have dictionary which act as key-value pair so no need to fill index
print(series)
print(series[series >= 2000])