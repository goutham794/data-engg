DATA_FILE = "./employee_details.csv"
SALRAY_BUCKET_BINS = [0, 49999.999, 100000, float('inf')] #0-49999.999, 50000-100000, >100000 
SALARY_BUCKET_LABELS = ['A', 'B', 'C']
DB_NAME = "EmployeeManagement"
COLLECTION_NAME= "Employees"
DATE_PATTERNS = r"^\d{4}-\d{2}-\d{2}$"
MONGO_URL = "mongodb://db:27017"
REFERENCE_DATE = '2023-01-01'