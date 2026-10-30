
import mysql.connector
from mysql.connector import Error
from decimal import Decimal, InvalidOperation


# Database Connection
def connect_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="140605",
            database="bank_db"
        )

        if conn.is_connected():
            print("Database Connected Successfully!")
            return conn

    except Error as e:
        print("Database Connection Error:", e)

    return None


# Bank Account Class
class BankAccount:

    def __init__(self, conn):
        self.__conn = conn

    # Create New Account
    def create_account(self):

        cursor = None

        try:
            account_no = int(input("Enter Account Number: "))
            name = input("Enter Customer Name: ").strip()
            amount = Decimal(input("Enter Initial Deposit: "))

            if not name:
                raise ValueError("Customer name cannot be empty.")

            if amount <= 0:
                raise ValueError("Initial deposit must be positive.")

            cursor = self.__conn.cursor()

            cursor.execute(
                """INSERT INTO accounts
                (account_no, customer_name, balance)
                VALUES (%s, %s, %s)""",
                (account_no, name, amount)
            )

            cursor.execute(
                """INSERT INTO transactions
                (account_no, transaction_type, amount, balance)
                VALUES (%s, %s, %s, %s)""",
                (account_no, "Initial Deposit", amount, amount)
            )

            self.__conn.commit()

            print("Account Created Successfully!")

        except (ValueError, InvalidOperation) as e:
            self.__conn.rollback()
            print("Invalid Input:", e)

        except Error as e:
            self.__conn.rollback()
            print("Database Error:", e)

        finally:
            if cursor:
                cursor.close()

    # Get Account Balance
    def check_balance(self):

        cursor = None

        try:
            account_no = int(input("Enter Account Number: "))

            cursor = self.__conn.cursor()

            cursor.execute(
                "SELECT customer_name, balance FROM accounts WHERE account_no=%s",
                (account_no,)
            )

            result = cursor.fetchone()

            if result:
                print("Customer Name:", result[0])
                print("Current Balance: Rs.", result[1])
            else:
                print("Account Not Found!")

        except ValueError:
            print("Enter a valid account number.")

        except Error as e:
            print("Database Error:", e)

        finally:
            if cursor:
                cursor.close()

    # Deposit Money
    def deposit(self):

        cursor = None

        try:
            account_no = int(input("Enter Account Number: "))
            amount = Decimal(input("Enter Deposit Amount: "))

            if amount <= 0:
                raise ValueError("Deposit amount must be positive.")

            cursor = self.__conn.cursor()

            cursor.execute(
                "SELECT balance FROM accounts WHERE account_no=%s FOR UPDATE",
                (account_no,)
            )

            result = cursor.fetchone()

            if not result:
                print("Account Not Found!")
                self.__conn.rollback()
                return

            balance = result[0]
            new_balance = balance + amount

            cursor.execute(
                "UPDATE accounts SET balance=%s WHERE account_no=%s",
                (new_balance, account_no)
            )

            cursor.execute(
                """INSERT INTO transactions
                (account_no, transaction_type, amount, balance)
                VALUES (%s, %s, %s, %s)""",
                (account_no, "Deposit", amount, new_balance)
            )

            self.__conn.commit()

            print("Amount Deposited Successfully!")
            print("New Balance: Rs.", new_balance)

        except (ValueError, InvalidOperation) as e:
            self.__conn.rollback()
            print("Invalid Input:", e)

        except Error as e:
            self.__conn.rollback()
            print("Database Error:", e)

        finally:
            if cursor:
                cursor.close()

    # Withdraw Money
    def withdraw(self):

        cursor = None

        try:
            account_no = int(input("Enter Account Number: "))
            amount = Decimal(input("Enter Withdrawal Amount: "))

            if amount <= 0:
                raise ValueError("Withdrawal amount must be positive.")

            cursor = self.__conn.cursor()

            cursor.execute(
                "SELECT balance FROM accounts WHERE account_no=%s FOR UPDATE",
                (account_no,)
            )

            result = cursor.fetchone()

            if not result:
                print("Account Not Found!")
                self.__conn.rollback()
                return

            balance = result[0]

            if amount > balance:
                print("Insufficient Balance!")
                self.__conn.rollback()
                return

            new_balance = balance - amount

            cursor.execute(
                "UPDATE accounts SET balance=%s WHERE account_no=%s",
                (new_balance, account_no)
            )

            cursor.execute(
                """INSERT INTO transactions
                (account_no, transaction_type, amount, balance)
                VALUES (%s, %s, %s, %s)""",
                (account_no, "Withdrawal", amount, new_balance)
            )

            self.__conn.commit()

            print("Withdrawal Successful!")
            print("Remaining Balance: Rs.", new_balance)

        except (ValueError, InvalidOperation) as e:
            self.__conn.rollback()
            print("Invalid Input:", e)

        except Error as e:
            self.__conn.rollback()
            print("Database Error:", e)

        finally:
            if cursor:
                cursor.close()

    # Calculate and Credit Simple Interest
    def calculate_interest(self):

        cursor = None

        try:
            account_no = int(input("Enter Account Number: "))

            rate = Decimal(input("Enter Annual Interest Rate (%): "))
            time = Decimal(input("Enter Time (Years): "))

            if rate < 0 or time <= 0:
                raise ValueError("Rate cannot be negative and time must be positive.")

            cursor = self.__conn.cursor()

            cursor.execute(
                "SELECT balance FROM accounts WHERE account_no=%s FOR UPDATE",
                (account_no,)
            )

            result = cursor.fetchone()

            if not result:
                print("Account Not Found!")
                self.__conn.rollback()
                return

            principal = result[0]

            interest = (principal * rate * time) / Decimal("100")
            interest = interest.quantize(Decimal("0.01"))

            new_balance = principal + interest

            cursor.execute(
                "UPDATE accounts SET balance=%s WHERE account_no=%s",
                (new_balance, account_no)
            )

            cursor.execute(
                """INSERT INTO transactions
                (account_no, transaction_type, amount, balance)
                VALUES (%s, %s, %s, %s)""",
                (account_no, "Interest", interest, new_balance)
            )

            self.__conn.commit()

            print("Interest Credited Successfully!")
            print("Interest Amount: Rs.", interest)
            print("New Balance: Rs.", new_balance)

        except (ValueError, InvalidOperation) as e:
            self.__conn.rollback()
            print("Invalid Input:", e)

        except Error as e:
            self.__conn.rollback()
            print("Database Error:", e)

        finally:
            if cursor:
                cursor.close()

    # Display Transaction History
    def transaction_history(self):

        cursor = None

        try:
            account_no = int(input("Enter Account Number: "))

            cursor = self.__conn.cursor()

            cursor.execute(
                """SELECT transaction_type, amount,
                transaction_date, balance
                FROM transactions
                WHERE account_no=%s
                ORDER BY transaction_id""",
                (account_no,)
            )

            records = cursor.fetchall()

            if not records:
                print("No Transaction History Found!")
                return

            print("\n========== TRANSACTION HISTORY ==========")

            for record in records:

                print("----------------------------------")
                print("Type:", record[0])
                print("Amount: Rs.", record[1])
                print("Date:", record[2])
                print("Balance: Rs.", record[3])

            print("----------------------------------")

        except ValueError:
            print("Enter a valid account number.")

        except Error as e:
            print("Database Error:", e)

        finally:
            if cursor:
                cursor.close()


