import mysql.connector
import secrets

# Define your database connection details and connect
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