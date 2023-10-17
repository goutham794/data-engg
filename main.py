import pandas as pd
import numpy as np
import regex
import re
import pymongo
import logging

import config

def read_csv(file_path):
    """
    Read a CSV file and return a Pandas DataFrame.
    """
    data = pd.read_csv(file_path)
    data.columns = data.columns.str.strip()
    if data.empty:
        logging.warning(f"The CSV file {file_path} is empty. No data to process.")
    return data


logging.basicConfig(filename='logs/data_transform.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def log_change(data_before, data_after, message):
    """
    Function to log the Cleaning done on data.
    """
    change = data_before.compare(data_after, result_names=('old','updated'))
    if not change.empty:
        logging.info(f"{message}: {change.to_dict(orient='split')}")

def fix_misalignment(row):
    """
    returns `row` whose alignment is fixed, if possible else row of NaNs
    """
    split_names = row['FirstName'].split(maxsplit=1) 

    row['BirthDate'], row['Department'], row['Salary'] = \
        row['LastName'], row['BirthDate'], row['Department']
    if re.compile(config.DATE_PATTERNS).match(row['BirthDate']) == None:
        logging.error(f"Cannot fix suspected misalignment for row with EmployeeID {row['EmployeeID']}. {row['BirthDate']} does not match date format. Row will be deleted.")
        return pd.Series([np.nan]*len(row), index=row.index)
        
    if re.compile(r"\d+").match(row['Salary']) == None:
        logging.error(f"Cannot fix suspected misalignment for row with EmployeeID {row['EmployeeID']}. {row['Salary']} is not a valid number. Row will be deleted.")
        return pd.Series([np.nan]*len(row), index=row.index)

    row['FirstName'], row['LastName'] = split_names
    
    return row
    

def clean_data(data):
    """ Function to perform cleaning tasks on data """
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

    return data

def remove_rows_with_na(data, column_name: str, log_message: str):
    na_mask = data[column_name].isna()
    # Log warning
    data[na_mask].apply(
    lambda row: logging.warning(
        f"Deleting row with index {row.name}, "
        f"EmployeeID {row['EmployeeID']}, "
        f"reason : {log_message}"
    ), axis=1
)
    # Drop the rows
    data = data[~na_mask]
    return data



def transform_data(data):
    """
    Perform specified cleaning and transformations on the data.
    """
    if data.empty:
        logging.warning("Received an empty DataFrame in transform_data(). No transformations will be applied.")
        return data

    data = clean_data(data)

    data['BirthDate'] = pd.to_datetime(data['BirthDate'], format='%Y-%m-%d', errors='coerce')

    # Remove rows with non-valid birth dates
    data = remove_rows_with_na(data, 'BirthDate',
                                "BirthDate is not a valid date.")

    data['FullName'] = data['FirstName'] + ' ' + data['LastName']
    logging.info(f"Adding new column `FullName`")

    reference_date = pd.Timestamp(config.REFERENCE_DATE)

    data['Age'] = data['BirthDate'].apply(lambda x: int((reference_date-x).days / 365.2425))
    logging.info(f"Adding new column `Age`")

    data['BirthDate'] = data['BirthDate'].dt.strftime('%d/%m/%Y')
    logging.info(f"Changing birth date format to DD/MM/YYYY")

    # After coerced conversion non-numneric Salaries become NaN
    data['Salary'] = pd.to_numeric(data['Salary'], errors='coerce')

    # Remove rows with non-numeric Salary
    data = remove_rows_with_na(data, 'Salary',
                                "Salary is not numeric")

    # Create new column SalaryBucket based on conditions, neg Salaries -> Nan
    data['SalaryBucket'] = pd.cut(data['Salary'], 
            bins=config.SALRAY_BUCKET_BINS, labels=config.SALARY_BUCKET_LABELS)

    # Remove rows with negative Salary
    data = remove_rows_with_na(data, 'SalaryBucket',
                                "Salary is not negative")
    
    data.drop(['FirstName', 'LastName', 'BirthDate'], axis=1, inplace=True)
    logging.info(f"Removing columns 'FirstName', 'LastName', 'BirthDate'")
    
    return data


def load_data(dataframe, db_name, collection_name):
    """
    Push records to mongodb db.
    """
    if dataframe.empty:
        logging.warning("Received an empty DataFrame in load_data(). No data will be inserted into the database.")
        return
    client = pymongo.MongoClient(config.MONGO_URL)
    db = client[db_name]
    collection = db[collection_name]
    records = dataframe.to_dict('records')  # Convert DataFrame to dict
    collection.insert_many(records)
    collection.create_index([("EmployeeID", pymongo.ASCENDING)], unique=True)
    


if __name__ == '__main__':
    data = read_csv(config.DATA_FILE)
    data = transform_data(data)
    load_data(data, config.DB_NAME, config.COLLECTION_NAME)