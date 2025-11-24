# Phone Management System

A desktop application for managing a mobile phone shop's inventory, sales, repairs, and customers.

## Features
- **Inventory Management**: Add, edit, and track stock levels with category support.
- **Sales Module**: Modern UI for product selection, cart handling, discounts, and receipt generation (PDF with QR code).
- **Repair Tracking**: Create and manage repair orders, view status history.
- **Customer Management**: View customer list, search by phone, and see order history.
- **Dashboard**: Quick overview of key metrics and recent activity.
- **Professional Receipts**: Styled PDF receipts with shop branding.

## Installation
1. Ensure you have **Python 3.10+** installed.
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
   (The `requirements.txt` includes `ttkbootstrap`, `reportlab`, `qrcode`, etc.)
3. Run the application:
   ```bash
   python app.py
   ```

## Usage
- The main window opens with tabs for **Dashboard**, **Sales**, **Inventory**, **Repairs**, and **Customers**.
- Use the search bars and buttons to interact with each module.
- Sales receipts are saved as PDFs in the `receipts/` folder.

## Contributing
Feel free to submit issues or pull requests. Follow standard Python coding style and run tests before contributing.


    
