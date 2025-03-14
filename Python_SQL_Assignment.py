#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 13 10:49:21 2025

@author: dominicraven
"""

#STAGE 1: Set up Database

# Import libararies: 
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import re #regex formatting for salary inputs

# Connect to database
conn = sqlite3.connect("Company_Assignment.db")
cursor = conn.cursor()


# Step 1: Create Departments table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
)
""")



'''
Fetch department IDs and map them to the names of each department.
The names act as the "key", and the Id as the associated value 

Code defined as a function as I will need to update the department dictionary 
whenever a new department is added.
Expanded function to only accept valid table_names. 
The end-user does not have a way to input into the mapping function, minimising risk of SQL injection.
'''
def map_id_name(table_name):
    # Ensure table_name is validated (for typos) and predefined
    valid_tables = {"departments", "employees"}  
    
    if table_name not in valid_tables:
        raise ValueError("Invalid table name")

    query = f"SELECT id, name FROM {table_name}"
    cursor.execute(query)
    table_dict = {name: dept_id for dept_id, name in cursor.fetchall()}
    return table_dict


# Create employees table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    department TEXT,
    salary REAL
)
""")

# Insert set of default departments

'''
* Check if the departments table is empty
* Need to ensure the following code only runs when empty or else it will 
  use up an additional four department Ids each time the code is run, 
  messing up the neat autoindexing
'''
cursor.execute("SELECT COUNT(*) FROM departments")
row_count = cursor.fetchone()[0]

if row_count == 0:
    # Table is empty so insert default departments
    departments = [("HR",), ("IT",), ("Finance",), ("Marketing",)]
    cursor.executemany("INSERT OR IGNORE INTO departments (name) VALUES (?)", departments)
    conn.commit()
    print("Departments inserted successfully!")

# Call mapping function on departments table to create dictionary
departments_dict = map_id_name("departments")

# Insert set of default employees with department keys to show code works
# departments_dict["HR"] returns the mapped ID of the department
employees_initial = [
    ("Alice", 30, departments_dict["HR"], 50000),
    ("Bob", 25, departments_dict["IT"], 60000),
    ("Charlie", 35, departments_dict["Finance"], 70000),
    ("David", 28, departments_dict["Marketing"], 55000)
]

# Check if the employees table is empty
cursor.execute("SELECT COUNT(*) FROM employees")
row_count = cursor.fetchone()[0]

if row_count == 0:
    # Table is empty, so insert new data
    cursor.executemany("INSERT INTO employees (name, age, department, salary) VALUES (?, ?, ?, ?)", employees_initial)
    conn.commit()
    print("Employees inserted successfully!")

# Call mapping function on departments table to create dictionary
employees_dict = map_id_name("employees")


# will need to define functions to check if inputted values are as expected.
# checks will be run at multiple points so making into functions is helpful.
''' Regex formating is used in the salary checker to ensure the input string
contains only a valid 2 digit number, before it will be converted to a float'''
def check_salary(salary):
    if not re.match(r'^\d+(\.\d{1,2})?$', salary) or float(salary) <= 0:
        return False
    
    # If passes checks, convert to float with 2 decimal places
    salary = round(float(salary), 2)
    return salary




# STAGE 2: Implement CRUD


# 1. Add new Department


def add_department():
    new_d = input("Enter new Department name, press space to cancel: ")
    if new_d:
        print(new_d)
        
        # push user inputs to departments table
        cursor.execute("INSERT INTO departments (name) VALUES (?)", (new_d,))                    
        conn.commit()
        print(f"\nDepartment {new_d} added successfully!\n")     
        
        # Recall mapping function to update dictionary
        updated_departments_dict = map_id_name("departments")
        # print(updated_departments_dict)
        # Return the updated dictionary
        return updated_departments_dict
    else:
        return None  # Return None as no changes were made
    



# 2. Add New Employee
def add_employee():
    name = input("Enter name: ")
    
    age = input("Enter age: ") 
    # Check valid Age is entered
    while not age.isnumeric() or int(age) <= 18 or int(age) > 100:
        age = input("Enter valid age: ")
    age = int(age)
        
    department = input("Enter department: ")
    # Check valid department ID is entered
    while not department.isnumeric() or int(department) not in departments_dict.values():
        department = input("Enter valid department: ")

    salary = input("Enter salary: ")
    # Check valid salary is entered
    check_salary(salary)
    
    while not check_salary(salary):
        salary = input("Enter valid salary: ")
        check_salary(salary)
    # If passes the checks, running function to return the float
    salary = check_salary(salary)


    # push user inputs to employee table
    cursor.execute("INSERT INTO employees (name, age, department, salary) VALUES (?, ?, ?, ?)",
                   (name, age, department, salary))
    conn.commit()
    print(f"\nEmployee {name} added successfully!\n")
    
    # Recall mapping function to update employees dict
    updated_employees_dict = map_id_name("employees")

    # Return the updated dictionary
    return updated_employees_dict


def view_employees():
    cursor.execute("""SELECT employees.*, departments.name
                   FROM employees
                   JOIN departments
				   ON departments.id = employees.department """)
    employees = cursor.fetchall()

    if not employees:
        print("\nNo employees found.\n")
    else:
        print("\nEmployee List:")
        for emp in employees:
            print(emp)
    print()

def update_employee():
    emp_id = input("Enter Employee ID to update, or 0 to cancel: ")
    
    # Check valid id is entered
    while not emp_id.isnumeric(): #or int(emp_id) <= 18 or int(emp_id) > 100:
        emp_id = input("Enter valid Id: ")
    emp_id = int(emp_id)
    cursor.execute("SELECT * FROM employees WHERE id = ?", (emp_id,))
    employee = cursor.fetchone()

    cursor.execute("SELECT * FROM employees WHERE id = ?", (emp_id,))
    employee = cursor.fetchone()

    if not employee:
        print("\nEmployee not found!\n")
        return None

    print("\nUpdating Employee:", employee)

    name = input("Enter new name (or press Enter to keep the same): ") or employee[1]
    age = input("Enter new age (or press Enter to keep the same): ")
    if age:
        while not age.isnumeric() or int(age) <= 18 or int(age) > 100:
            age = input("Enter valid age: ")
    else:
        age = employee[2]
    age = int(age)

    department = input("Enter new department (or press Enter to keep the same): ") or employee[3]
    while not department.isnumeric() or int(department) not in departments_dict.values():
        department = input("Enter valid department: ")

    
    salary = input("Enter new salary (or press Enter to keep the same): ")
    if salary:
        while not check_salary(salary):
                salary = input("Enter valid salary (up to two decimal places): ")
                check_salary(salary)
        salary = check_salary(salary)
    else:
        salary = employee[4]  # Default to the existing salary if not input
    

    cursor.execute("UPDATE employees SET name = ?, age = ?, department = ?, salary = ? WHERE id = ?",
                   (name, age, department, salary, emp_id))
    conn.commit()
    print(f"\nEmployee ID {emp_id} updated successfully!\n")
    
    # Recall mapping function to update employees dict
    updated_employees_dict = map_id_name("employees")

    # Return the updated dictionary
    return updated_employees_dict

def delete_employee():
    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()
    print("\nEmployee List:")
    for emp in employees:
        print(emp)
    print()
    
    emp_id = input("Enter Employee ID to delete, or 0 to cancel: ")
    
    # Check valid id is entered
    while not emp_id.isnumeric(): #or int(emp_id) <= 18 or int(emp_id) > 100:
        emp_id = input("Enter valid Id: ")
    emp_id = int(emp_id)
    cursor.execute("SELECT * FROM employees WHERE id = ?", (emp_id,))
    employee = cursor.fetchone()


    if not employee:
        print("\nEmployee not found!\n")
        return None
    
    confirm = input(f"Are you sure you want to delete {employee[1]}? (yes/no): ").lower()
    if confirm == "yes":
        cursor.execute("DELETE FROM employees WHERE id = ?", (emp_id,))
        conn.commit()
        print(f"\nEmployee ID {emp_id} deleted successfully!\n")
        
        # Recall mapping function to update employees dict
        updated_employees_dict = map_id_name("employees")

        # Return the updated dictionary
        return updated_employees_dict
    
    else:
        print("\nDelete action canceled.\n")
        return None


def plot_barchart():
    # Step 1: Connect to the database and fetch data
    cursor.execute("""SELECT employees.*, departments.name
                   FROM employees
                   JOIN departments
				   ON departments.id = employees.department """)

    #cursor.execute("SELECT * FROM employees")
    rows = cursor.fetchall()
    


    # Convert to Pandas dataFrame
    df = pd.DataFrame(rows, columns=["id", "name", "age", "department Id", "salary", "department"])
    #print(df.head())

    department_counts = df["department"].value_counts()
    print("\nNumber of Employees per Department:")
    print(department_counts)
    
    # Plot the barchart
    plt.figure(figsize=(8, 5))
    department_counts.plot(kind="bar", color="skyblue")
    plt.title("Number of Employees per Department")
    plt.xlabel("Department")
    plt.ylabel("Number of Employees")
    plt.xticks(rotation=45)
    plt.grid(axis="y", linestyle="--", alpha=1)
    plt.savefig('Number of Employees per Department.jpg')
    plt.show()
    print(f"\nBarchart plotted successfully!\n")





# Menu function
def menu():
    # Reference the global dictionary variables so that any changes arent locked to a local function
    global departments_dict  
    global employees_dict 
    
    while True:
        print("\nEmployee Management System")
        print("1. Add Department")
        print("2. Add Employee")
        print("3. View Employees")
        print("4. Update Employee")
        print("5. Delete Employee")
        print("6. Show Employee Count by Department")
        print("7. Exit")

        choice = input("Enter your choice: ")
        
        if choice == "1":
            updated_dict1 = add_department()
            if updated_dict1:
                departments_dict = updated_dict1  # Update the global departments_dict
        elif choice == "2":
            updated_dict2 = add_employee()
            if updated_dict2:
                employees_dict = updated_dict2  # Update the global employees_dict
        elif choice == "3":
            view_employees()
        elif choice == "4":
            updated_dict4 = update_employee()
            if updated_dict4:
                employees_dict = updated_dict4  # Update the global employees_dict
        elif choice == "5":
            updated_dict5 = delete_employee()
            if updated_dict5:
                employees_dict = updated_dict5  # Update the global employees_dict
        elif choice == "6":
            plot_barchart()
        elif choice == "7":
            print("\nExiting... Goodbye!")
            break
        else:
            print("\nInvalid choice! Please enter a number between 1 and 7.\n")

# Run the menu
menu()

conn.close()