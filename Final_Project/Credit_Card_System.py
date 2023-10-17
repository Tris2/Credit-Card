from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType
import mysql.connector
import secrets
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd
import requests


#Req 1.1 and 1.2

"""

Req-1.1
Data Extraction and Transformation with Python and 
PySpark
Functional Requirement 1.1
For “Credit Card System,” create a Python and PySpark SQL program to read/extract the following JSON files according to the specifications found in the mapping document.
 
1. CDW_SAPP_BRANCH.JSON
2. CDW_SAPP_CREDITCARD.JSON
3. CDW_SAPP_CUSTOMER.JSON

Note: Data Engineers will be required to transform the data based on the requirements found in the Mapping Document.

Hint: [You can use  PySQL “select statement query” or simple Pyspark RDD].
Req-1.2
Data loading into Database
Function Requirement 1.2
Once PySpark reads data from JSON files, and then utilizes Python, PySpark, and Python modules to load data into RDBMS(SQL), perform the following:
 
Create a Database in SQL(MySQL), named “creditcard_capstone.”
Create a Python and Pyspark Program to load/write the “Credit Card System Data” into RDBMS(creditcard_capstone).
Tables should be created by the following names in RDBMS:
CDW_SAPP_BRANCH
CDW_SAPP_CREDIT_CARD
CDW_SAPP_CUSTOMER 



"""

#Branch Schema
branch_schema = StructType([
    StructField("BRANCH_CODE", IntegerType(), True),
    StructField("BRANCH_NAME", StringType(), True),
    StructField("BRANCH_STREET", StringType(), True),
    StructField("BRANCH_CITY", StringType(), True),
    StructField("BRANCH_STATE", StringType(), True),
    StructField("BRANCH_ZIP", IntegerType(), True),
    StructField("BRANCH_PHONE", StringType(), True),
    StructField("LAST_UPDATED", TimestampType(), True)
])

spark = SparkSession.builder.appName("JsonExtraction").getOrCreate()

branch_data = spark.read.json("cdw_sapp_branch.json")

branch_data.createOrReplaceTempView("branch_data")

#Extracting the transformed Branch Data
transformed_branch_data = spark.sql("""
    SELECT
        CAST(BRANCH_CODE AS INT) AS BRANCH_CODE,
        BRANCH_NAME AS BRANCH_NAME,
        BRANCH_STREET AS BRANCH_STREET,
        BRANCH_CITY AS BRANCH_CITY,
        BRANCH_STATE AS BRANCH_STATE,
        CASE
            WHEN BRANCH_ZIP IS NULL THEN 99999
            ELSE CAST(BRANCH_ZIP AS INT)
        END AS BRANCH_ZIP,
        CASE
            WHEN BRANCH_PHONE RLIKE '\\d{10}'
            THEN CONCAT('(', SUBSTR(BRANCH_PHONE, 1, 3), ')', SUBSTR(BRANCH_PHONE, 4, 3), '-', SUBSTR(BRANCH_PHONE, 7, 4))
            ELSE BRANCH_PHONE
        END AS BRANCH_PHONE,
        LAST_UPDATED AS LAST_UPDATED
    FROM branch_data
""")



#Customer Schema

schema_customer = StructType([
    StructField("SSN", IntegerType(), True),
    StructField("FIRST_NAME", StringType(), True),
    StructField("MIDDLE_NAME", StringType(), True),
    StructField("LAST_NAME", StringType(), True),
    StructField("CREDIT_CARD_NO", StringType(), True),
    StructField("STREET_NAME", StringType(), True),
    StructField("APT_NO", StringType(), True),
    StructField("CUST_CITY", StringType(), True),
    StructField("CUST_STATE", StringType(), True),
    StructField("CUST_COUNTRY", StringType(), True),
    StructField("CUST_ZIP", IntegerType(), True),
    StructField("CUST_PHONE", StringType(), True),
    StructField("CUST_EMAIL", StringType(), True),
    StructField("LAST_UPDATED", TimestampType(), True)
])

#Reading json file with schema
customer_data = spark.read.schema(schema_customer).json("cdw_sapp_custmer.json") 

#Temp view for customer data
customer_data.createOrReplaceTempView("customer_data")

