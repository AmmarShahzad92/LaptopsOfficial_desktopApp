# Laptop Inventory & POS System

This is a comprehensive desktop application built with Python and PyQt6 for managing a laptop inventory and sales business. It provides a feature-rich graphical user interface to handle various aspects of the business, from inventory control and sales processing (Point of Sale) to customer management and in-depth reporting.

## Features

*   **Authentication**: Secure login for staff members with role-based access.
*   **Admin Panel**: A central dashboard for administrators to manage the entire system, including staff, roles, and locations.
*   **Point of Sale (POS)**: A dedicated window for processing sales transactions, generating invoices, and printing receipts.
*   **Inventory Management**:
    *   Add, update, and view products and categories.
    *   Track stock levels across different locations (stores, warehouses).
    *   Manage suppliers and purchase orders.
    *   Handle stock movements and returns.
*   **Reporting**:
    *   Generate detailed reports on sales, inventory, purchases, and customer activity.
    *   Visualize data with charts and graphs.
*   **Customer Management**: Maintain a database of customer information for sales and marketing purposes.
*   **Database Management**:
    *   Initialize the SQLite database schema.
    *   Seed the database with initial data for testing and demonstration.

## Tech Stack

*   **Language**: Python
*   **GUI**: PyQt6
*   **Database**: SQLite
*   **Reporting**: reportlab (for PDF generation), pandas, openpyxl
*   **Data Visualization**: matplotlib, seaborn
*   **Barcode/QR Code**: python-barcode, qrcode

## Project Structure

The project is organized into a modular structure:

*   `main.py`: The main entry point of the application.
*   **Window Files** (`welcome_window.py`, `admin_panel.py`, `pos_window.py`, etc.): Each file defines a specific window or major UI component.
*   `app/`: This directory contains the core application logic, following a layered architecture.
    *   `models/`: Defines the database schema and data structures using SQLAlchemy-like classes for each table (e.g., `products.py`, `sales.py`, `customers.py`).
    *   `controllers/`: Contains the business logic to handle user interactions, data validation, and communication between the UI and the database.
    *   `database/`: Manages the database connection (`db.py`).
*   `widgets.py`: Contains custom UI widgets used across the application.
*   `styles.py`: Defines the styling (QSS) for the UI components.
*   `initialize_database.py`: Script to create the database tables.
*   `seed_data.py`: Script to populate the database with sample data.
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
    To populate the database with some sample data for demonstration, run:
    ```bash
    python seed_data.py
    ```

4.  **Run the Application**:
    Start the application by running the main script:
    ```bash
    python main.py
    ```
