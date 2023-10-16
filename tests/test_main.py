import pandas as pd
import unittest
from unittest.mock import MagicMock, patch

from main import read_csv, clean_data, transform_data, load_data
import test_utils

class TestCSVReading(unittest.TestCase):
    def test_read_csv(self):
        data = read_csv("employee_details.csv")
        self.assertIsInstance(data, pd.DataFrame)
        self.assertNotEqual(data.shape[0], 0)

class TestDataTransformation(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        """
        Initializing the test case with the mock data.
        `self.cleaned_data` is the output of `clean_data` function
        `self.transformed_data` is the final output of `transform_data` function
        Similarly, next two attributes are the expected outputs of clean and transform.
        """
        super().__init__(methodName)
        self.cleaned_data = transform_data(pd.DataFrame(test_utils.MOCK_DATA))
        self.transformed_data = transform_data(pd.DataFrame(test_utils.MOCK_DATA))
        self.expected_cleaned_output = pd.DataFrame(test_utils.MOCK_TRANSFORMED_DATA)
        self.expected_transformed_output = pd.DataFrame(test_utils.MOCK_TRANSFORMED_DATA)

    def test_name_cleaning(self):
        assert self.cleaned_data['FirstName'].equals(self.expected_cleaned_output['FirstName']), "First name cleaning error"
        assert self.cleaned_data['LastName'].equals(self.expected_cleaned_output['LastName']), "Last name cleaning error"

    def test_date_cleaning(self):
        assert self.transformed_data['BirthDate'].equals(self.expected_cleaned_output['BirthDate']), "Birth date cleaning error"

    def test_date_conversion(self):
        assert self.transformed_data['BirthDate'].equals(self.expected_transformed_output['BirthDate']), "Birthdate formatting error"
    
    def test_name_merging(self):
        assert self.transformed_data['FullName'].equals(self.expected_transformed_output['FullName']), "Birthdate formatting error"

    def test_age_calculation(self):
        assert self.transformed_data['Age'].equals(self.expected_transformed_output['Age']), "Age calculation wrong"

    def test_salary_bucket_allocation(self):
        assert self.transformed_data['SalaryBucket'].equals(self.expected_transformed_output['SalaryBucket']), "Salary buket allocation wrong"

class TestLoadData(unittest.TestCase):
    @patch('main.pymongo.MongoClient')
    def test_load_data(self, mock_mongo_client):
        
        # Configure the mock objects
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_mongo_client.return_value.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        
        # Call the function with the mock data
        test_df = pd.DataFrame(test_utils.MOCK_TRANSFORMED_DATA)
        load_data(test_df, 'EmployeeManagement',
                                  'Employees')
        
        # Assertions
        mock_mongo_client.assert_called_once_with("mongodb://db:27017")
        mock_db.__getitem__.assert_called_once_with("Employees")
        records = test_df.to_dict('records')
        mock_collection.insert_many.assert_called_once_with(records)

    