# Write SQL queries based on the qualified column names
transformed_customer_data = spark.sql("""
    SELECT
        CAST(customer_data.SSN AS INT) AS SSN,
        INITCAP(customer_data.FIRST_NAME) AS FIRST_NAME,
        LOWER(customer_data.MIDDLE_NAME) AS MIDDLE_NAME,
        INITCAP(customer_data.LAST_NAME) AS LAST_NAME,
        customer_data.CREDIT_CARD_NO AS Credit_card_no,
        CONCAT_WS(', ', customer_data.APT_NO, customer_data.STREET_NAME) AS FULL_STREET_ADDRESS,
        customer_data.CUST_CITY AS CUST_CITY,
        customer_data.CUST_STATE AS CUST_STATE,
        customer_data.CUST_COUNTRY AS CUST_COUNTRY,
        CAST(COALESCE(customer_data.CUST_ZIP, 99999) AS INT) AS CUST_ZIP,
        CASE
            WHEN customer_data.CUST_PHONE RLIKE '\\d{10}'
            THEN CONCAT('(', SUBSTR(customer_data.CUST_PHONE, 1, 3), ')', SUBSTR(customer_data.CUST_PHONE, 4, 3), '-', SUBSTR(customer_data.CUST_PHONE, 7, 4))
            ELSE customer_data.CUST_PHONE
        END AS CUST_PHONE,
        customer_data.CUST_EMAIL AS CUST_EMAIL,
        customer_data.LAST_UPDATED AS LAST_UPDATED
    FROM customer_data
""")



#Schema for Credit card
schema_credit_card = StructType([
    StructField("CUST_CC_NO", StringType(), True),
    StructField("TIMEID", StringType(), True),
    StructField("CUST_SSN", IntegerType(), True),
    StructField("BRANCH_CODE", IntegerType(), True),
    StructField("TRANSACTION_TYPE", StringType(), True),
    StructField("TRANSACTION_VALUE", DoubleType(), True),
    StructField("TRANSACTION_ID", IntegerType(), True)
])

# Read the JSON file with the defined schema
credit_card_data = spark.read.schema(schema_credit_card).json("cdw_sapp_credit.json")

# Create a temporary view for credit card data
credit_card_data.createOrReplaceTempView("credit_card_data")

# Write SQL queries based on the qualified column names
transformed_credit_card_data = spark.sql("""
    SELECT
        CUST_CC_NO AS CUST_CC_NO,
        TIMEID AS TIMEID,
        CAST(CUST_SSN AS INT) AS CUST_SSN,
        CAST(BRANCH_CODE AS INT) AS BRANCH_CODE,
        TRANSACTION_TYPE AS TRANSACTION_TYPE,
        CAST(TRANSACTION_VALUE AS DOUBLE) AS TRANSACTION_VALUE,
        CAST(TRANSACTION_ID AS INT) AS TRANSACTION_ID
    FROM credit_card_data
""")



spark = SparkSession.builder.appName("CreditCardSystemLoader").getOrCreate()

# Load the transformed data into DataFrames (replace with your DataFrames)
branch_data = transformed_branch_data
credit_card_data = transformed_credit_card_data
customer_data = transformed_customer_data


db = mysql.connector.connect(
    host = "localhost",
    user = secrets.mysql_username,
    passwd = secrets.mysql_password,
    database = "creditcard_capstone" #Database in mysql

)




# Write DataFrames to MySQL tables using the existing MySQL connection
branch_data.write \
    .format("jdbc") \
    .option("url", "jdbc:mysql://localhost:3306/creditcard_capstone") \
    .option("dbtable", "CDW_SAPP_BRANCH") \
    .option("mode", "overwrite") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("user", secrets.mysql_username) \
    .option("password", secrets.mysql_password) \
    .save()
credit_card_data.write \
    .format("jdbc") \
    .option("url", "jdbc:mysql://localhost:3306/creditcard_capstone") \
    .option("dbtable", "CDW_SAPP_CREDIT_CARD") \
    .option("mode", "overwrite") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("user", secrets.mysql_username) \
    .option("password", secrets.mysql_password) \
    .save()
customer_data.write \
    .format("jdbc") \
    .option("url", "jdbc:mysql://localhost:3306/creditcard_capstone") \
    .option("dbtable", "CDW_SAPP_CUSTOMER") \
    .option("mode", "overwrite") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("user", secrets.mysql_username) \
    .option("password", secrets.mysql_password) \
    .save()
# Stop the Spark session
spark.stop()
# Close the MySQL connection
db.close()



#Req 2.1

