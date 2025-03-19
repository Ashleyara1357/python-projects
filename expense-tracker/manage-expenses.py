import csv
import os
import datetime
from tabulate import tabulate # type: ignore

# Constants
EXPENSES_FILE = "expenses.csv"
CATEGORIES = ["Food", "Transportation", "Housing", "Entertainment", "Utilities", "Healthcare", "Other"]
HEADERS = ["Date", "Amount", "Category", "Description"]

def initialize_expense_file():
    """Create the expenses CSV file if it doesn't exist."""
    if not os.path.exists(EXPENSES_FILE):
        with open(EXPENSES_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(HEADERS)
        print(f"✅ Created new expense tracker file: {EXPENSES_FILE}")
    else:
        print(f"✅ Using existing expense tracker file: {EXPENSES_FILE}")

def load_expenses():
    """Load expenses from CSV file."""
    if not os.path.exists(EXPENSES_FILE):
        return []
    
    expenses = []
    with open(EXPENSES_FILE, 'r', newline='') as file:
        for row in csv.DictReader(file):
            try:
                row["Amount"] = float(row["Amount"])
                expenses.append(row)
            except (ValueError, KeyError):
                continue
    return expenses

def save_expenses(expenses):
    """Save expenses to CSV file."""
    with open(EXPENSES_FILE, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(expenses)

def add_expense():
    """Add a new expense to the CSV file."""
    try:
        # Get date
        date = input("Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
        if not date:
            date = datetime.date.today().strftime('%Y-%m-%d')
        else:
            try:
                datetime.datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                print("❌ Invalid date format. Using today's date.")
                date = datetime.date.today().strftime('%Y-%m-%d')

        # Get amount
        while True:
            try:
                amount = float(input("Enter amount: $").strip())
                if amount <= 0:
                    print("❌ Amount must be greater than zero.")
                    continue
                break
            except ValueError:
                print("❌ Invalid amount. Please enter a number.")

        # Get category
        print("\nCategories:")
        for i, category in enumerate(CATEGORIES, 1):
            print(f"{i}. {category}")

        choice = input("\nSelect category number or type a custom category: ").strip()
        try:
            index = int(choice) - 1
            category = CATEGORIES[index] if 0 <= index < len(CATEGORIES) else choice
        except ValueError:
            category = choice

        description = input("Enter description: ").strip()

        # Save the expense
        expenses = load_expenses()
        expenses.append({
            "Date": date,
            "Amount": amount,
            "Category": category,
            "Description": description
        })
        save_expenses(expenses)
        print(f"✅ Expense of ${amount:.2f} added for {description} on {date}.")

    except Exception as e:
        print(f"❌ Error adding expense: {e}")

def view_expenses(filter_category=None, filter_month=None):
    """Display all expenses with optional filters."""
    expenses = load_expenses()
    if not expenses:
        print("❌ No expenses found.")
        return

    filtered_expenses = []
    total = 0

    for exp in expenses:
        if filter_category and exp["Category"].lower() != filter_category.lower():
            continue
        if filter_month and not exp["Date"].startswith(filter_month):
            continue
        filtered_expenses.append(exp)
        total += exp["Amount"]

    if not filtered_expenses:
        print("❌ No matching expenses found.")
        return
    
    # Format for display
    table_data = [[
        exp["Date"],
        f"${exp['Amount']:.2f}",
        exp["Category"],
        exp["Description"]
    ] for exp in filtered_expenses]

    print("\n📊 Expense List:")
    print(tabulate(table_data, headers=HEADERS, tablefmt="pretty"))
    print(f"\n💰 Total: ${total:.2f}")

def delete_expense():
    """Delete an expense by index."""
    expenses = load_expenses()
    if not expenses:
        print("❌ No expenses to delete.")
        return

    # Display expenses with index
    table_data = [[i + 1, exp["Date"], f"${exp['Amount']:.2f}", exp["Category"], exp["Description"]] 
                  for i, exp in enumerate(expenses)]
    print("\n📊 Current Expenses:")
    print(tabulate(table_data, headers=["#", "Date", "Amount", "Category", "Description"], tablefmt="pretty"))

    try:
        index = int(input("\nEnter the number of the expense to delete (or 0 to cancel): ")) - 1
        if index == -1:
            print("🛑 Deletion cancelled.")
            return
        
        if 0 <= index < len(expenses):
            deleted_expense = expenses.pop(index)
            save_expenses(expenses)
            print(f"✅ Deleted expense: ${deleted_expense['Amount']:.2f} for {deleted_expense['Description']}")
        else:
            print("❌ Invalid choice.")
    except ValueError:
        print("❌ Please enter a valid number.")

def calculate_summary():
    """Display expense summary by category."""
    expenses = load_expenses()
    if not expenses:
        print("❌ No expenses found.")
        return
    
    summary = {}
    for exp in expenses:
        category = exp["Category"]
        summary[category] = summary.get(category, 0) + exp["Amount"]

    table_data = [[cat, f"${amt:.2f}"] for cat, amt in sorted(summary.items())]
    
    print("\n📊 Expense Summary:")
    print(tabulate(table_data, headers=["Category", "Total"], tablefmt="pretty"))

def main():
    """Main function to run the expense tracker."""
    initialize_expense_file()

    menu_options = {
        '1': lambda: add_expense(),
        '2': lambda: view_expenses(),
        '3': lambda: view_expenses(filter_category=input("Enter category: ").strip()),
        '4': lambda: view_expenses(filter_month=input("Enter month (YYYY-MM): ").strip()),
        '5': lambda: delete_expense(),
        '6': lambda: calculate_summary(),
        '7': lambda: print("Goodbye! 👋") or True
    }

    while True:
        print("\n=== Expense Tracker ===")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. View Expenses by Category")
        print("4. View Expenses by Month")
        print("5. Delete Expense")
        print("6. View Summary")
        print("7. Exit")

        choice = input("\nEnter your choice: ").strip()
        action = menu_options.get(choice, lambda: print("❌ Invalid choice."))
        if action() is True:  # Exit condition
            break

if __name__ == "__main__":
    main()