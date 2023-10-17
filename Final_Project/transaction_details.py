import mysql.connector
import secrets
# Define your database connection details
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