"""
Once data is loaded into the database, we need a front-end (console) to see/display data. For that, create a console-based Python program to satisfy System Requirements 2 (2.1 and 2.2). 
 2.1 Transaction Details Module

Req-2.1

Transaction Details Module
Functional Requirements 2.1
1)    Used to display the transactions made by customers living in a given zip code for a given month and year. Order by day in descending order.
2)    Used to display the number and total values of transactions for a given type.
3)    Used to display the total number and total values of transactions for branches in a given state.



"""

# Define database connection details
db = mysql.connector.connect(
    host = "localhost",
    user = secrets.mysql_username,
    passwd = secrets.mysql_password,
    database = "creditcard_capstone" #Database in mysql

)
cursor = db.cursor()
# Function to display transactions by zip code, month, and year
def display_transactions_by_zip_month_year(zip_code, month, year):
    # SQL query to retrieve transactions by zip code, month, and year
    query = """
    SELECT * FROM CDW_SAPP_CREDIT_CARD
    WHERE YEAR(TIMEID) = %s AND MONTH(TIMEID) = %s AND CUST_ZIP = %s
    ORDER BY TIMEID DESC;
    """
    cursor.execute(query, (year, month, zip_code))
    transactions = cursor.fetchall()
    # Display the results
    print("Transactions by Zip Code, Month, and Year:")
    for transaction in transactions:
        print(transaction)
# Function to display number and total values of transactions for a given type
def display_transactions_by_type(transaction_type):
    # SQL query to retrieve transactions by type
    query = """
    SELECT COUNT(*) AS transaction_count, SUM(TRANSACTION_VALUE) AS total_value
    FROM CDW_SAPP_CREDIT_CARD
    WHERE TRANSACTION_TYPE = %s;
    """
    cursor.execute(query, (transaction_type,))
    result = cursor.fetchone()
    # Display the results
    print("Number of Transactions by Type:", result[0])
    print("Total Value of Transactions by Type:", result[1])
# Function to display total number and total values of transactions for branches in a given state
def display_transactions_by_state(branch_state):
    # SQL query to retrieve transactions by state
    query = """
    SELECT BRANCH_CODE, COUNT(*) AS transaction_count, SUM(TRANSACTION_VALUE) AS total_value
    FROM CDW_SAPP_CREDIT_CARD
    WHERE BRANCH_CODE IN (
        SELECT BRANCH_CODE FROM CDW_SAPP_BRANCH WHERE BRANCH_STATE = %s
    )
    GROUP BY BRANCH_CODE;
    """
    cursor.execute(query, (branch_state,))
    results = cursor.fetchall()
    # Display the results
    print("Transactions by State:", branch_state)
    for result in results:
        print("Branch Code:", result[0])
        print("Number of Transactions:", result[1])
        print("Total Value of Transactions:", result[2])
# Main program
if __name__ == "__main":
    while True:
        print("Transaction Details Module:")
        print("1. Display Transactions by Zip Code, Month, and Year")
        print("2. Display Number and Total Values of Transactions by Type")
        print("3. Display Total Number and Total Values of Transactions by Branch State")
        print("4. Quit")
        choice = input("Enter your choice: ")
        if choice == "1":
            zip_code = input("Enter Zip Code: ")
            month = input("Enter Month (numeric): ")
            year = input("Enter Year (YYYY): ")
            display_transactions_by_zip_month_year(zip_code, month, year)
        elif choice == "2":
            transaction_type = input("Enter Transaction Type: ")
            display_transactions_by_type(transaction_type)
        elif choice == "3":
            branch_state = input("Enter Branch State: ")
            display_transactions_by_state(branch_state)
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please enter a valid option.")
    # Close the database connection
    cursor.close()
    db.close()


#Req 2.2

"""
2.2 Customer Details Module

Req-2.2

Customer Details
Functional Requirements 2.2
1) Used to check the existing account details of a customer.
2) Used to modify the existing account details of a customer.
3) Used to generate a monthly bill for a credit card number for a given month and year.
4) Used to display the transactions made by a customer between two dates. Order by year, month, and day in descending order.

"""
# Define database connection details and connect
db = mysql.connector.connect(
    host = "localhost",
    user = secrets.mysql_username,
    passwd = secrets.mysql_password,
    database = "creditcard_capstone" #Database in mysql
)
cursor = db.cursor()
# Function to check existing account details of a customer
def check_customer_details(customer_id):
    # SQL query to retrieve customer details
    query = "SELECT * FROM CDW_SAPP_CUSTOMER WHERE SSN = %s"
    cursor.execute(query, (customer_id,))
    customer_details = cursor.fetchone()
    # Display customer details
    if customer_details:
        print("Customer Details:")
        print("SSN:", customer_details[0])
        print("First Name:", customer_details[1])
        print("Last Name:", customer_details[2])
        print("Street Address:", customer_details[3])
        print("City:", customer_details[4])
        print("State:", customer_details[5])
        print("Country:", customer_details[6])
        print("ZIP:", customer_details[7])
        print("Phone:", customer_details[8])
        print("Email:", customer_details[9])
    else:
        print("Customer not found.")
