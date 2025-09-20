# performance-management-system_25486
📋 Performance Management System (PMS)
This is a simple web-based Performance Management System built with Python, Streamlit, and a PostgreSQL database. It allows managers and employees to track goals, manage tasks, provide feedback, and view performance reports.

✨ Features
Goal & Task Management: Create, view, update, and delete goals and their associated tasks.

Progress Tracking: Monitor the status of goals and tasks.

Feedback System: Managers can provide feedback on goals, with an automated trigger for completed goals.

Reporting: A clear, centralized view of an employee's performance history, including goals and feedback.

Business Insights: A dashboard providing key performance metrics using SQL aggregations (COUNT, SUM, AVG, MIN, MAX).

🛠️ Prerequisites
Before you begin, ensure you have the following installed:

Python 3.x: The core language for the application.

PostgreSQL: The database system to store all the data.

Required Python Libraries: You'll need streamlit for the front end and psycopg2-binary for database connectivity.

You can install the Python libraries using pip:

Bash

pip install streamlit psycopg2-binary
🚀 Setup & Installation
Follow these steps to get the application up and running.

1. Database Setup
First, you need to set up the PostgreSQL database and create the necessary tables.

Connect to your PostgreSQL database instance using a client like psql or pgAdmin.

Run the SQL script provided below to create the employees, goals, tasks, and feedback tables.

SQL

-- Drop tables to start fresh
DROP TABLE IF EXISTS feedback;
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS goals;
DROP TABLE IF EXISTS employees;

-- Create Employees table
CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    manager_id INTEGER REFERENCES employees(employee_id)
);

-- Create Goals table
CREATE TABLE goals (
    goal_id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(employee_id),
    manager_id INTEGER REFERENCES employees(employee_id),
    description TEXT NOT NULL,
    due_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('Draft', 'In Progress', 'Completed', 'Cancelled'))
);

-- Create Tasks table
CREATE TABLE tasks (
    task_id SERIAL PRIMARY KEY,
    goal_id INTEGER REFERENCES goals(goal_id),
    description TEXT NOT NULL,
    is_approved BOOLEAN DEFAULT FALSE
);

-- Create Feedback table
CREATE TABLE feedback (
    feedback_id SERIAL PRIMARY KEY,
    goal_id INTEGER REFERENCES goals(goal_id),
    manager_id INTEGER REFERENCES employees(employee_id),
    feedback_text TEXT NOT NULL,
    automated_trigger_info TEXT
);

-- Add some sample data
INSERT INTO employees (name, manager_id) VALUES
('Alice Johnson', NULL),
('Bob Smith', 1),
('Charlie Brown', 1),
('Diana Prince', 2);

INSERT INTO goals (employee_id, manager_id, description, due_date, status) VALUES
(2, 1, 'Complete Q3 sales report', '2023-09-30', 'In Progress'),
(3, 1, 'Develop new marketing strategy', '2023-10-15', 'Draft'),
(4, 2, 'Onboard new team members', '2023-09-25', 'Completed');

2. Configure the Application
The application is split into two files: backend.py and frontend.py.

backend.py: This file contains the database connection logic and all the CRUD operations.

frontend.py: This file builds the user interface using Streamlit and calls the functions from backend.py.

In frontend.py, you need to update the DB_DETAILS dictionary with your specific PostgreSQL connection information:

Python

DB_DETAILS = {
    'dbname': 'your_db_name',
    'user': 'your_user',
    'password': 'your_password',
    'host': 'localhost'
}
3. Run the Application
Once the database is set up and the connection details are configured, you can run the Streamlit application from your terminal.

Navigate to the directory containing your files and execute:

Bash

streamlit run frontend.py
A new tab should open in your default web browser, displaying the Performance Management System.

📂 File Structure
The project has a clean and simple structure:

.
├── backend.py
└── frontend.py
└── README.md
backend.py: Contains the DatabaseManager class for all database interactions.

frontend.py: The Streamlit application interface.

README.md: This file.

This project can be easily extended with more features, such as user authentication, more detailed reporting, or additional feedback triggers.






