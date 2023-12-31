MOCK_DATA_1 = {
    'EmployeeID': ['E001', 'E002', 'E003'],
    'FirstName': ['12@Alice', 'Bob', '  Charlie'],
    'LastName' : ['Smith', 'Taylor  ', 'Cooper23_3'],
    'BirthDate': ['1990-06-1.2', '1988-01-03', '1995-07-15@1'],
    'Department': ['Finance', 'HR', 'IT'],
    'Salary': ['50000', '100000', '47000']
}


MOCK_CLEANED_DATA_1 = {
    'EmployeeID': ['E001', 'E002', 'E003'],
    'FirstName': ['Alice', 'Bob', 'Charlie'],
    'LastName' : ['Smith', 'Taylor', 'Cooper'],
    'BirthDate': ['1990-06-12', '1988-01-03', '1995-07-15'],
    'Department': ['Finance', 'HR', 'IT'],
    'Salary': ['50000', '100000', '47000'],
}


MOCK_TRANSFORMED_DATA_1 = {
    'EmployeeID': ['E001', 'E002', 'E003'],
    'FullName': ['Alice Smith', 'Bob Taylor', 'Charlie Cooper'],
    'Department': ['Finance', 'HR', 'IT'],
    'Salary': ['50000', '100000', '47000'],
    'Age': [32, 34, 27],
    'SalaryBucket': ['B', 'B', 'A'],
}



MOCK_DATA_2 = {
    'EmployeeID': ['E004', 'E005', 'E006'],
    'FirstName': ['12@Alice', 'Bob', '  Charlie'],
    'LastName' : ['Smith', 'Taylor  ', 'Cooper23_3'],
    'BirthDate': ['1990-06-1.2', '1988-01-03', '1995-07-15@1'],
    'Department': ['Finance', 'HR', 'IT'],
    'Salary': ['55000', '90000', '47000']
}


MOCK_CLEANED_DATA_2 = {
    'EmployeeID': ['E004', 'E005', 'E006'],
    'FirstName': ['Alice', 'Bob', 'Charlie'],
    'LastName' : ['Smith', 'Taylor', 'Cooper'],
    'BirthDate': ['1990-06-12', '1988-01-03', '1995-07-15'],
    'Department': ['Finance', 'HR', 'IT'],
    'Salary': ['55000', '90000', '47000'],
}


MOCK_TRANSFORMED_DATA_2 = {
    'EmployeeID': ['E001', 'E002', 'E003'],
    'FullName': ['Alice Smith', 'Bob Taylor', 'Charlie Cooper'],
    'Department': ['Finance', 'HR', 'IT'],
    'Salary': ['55000', '90000', '47000'],
    'Age': [32, 34, 27],
    'SalaryBucket': ['B', 'B', 'A'],
}