# Function to modify existing account details of a customer
def modify_customer_details(customer_id, new_email):
    # SQL query to update customer email
    query = "UPDATE CDW_SAPP_CUSTOMER SET CUST_EMAIL = %s WHERE SSN = %s"
    cursor.execute(query, (new_email, customer_id))
    db.commit()
    print("Customer email updated successfully.")
# Function to generate a monthly bill for a credit card
def generate_monthly_bill(credit_card_number, month, year):
    # SQL query to retrieve monthly bill details
    query = """
    SELECT * FROM CDW_SAPP_CREDIT_CARD
    WHERE YEAR(TIMEID) = %s AND MONTH(TIMEID) = %s AND CUST_CC_NO = %s
    ORDER BY TIMEID DESC;
    """
    cursor.execute(query, (year, month, credit_card_number))
    monthly_bill = cursor.fetchall()
    # Display the monthly bill
    if monthly_bill:
        print("Monthly Bill for Credit Card Number:", credit_card_number)
        for transaction in monthly_bill:
            print(transaction)
    else:
        print("No transactions found for the specified month and year.")
# Function to display customer transactions between two dates
def display_transactions_between_dates(customer_id, start_date, end_date):
    # SQL query to retrieve transactions between two dates
    query = """
    SELECT * FROM CDW_SAPP_CREDIT_CARD
    WHERE TIMEID BETWEEN %s AND %s AND CUST_CC_NO = %s
    ORDER BY TIMEID DESC;
    """
    cursor.execute(query, (start_date, end_date, customer_id))
    transactions = cursor.fetchall()
    # Display transactions
    if transactions:
        print("Transactions between", start_date, "and", end_date)
        for transaction in transactions:
            print(transaction)
    else:
        print("No transactions found between the specified dates.")
# Main program
if __name__ == "__main":
    while True:
        print("Customer Details Module:")
        print("1. Check Customer Details")
        print("2. Modify Customer Email")
        print("3. Generate Monthly Bill")
        print("4. Display Customer Transactions Between Two Dates")
        print("5. Quit")
        choice = input("Enter your choice: ")
        if choice == "1":
            customer_id = input("Enter Customer SSN: ")
            check_customer_details(customer_id)
        elif choice == "2":
            customer_id = input("Enter Customer SSN: ")
            new_email = input("Enter New Email: ")
            modify_customer_details(customer_id, new_email)
        elif choice == "3":
            credit_card_number = input("Enter Credit Card Number: ")
            month = input("Enter Month (numeric): ")
            year = input("Enter Year (YYYY): ")
            generate_monthly_bill(credit_card_number, month, year)
        elif choice == "4":
            customer_id = input("Enter Customer SSN: ")
            start_date = input("Enter Start Date (YYYYMMDD): ")
            end_date = input("Enter End Date (YYYYMMDD): ")
            display_transactions_between_dates(customer_id, start_date, end_date)
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please enter a valid option.")
    # Close the database connection
    cursor.close()
    db.close()




#Req 3.1

"""
Req - 3
 Data Analysis and Visualization
Functional Requirements 3.1
Find and plot which transaction type has the highest transaction count.
Note: Save a copy of the visualization to a folder in your github, making sure it is PROPERLY NAMED! 



"""

# Define your database connection details
db = mysql.connector.connect(
    host = "localhost",
    user = secrets.mysql_username,
    passwd = secrets.mysql_password,
    database = "creditcard_capstone" #Database in mysql
)

