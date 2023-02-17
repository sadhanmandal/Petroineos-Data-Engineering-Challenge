# Python 3.x
from urllib.request import urlopen, urlretrieve, quote
from bs4 import BeautifulSoup
import re
import requests
import pandas as pd
import os
import sys
import glob

def getFile(new_file,response_content):
    output = open(new_file, 'wb')
    output.write(response_content.content)
    output.close()
    print("---------Downloaded File in your Path")
    data=pd.read_excel(new_file, sheet_name='Quarter')
    
    return data
        
def clean_n_save_data(new_file,new_data):
    df=new_data.iloc[3::, :]
    print("Cleaned the Data")
    dft=df.transpose()
    dft=dft.reset_index(drop=True)
    dft.columns = dft.iloc[0]
    dft=dft.iloc[1::, :]
    # renaming the column "Column1"
    dft.rename(columns = {"Column1": "Quarters"},inplace = True)
    #Saving Cleanded file to csv
    fncsv=new_file.replace('.xlsx', '.csv')
    dft.to_csv(fncsv)
    print("Saved the data csv after cleaning to local path")
    #Basic Profiling for 
    profileb=dft.describe(include='all')
    prbcsv=new_file.replace('.xlsx', '')+"_data_profiling.csv"
    profileb.to_csv(prbcsv)
    print("Saved the Basic profiling as csv")
    ##Applying Advance Profiling
    dftt=dft.iloc[::, 1::]
    dftt = dftt.astype('float')
    profilen=get_basic_profile(dftt)
    profilen = pd.DataFrame.from_dict(profilen)
    prbcsv=new_file.replace('.xlsx', '')+"_numeric_data_profiling.csv"
    profilen.to_csv(prbcsv)
    print("Saved the Advance Basic profiling as csv")

    return

#Profiling Method
def get_basic_profile(dataframe):
    df=dataframe
    quantile_range = 0.5
    results = {}
    
    for column in dataframe.columns:
        count = df[column].count()
        nans = df[column].isna().sum()
        min = df[column].min()
        max = df[column].max()
        median = df[column].median()
        std = df[column].std()
        kurt = df[column].kurt()
        skew = df[column].skew()
        quant = df[column].quantile(q=quantile_range)
        
        results[column] = {'count': count,
                            'count_na': nans,
                            'min':min,
                            'max':max,
                            'median':median,
                            'std':std,
                            'kurt':kurt,
                            'skew':skew,
                            f'quant {quantile_range}':quant}
 
    return results

if len(sys.argv) > 1:
    url = 'https://www.gov.uk/government/statistics/oil-and-oil-products-section-3-energy-trends'
    u = urlopen(url)
    try:
        html = u.read().decode('utf-8')
    finally:
        u.close()

    soup = BeautifulSoup(html, "html.parser")
    soup=soup.find_all('h3', text=re.compile('natural gas liquids and feedstocks'))
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(soup))
    filename = urls[0].rsplit('/', 1)[-1]

    #check if file exist before downloading
    local_dir = str(sys.argv[1])
    print(local_dir)
    file = os.path.join(local_dir, filename)
    excel_files = glob.glob(os.path.join(local_dir, '*.xlsx'))
    print(excel_files)
    if file not in excel_files:
        print("Downloading new dataset")
        resp = requests.get(urls[0])
        data = getFile(file,resp)
        #Clean and save csv
        clean_n_save_data(file,data)

    else:
        print("No new dataset detected")
else:
    print("Please Pass Local Directory such as: python assignment.py /path_to_directory_to_store_data")
