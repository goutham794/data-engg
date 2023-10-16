# To run
 - `mkdir app_logs`
 We need an `app_logs` directory, this folder would be bind mount to the container, so we can view generated logs locally.
  - `docker-compose up -d`

# To view the inserted data
  - `docker exec -it my_mongo mongosh`
 Now you get access to the mongo shell in the mongodb docker container.
  - `use EmployeeManagement`
  - `db.Employees.find()`
 The above command displays all inserted documents in the `Employees` collection.

# Logs
 - Look in app_logs/ folder to see the logs of cleaning and transformation done.

# Documentation

## Data Transformation and Cleaning
 - Column header names are stripped of trailing spaces
 - Stripping White Spaces in all columns.
 - Removing rows where values match the column header names.
 - Trailing and Leading non-alphabet characters are removed from the names.
 - Misaligned rows (values shifted by 1 column), due to merged first and last names, are fixed.
 - Birth date is cleaned (YYYY-MM-DD followed by random string is cleaned)
 - Period or decimal point found in Birth date is removed.


### Assumptions
 - Trailing and Leading non-alphabet characters are removed from the names. Non-alphabet characters inside the name are kept.
 - Rows containing salaries with any non-numeric characters or negative numbers are deleted.