# Main Program
def main():

    conn = connect_db()

    if conn is None:
        print("Unable to start Bank Management System.")
        return

    bank = BankAccount(conn)

    try:

        while True:

            print("\n================================")
            print("      BANK MANAGEMENT SYSTEM")
            print("================================")

            print("1. Create New Account")
            print("2. Check Account Balance")
            print("3. Deposit Money")
            print("4. Withdraw Money")
            print("5. Calculate Simple Interest")
            print("6. View Transaction History")
            print("7. Exit")

            try:
                choice = int(input("\nEnter Your Choice: "))

                if choice == 1:
                    bank.create_account()

                elif choice == 2:
                    bank.check_balance()

                elif choice == 3:
                    bank.deposit()

                elif choice == 4:
                    bank.withdraw()

                elif choice == 5:
                    bank.calculate_interest()

                elif choice == 6:
                    bank.transaction_history()

                elif choice == 7:
                    print("Thank You for Using Our Banking System!")
                    break

                else:
                    print("Invalid Choice! Select 1 to 7.")

            except ValueError:
                print("Please Enter a Valid Number!")

    except KeyboardInterrupt:
        print("\nApplication Interrupted.")

    finally:
        conn.close()
        print("Database Connection Closed.")


if __name__ == "__main__":
    main()
