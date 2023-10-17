import pandas as pd
import pytest
from unittest.mock import MagicMock, patch

import sys
sys.path.append("../")
from main import read_csv, clean_data, transform_data, load_data
from tests import test_utils

MOCK_DATA_CLEANING_PARAMETERS = [
    (test_utils.MOCK_DATA_1, test_utils.MOCK_CLEANED_DATA_1),
    (test_utils.MOCK_DATA_2, test_utils.MOCK_CLEANED_DATA_2),
]
MOCK_DATA_TRANSFORM_PARAMETERS = [
    (test_utils.MOCK_DATA_1, test_utils.MOCK_TRANSFORMED_DATA_1),
    (test_utils.MOCK_DATA_2, test_utils.MOCK_TRANSFORMED_DATA_2),
]

@pytest.fixture(params=MOCK_DATA_CLEANING_PARAMETERS)
def cleaned_data(request):
    """Fixture to provide cleaned data and expected cleaned output."""
    input_data, expected_cleaned_output = request.param
    cleaned_output = clean_data(pd.DataFrame(input_data))
    return cleaned_output, pd.DataFrame(expected_cleaned_output)

@pytest.fixture(params=MOCK_DATA_TRANSFORM_PARAMETERS)
def transformed_data(request):
    """Fixture to provide transformed data and expected transformed output."""
    input_data, expected_transformed_output = request.param
    transformed_output = transform_data(pd.DataFrame(input_data))
    return transformed_output, pd.DataFrame(expected_transformed_output)

def test_read_csv():
    data = read_csv("tests/sample_csv.csv")
    assert isinstance(data, pd.DataFrame)
    # assert data.shape[0] != 0

def test_name_cleaning(cleaned_data):
    cleaned_output, expected_cleaned_output = cleaned_data
    assert cleaned_output['FirstName'].equals(expected_cleaned_output['FirstName']), "First name cleaning error"
    assert cleaned_output['LastName'].equals(expected_cleaned_output['LastName']), "Second name cleaning error"

def test_date_cleaning(cleaned_data):
    cleaned_output, expected_cleaned_output = cleaned_data
    assert cleaned_output ['BirthDate'].equals(expected_cleaned_output['BirthDate']), "Birth date cleaning error"

def test_date_conversion(transformed_data):
    transformed_output, expected_transformed_output  = transformed_data
    assert transformed_output['BirthDate'].equals(expected_transformed_output['BirthDate']), "Birthdate formatting error"

def test_name_merging(transformed_data):
    transformed_output, expected_transformed_output  = transformed_data
    assert transformed_output['FullName'].equals(expected_transformed_output['FullName']), "FullName merging error"

def test_age_calculation(transformed_data):
    transformed_output, expected_transformed_output  = transformed_data
    assert transformed_output['Age'].equals(expected_transformed_output['Age']), "Age calculation wrong"

def test_salary_bucket_allocation(transformed_data):
    transformed_output, expected_transformed_output  = transformed_data
    assert transformed_output['SalaryBucket'].astype(str).equals(expected_transformed_output['SalaryBucket']), "Salary bucket allocation wrong"

@patch('main.pymongo.MongoClient')
def test_load_data(mock_mongo_client):
    # Configure the mock objects
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_mongo_client.return_value.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection
    
    # Call the function with the mock data
    test_df = pd.DataFrame(test_utils.MOCK_TRANSFORMED_DATA_1)
    load_data(test_df, 'EmployeeManagement', 'Employees')
    
    # Assertions
    mock_mongo_client.assert_called_once_with("mongodb://db:27017")
    mock_db.__getitem__.assert_called_once_with("Employees")
    records = test_df.to_dict('records')
    mock_collection.insert_many.assert_called_once_with(records)
