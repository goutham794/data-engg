import pandas as pd
import numpy as np
import regex
import re
import pymongo

import constants

def read_csv(file_path):
    """
    Read a CSV file and return a Pandas DataFrame.
    """
    data = pd.read_csv(file_path)
    data.columns = data.columns.str.strip()
    return data

import pandas as pd
import logging

# Configuring logging
logging.basicConfig(filename='data_cleaning.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def log_change(data_before, data_after, message):
    change = data_before.compare(data_after)
    if not change.empty:
        logging.info(f"{message}: {change.to_dict(orient='split')}")

def fix_misalignment(row):
    """
    """
    split_names = row['FirstName'].split(maxsplit=1) 

    row['BirthDate'], row['Department'], row['Salary'] = \
        row['LastName'], row['BirthDate'], row['Department']
    if re.compile(constants.DATE_PATTERNS).match(row['BirthDate']) == None:
        logging.error(f"Cannot fix suspected misalignment for row with EmployeeID {row['EmployeeID']}. {row['BirthDate']} does not match date format. Row will be deleted.")
        return pd.Series([np.nan]*len(row), index=row.index)
        
    if re.compile(r"\d+").match(row['Salary']) == None:
        logging.error(f"Cannot fix suspected misalignment for row with EmployeeID {row['EmployeeID']}. {row['Salary']} is not a valid number. Row will be deleted.")
        return pd.Series([np.nan]*len(row), index=row.index)

    row['FirstName'], row['LastName'] = split_names
    
    return row
    


def transform_data(data):
    """
    Perform specified transformations on the data.
    """
    data = data.map(lambda x: x.strip() if isinstance(x, str) else x)
    logging.info(f"Stripping trailing and leading white spaces in all values.")

    # Identifying rows where all values match the column names
    mask = (data == data.columns).all(axis=1)

    # Filtering out those rows
    data = data[~mask]
    logging.info(f"Removing rows that have column names as values.")

    # Clean First Names
    original_data = data.copy()
    data['FirstName'] = data['FirstName'].apply(lambda x: regex.sub(r'^[^\p{L}]+|[^\p{L}]+$', '', x, flags=re.UNICODE))
    log_change(original_data['FirstName'], data['FirstName'], 'FirstName cleaning')


    # Identify misaligned rows
    misaligned_mask = data['Salary'].isna()

    # Apply corrections and update dataframe
    data = data.apply(lambda row: fix_misalignment(row) if row.name in data.index[misaligned_mask] else row, axis=1)

    # Clean Last Names
    original_data = data.copy()
    data['LastName'] = data['LastName'].apply(lambda x: regex.sub(r'^[^\p{L}]+|[^\p{L}]+$', '', x, flags=re.UNICODE))
    log_change(original_data['LastName'], data['LastName'], 'LastName cleaning')

    original_data = data.copy()
    data['BirthDate'] = data['BirthDate'].apply(lambda x: re.sub(r'(\d{4}-\d{2}-\d{2}).*', r'\1', x))
    log_change(original_data['BirthDate'], data['BirthDate'], 'Birth date-Clean YYYYMMDD followed by random string is cleaned to YYYY-MM-DD')

    original_data = data.copy()
    data['BirthDate'] = data['BirthDate'].apply(lambda x: x.replace('.',''))
    log_change(original_data['BirthDate'], data['BirthDate'], 'Birth date-Clean, Decimal point removed.')

    data['BirthDate'] = pd.to_datetime(data['BirthDate'], format='%Y-%m-%d', errors='coerce')

    data['FullName'] = data['FirstName'] + ' ' + data['LastName']
    logging.info(f"Adding new column `FullName`")

    for index, row in data[data['BirthDate'].isna()].iterrows():
        logging.error(f"Deleting row with index {index}, EmployeeID {row['EmployeeID']}, because BirthDate is not a valid date.")
    data = data.dropna(subset=['BirthDate'])


    reference_date = pd.Timestamp('2023-01-01')

    data['Age'] = data['BirthDate'].apply(lambda x: int((reference_date-x).days / 365.2425))
    logging.info(f"Adding new column `Age`")

    data['BirthDate'] = data['BirthDate'].dt.strftime('%d/%m/%Y')
    logging.info(f"Changing birth date format to DD/MM/YYYY")

    data['Salary'] = pd.to_numeric(data['Salary'], errors='coerce')
    for index, row in data[data['Salary'].isna()].iterrows():
        logging.error(f"Deleting row with index {index}, EmployeeID {row['EmployeeID']}, because Salary is not numeric.")
    data = data.dropna(subset=['Salary'])


    bins = [0, 50000, 100000, float('inf')]
    labels = ['A', 'B', 'C']

    # Create new column SalaryBucket based on conditions
    data['SalaryBucket'] = pd.cut(data['Salary'], bins=bins, labels=labels, right=False)

    for index, row in data[data['SalaryBucket'].isna()].iterrows():
        logging.error(f"Deleting row with index {index}, EmployeeID {row['EmployeeID']}, because Salary is negative")
    data = data.dropna(subset=['SalaryBucket'])

    return data


def load_data(dataframe, db_name, collection_name):
    # client = pymongo.MongoClient("mongodb://localhost:27017/")
    client = pymongo.MongoClient("mongodb://db:27017")
    
    db = client[db_name]
    
    collection = db[collection_name]

    records = dataframe.to_dict('records')  # Convert DataFrame to dict
    collection.insert_many(records)

    collection.create_index([("EmployeeID", pymongo.ASCENDING)], unique=True)
    


if __name__ == '__main__':
    data = read_csv('employee_details.csv')
    data = transform_data(data)
    load_data(data, 'EmployeeManagement', 'Employees')