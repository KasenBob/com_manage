import pandas as pd

df=pd.read_excel('stu_message.xlsx')
data=df.head()
print(format(data))