from sqlalchemy import create_engine


#connect to SQL
engine=create_engine("mssql+pyodbc://@MarketingWorkConnection64bit")
table_name='HP_Serialized_Parts'
output_file= r'\\insight.com\team\finance\Business Intelligence\Working Folders\Yunior\HP_Serialized_Parts\HP_Serialized_Parts\result.csv'





        