# SQL query to find transaction type with the highest transaction count
query = """
SELECT TRANSACTION_TYPE, COUNT(*) AS transaction_count
FROM CDW_SAPP_CREDIT_CARD
GROUP BY TRANSACTION_TYPE
ORDER BY transaction_count DESC
LIMIT 1;
"""
# Execute the query and retrieve data
cursor = db.cursor()
cursor.execute(query)
result = cursor.fetchone()
# Extract transaction type and count
transaction_type = result[0]
transaction_count = result[1]
# Plot the result
plt.figure(figsize=(8, 6))
plt.bar(transaction_type, transaction_count)
plt.xlabel("Transaction Type")
plt.ylabel("Transaction Count")
plt.title("Transaction Type with the Highest Transaction Count")
plt.tight_layout()
# Save the visualization to a folder in your GitHub repository with a proper name
plt.savefig("path_to_github_repo/transaction_type_highest_count.png")
plt.show()
# Close the database connection
cursor.close()
db.close()


#Req 3.2

"""
Functional Requirements 3.2
Find and plot which state has a high number of customers.

Note: Save a copy of the visualization to a folder in your github, making sure it is PROPERLY NAMED!

"""

# SQL query to find the state with a high number of customers
query = """
SELECT CUST_STATE, COUNT(*) AS customer_count
FROM CDW_SAPP_CUSTOMER
GROUP BY CUST_STATE
ORDER BY customer_count DESC
LIMIT 1;
"""
# Execute the query and retrieve data
cursor = db.cursor()
cursor.execute(query)
result = cursor.fetchone()
# Extract state and customer count
state = result[0]
customer_count = result[1]
# Plot the result
plt.figure(figsize=(8, 6))
plt.bar(state, customer_count)
plt.xlabel("State")
plt.ylabel("Customer Count")
plt.title("State with a High Number of Customers")
plt.tight_layout()
# Save the visualization to a folder in your GitHub repository with a proper name
plt.savefig("path_to_github_repo/state_high_customer_count.png")
plt.show()
# Close the database connection
cursor.close()
db.close()


#Req 3.3

"""
Functional Requirements 3.3
Find and plot the sum of all transactions for the top 10 customers, and which customer has the highest transaction amount.
Hint (use CUST_SSN). 

Note: Save a copy of the visualization to a folder in your github, making sure it is PROPERLY NAMED!


"""

# SQL query to find the top 10 customers with the highest transaction amounts
query = """
SELECT CUST_SSN, SUM(TRANSACTION_VALUE) AS total_transaction_amount
FROM CDW_SAPP_CREDIT_CARD
GROUP BY CUST_SSN
ORDER BY total_transaction_amount DESC
LIMIT 10;
"""
# Execute the query and retrieve data
cursor = db.cursor()
cursor.execute(query)
result = cursor.fetchall()
# Extract data into separate lists
customer_ssns = [row[0] for row in result]
transaction_amounts = [row[1] for row in result]
# Plot the result
plt.figure(figsize=(10, 6))
plt.bar(customer_ssns, transaction_amounts)
plt.xlabel("Customer SSN")
plt.ylabel("Total Transaction Amount")
plt.title("Top 10 Customers with Highest Transaction Amount")
plt.xticks(rotation=45)
plt.tight_layout()
# Save the visualization to a folder in your GitHub repository with a proper name
plt.savefig("path_to_github_repo/top_10_customers_transaction_amount.png")
plt.show()
# Close the database connection
cursor.close()
db.close()



#Req 4.1, 4.2, 4.3

"""
4. Functional Requirements - LOAN Application Dataset
Req-4
 Access to Loan API Endpoint
Functional Requirements 4.1
Create a Python program to GET (consume) data from the above API endpoint for the loan application dataset.
Functional Requirements 4.2
Find the status code of the above API endpoint.

Hint: status code could be 200, 400, 404, 401.
Functional Requirements 4.3
Once Python reads data from the API, utilize PySpark to load data into RDBMS (SQL). The table name should be CDW-SAPP_loan_application in the database.

Note: Use the “creditcard_capstone” database.

"""

