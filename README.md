# Laptop Inventory Management System

This is a desktop application built with Python for managing a laptop inventory business. It provides a graphical user interface to handle various aspects of the business, from inventory control to sales and reporting.

## Features

*   **Welcome Screen**: An initial screen to welcome the user.
*   **Admin Panel**: A comprehensive dashboard for administrators to manage the entire system.
*   **Point of Sale (POS)**: A dedicated window for processing sales transactions.
*   **Inventory Management**:
    *   Add, update, and view inventory items.
    *   Track stock levels and locations.
*   **Reporting**: Generate reports on sales, inventory, and customers.
*   **Customer Management**: Keep a record of customer information.
*   **Database Management**:
    *   Initialize the database schema.
    *   Seed the database with initial data for testing and demonstration.

## Tech Stack

*   **Language**: Python
*   **GUI**: (Likely) Tkinter or a similar Python GUI framework.
*   **Database**: SQLite (as suggested by the `db.py` and `initialize_database.py` files).

## Project Structure

The project is organized into a modular structure:

*   `main.py`: The main entry point of the application.
*   **Window Files** (`welcome_window.py`, `admin_panel.py`, `inventory_window.py`, etc.): Each file defines a specific window or part of the user interface.
*   `app/`: This directory contains the core application logic, following a Model-View-Controller (MVC) like pattern.
    *   `models/`: Defines the database tables and data structures (e.g., `products.py`, `sales.py`, `customers.py`).
    *   `controllers/`: Contains the business logic to handle user interactions and data manipulation.
    *   `database/`: Manages the database connection.
*   `widgets.py`: Contains custom UI widgets used across the application.
*   `styles.py`: Defines the styling for the UI components.
*   `requirements.txt`: Lists the Python dependencies required to run the project.

## How to Run

1.  **Install Dependencies**:
    Open a terminal in the project directory and run:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Initialize the Database**:
    Run the database initialization script to set up the necessary tables:
    ```bash
    python initialize_database.py
    ```

3.  **Seed the Database (Optional)**:
    To populate the database with some sample data, run:
    ```bash
    python seed_data.py
    ```

4.  **Run the Application**:
    Start the application by running the main script:
    ```bash
    python main.py
    ```