# API endpoint for the loan application dataset
api_url = "https://raw.githubusercontent.com/platformps/LoanDataset/main/loan_data.json"
# Database connection configuration
db = mysql.connector.connect(
    host = "localhost",
    user = secrets.mysql_username,
    passwd = secrets.mysql_password,
    database = "creditcard_capstone" #Database in mysql
)
# Send a GET request to the API endpoint
response = requests.get(api_url)
# Check if the request was successful (status code 200)
if response.status_code == 200:
    loan_data = response.json()
    # Create a cursor to execute SQL commands
    cursor = db.cursor()
    # Define the table schema for CDW_SAPP_loan_application
    create_table_query = """
    CREATE TABLE IF NOT EXISTS CDW_SAPP_loan_application (
        Application_ID VARCHAR(20) PRIMARY KEY,
        Gender VARCHAR(10),
        Married VARCHAR(10),
        Dependents VARCHAR(10),
        Education VARCHAR(20),
        Self_Employed VARCHAR(10),
        Credit_History INT,
        Property_Area VARCHAR(20),
        Income VARCHAR(20),
        Application_Status VARCHAR(10)
    );
    """
    # Create the CDW-SAPP_loan_application table if it doesn't exist
    cursor.execute(create_table_query)
    # Insert data into the table
    insert_query = """
    INSERT INTO CDW_SAPP_loan_application (
        Application_ID, Gender, Married, Dependents, Education, Self_Employed,
        Credit_History, Property_Area, Income, Application_Status
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    # Iterate through the loan data and insert it into the database
    for record in loan_data:
        data_tuple = (
            record["Application_ID"],
            record["Gender"],
            record["Married"],
            record["Dependents"],
            record["Education"],
            record["Self_Employed"],
            record["Credit_History"],
            record["Property_Area"],
            record["Income"],
            record["Application_Status"],
        )
        cursor.execute(insert_query, data_tuple)
    # Commit the changes and close the cursor and database connection
    db.commit()
    cursor.close()
    db.close()
    print("Loan data loaded into the RDBMS.")
else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")


#Req 5.1

"""
Req-5
Data Analysis and Visualization
Functional Requirements 5.1
Find and plot the percentage of applications approved for self-employed applicants.
Note: Save a copy of the visualization to a folder in your github, making sure it is PROPERLY NAMED!


"""

# Load data from your MySQL database into a Pandas DataFrame
db = mysql.connector.connect(
    host = "localhost",
    user = secrets.mysql_username,
    passwd = secrets.mysql_password,
    database = "creditcard_capstone" #Database in mysql
)
query = "SELECT * FROM CDW_SAPP_loan_application"
loan_data = pd.read_sql(query, db)
# Filter self-employed applicants
self_employed_applicants = loan_data[loan_data['Self_Employed'] == 'Yes']
# Calculate the percentage of approved applications among self-employed applicants
approved_percentage = (self_employed_applicants['Application_Status'] == 'Y').mean() * 100
# Create a bar chart
plt.bar(['Self-Employed'], [approved_percentage])
plt.ylabel('Percentage Approved')
plt.title('Percentage of Applications Approved for Self-Employed Applicants')
# Save the visualization to a folder in your GitHub repository
#plt.savefig('path/to/your/github/repository/self_employed_approval.png')


#Req 5.2

"""
Functional Requirements 5.2
Find the percentage of rejection for married male applicants.
Note: Save a copy of the visualization to a folder in your github, making sure it is PROPERLY NAMED!

"""

# Filter married male applicants
married_male_applicants = loan_data[(loan_data['Gender'] == 'Male') & (loan_data['Married'] == 'Yes')]
# Calculate the percentage of rejection among married male applicants
rejection_percentage = (married_male_applicants['Application_Status'] == 'N').mean() * 100
# Create a bar chart
plt.bar(['Married Male'], [rejection_percentage])
plt.ylabel('Percentage Rejected')
plt.title('Percentage of Rejection for Married Male Applicants')
# Save the visualization to a folder in your GitHub repository
#plt.savefig('path/to/your/github/repository/married_male_rejection.png')



#Req 5.3

"""
Functional Requirements 5.3
Find and plot the top three months with the largest volume of transaction data.
Note: Save a copy of the visualization to a folder in your github, making sure it is PROPERLY NAMED!

"""

# Assuming your dataset has a date column named 'Application_Date'
loan_data['Application_Date'] = pd.to_datetime(loan_data['Application_Date'])
# Calculate the count of applications for each month
monthly_counts = loan_data.groupby(loan_data['Application_Date'].dt.to_period('M')).size()
# Select the top three months with the largest volume
top_three_months = monthly_counts.nlargest(3)
# Create a bar chart
top_three_months.plot(kind='bar')
plt.xlabel('Month')
plt.ylabel('Number of Applications')
plt.title('Top Three Months with Largest Volume of Applications')
# Save the visualization to a folder in your GitHub repository
#plt.savefig('path/to/your/github/repository/top_three_months.png')