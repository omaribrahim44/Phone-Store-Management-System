# 📱 Phone Store Management System

A comprehensive desktop application for managing mobile phone shop operations including inventory, sales, repairs, and customer relationships.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)](https://github.com/omaribrahim44/Phone-Store-Management-System)
[![Tests](https://img.shields.io/badge/Tests-148%20Passing-success.svg)](tests/)

## 🚀 Quick Start (5 Minutes Setup)

### **For Windows Users (Easiest Method):**
1. **Install Python** from [python.org](https://www.python.org/downloads/) (✅ Check "Add Python to PATH")
2. **Download** this project (Code → Download ZIP)
3. **Extract** to any folder (e.g., `C:\PhoneManagementSystem`)
4. **Double-click** `INSTALL_AND_RUN.bat` ⭐
5. **Done!** Application installs, creates desktop shortcut, and launches automatically

### **From Now On:**
- Just double-click the **"Phone Management System"** icon on your desktop!

### **Login:**
- Username: `admin`
- Password: `admin123`
- ⚠️ Change password immediately after first login!

## ✨ Features

### 📊 Dashboard
- Real-time business metrics with modern donut charts
- 6-card layout showing sales, revenue, profit, repairs, overdue orders, and stock levels
- Professional data visualization with colorblind-friendly palette
- Efficient database queries for instant updates

### 💰 Sales Management
- Modern point-of-sale interface with product search
- Shopping cart with quantity management
- Discount and tax calculations
- Customer data capture (name, phone, email, address)
- Professional PDF receipt generation with QR codes
- Automatic customer relationship tracking

### 📦 Inventory Management
- Comprehensive product catalog with categories
- Stock level tracking with visual indicators
- Low stock and out-of-stock alerts
- Add/Edit/Delete functionality with validation
- Profit margin calculator
- Real-time inventory value display
- Barcode support

### 🔧 Repair Tracking
- Complete repair order management
- Device information tracking (model, IMEI)
- Parts and service itemization
- Status tracking (Pending, In Progress, Completed)
- Customer linking and history
- Repair receipt generation

### 👥 Customer Management
- Unified customer database
- Visual customer type differentiation:
  - 🛒 **Sales Customers** (Green) - Purchase only
  - 🔧 **Repair Customers** (Blue) - Repairs only
  - 🌟 **VIP Customers** (Purple) - Both purchases and repairs
- Tab-based filtering by customer type
- Complete contact information (phone, email, address)
- Purchase and repair statistics
- Customer detail views with stat cards
- Export functionality

### 📝 Audit Logs
- Complete transaction history
- User action tracking
- Timestamp and user identification
- Searchable and filterable logs

### 👤 User Management
- Multi-user support with role-based access
- Secure password hashing
- Admin and staff roles
- User activity tracking

### ⚙️ Settings
- Shop configuration (name, address, phone)
- Theme customization
- Backup and restore functionality
- System health checks

## 🚀 Quick Start

> **⚡ Want to get started fast?** Check out [QUICK_START.md](QUICK_START.md) for a 5-minute setup!

### Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.10 or higher** - [Download Python](https://www.python.org/downloads/)
- **pip** (comes with Python)
- **Git** (optional, for cloning) - [Download Git](https://git-scm.com/downloads)

### Installation Steps

#### Option 1: Using Git (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/omaribrahim44/Phone-Store-Management-System.git

# 2. Navigate to project directory
cd Phone-Store-Management-System

# 3. Create a virtual environment (recommended)
python -m venv venv

# 4. Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 5. Install dependencies
pip install -r requirements.txt

# 6. Initialize the database
python db_init.py

# 7. Run the application
python app.py
```

#### Option 2: Download ZIP

```bash
# 1. Download ZIP from GitHub
# Click "Code" → "Download ZIP" on the repository page
# Extract the ZIP file to your desired location

# 2. Open terminal/command prompt in the extracted folder

# 3. Create a virtual environment (recommended)
python -m venv venv

# 4. Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 5. Install dependencies
pip install -r requirements.txt

# 6. Initialize the database
python db_init.py

# 7. Run the application
python app.py
```

### First Time Setup

After running the application for the first time:

1. **Default Admin Credentials**
   - Username: `admin`
   - Password: `admin123`
   - ⚠️ **Change this immediately** via Settings → Users

2. **Configure Shop Details**
   - Go to Settings tab
   - Update shop name, address, and phone number
   - Choose your preferred theme

3. **Add Initial Inventory**
   - Navigate to Inventory tab
   - Click "Add Item" to add your first products

### Troubleshooting

#### Python Version Issues
```bash
# Check Python version
python --version

# If version is below 3.10, download latest from python.org
```

#### Module Not Found Errors
```bash
# Ensure virtual environment is activated
# Then reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

#### Database Errors
```bash
# Reinitialize the database
python db_init.py
```

#### Permission Errors (Windows)
```bash
# Run as administrator or use:
python -m pip install -r requirements.txt
```

#### Permission Errors (macOS/Linux)
```bash
# Use pip with --user flag
pip install --user -r requirements.txt
```

## 📋 System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 20.04+)
- **Python**: 3.10 or higher
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 500MB free space
- **Display**: 1280x720 minimum resolution

### Python Dependencies

#### Core Dependencies
- `ttkbootstrap>=1.10.1` - Modern UI components and themes
- `reportlab>=4.0.0` - Professional PDF receipt generation
- `qrcode>=7.4.2` - QR code generation for receipts
- `Pillow>=10.0.0` - Image processing for QR codes
- `bcrypt>=4.1.0` - Secure password hashing

#### Testing Dependencies (Optional)
- `hypothesis>=6.90.0` - Property-based testing framework
- `pytest>=7.4.0` - Testing framework
- `pytest-cov>=4.1.0` - Code coverage reports
- `faker>=20.0.0` - Test data generation

#### Standard Library (Included with Python)
- `sqlite3` - Database management
- `tkinter` - GUI framework (comes with Python)
- `json` - Configuration management
- `datetime` - Date/time handling
- `hashlib` - Password hashing
- `pathlib` - File path operations

### Installing Dependencies

```bash
# Install all dependencies (including testing)
pip install -r requirements.txt

# Install only core dependencies (without testing tools)
pip install ttkbootstrap reportlab qrcode Pillow bcrypt
```

### Verifying Installation

```bash
# Check if all dependencies are installed
pip list

# Run a quick test
python -c "import ttkbootstrap, reportlab, qrcode; print('All core dependencies installed!')"
```

## 🎨 User Interface

The application features a modern, professional interface with:
- **Consistent Design**: Segoe UI font family throughout
- **Color-Coded Elements**: Visual differentiation for quick recognition
- **Responsive Layout**: Adapts to different screen sizes
- **Modern Placeholders**: Contextual hints in all input fields
- **Professional Styling**: ttkbootstrap themes with custom enhancements

## 🗄️ Database Schema

SQLite database with the following main tables:
- `inventory` - Product catalog and stock levels
- `sales` - Sales transactions
- `sale_items` - Individual items in sales
- `repair_orders` - Repair service orders
- `customers` - Unified customer database
- `users` - System users and authentication
- `audit_log` - System activity tracking

## 🧪 Testing

Comprehensive test suite with property-based testing:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_inventory.py

# Run with coverage
pytest --cov=modules --cov=controllers
```

Test coverage includes:
- Unit tests for all controllers
- Property-based tests for data integrity
- Transaction atomicity tests
- Validation tests
- Integration tests

## 📁 Project Structure

```
Phone-Store-Management-System/
├── controllers/          # Business logic
├── modules/             # Core functionality
├── ui/                  # User interface components
├── tests/               # Test suite
├── backups/             # Database backups
├── logs/                # Application logs
├── app.py              # Application entry point
├── db_init.py          # Database initialization
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## 🔧 Configuration

Edit `shop_config.json` to customize:
```json
{
  "name": "Your Shop Name",
  "address": "Your Address",
  "phone": "Your Phone Number",
  "theme": "flatly"
}
```

## 📖 Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - 📖 **Complete setup instructions** (START HERE!)
- **[ENHANCEMENTS_COMPLETE.md](ENHANCEMENTS_COMPLETE.md)** - Complete feature documentation
- **[CLEANUP_SUMMARY.md](CLEANUP_SUMMARY.md)** - Project cleanup details
- **[tests/README.md](tests/README.md)** - Testing documentation

### 🆘 Need Help?
- **New to the project?** Read [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed instructions
- **Having issues?** Check the [Troubleshooting](#troubleshooting) section
- **Want to contribute?** See [Contributing](#contributing) guidelines

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please ensure:
- Code follows Python PEP 8 style guide
- All tests pass (`pytest`)
- New features include tests
- Documentation is updated

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**Omar Ibrahim**
- GitHub: [@omaribrahim44](https://github.com/omaribrahim44)

## 🙏 Acknowledgments

- Built with [ttkbootstrap](https://ttkbootstrap.readthedocs.io/) for modern UI
- PDF generation powered by [ReportLab](https://www.reportlab.com/)
- Testing with [Hypothesis](https://hypothesis.readthedocs.io/) for property-based testing

## 📊 Project Status

✅ **Production Ready** - Fully functional with comprehensive testing

### Recent Updates (v2.0)
- ✅ Complete UI/UX modernization with ttkbootstrap
- ✅ Unified customer management system with VIP tracking
- ✅ Enhanced data visualization with donut charts
- ✅ Property-based testing infrastructure with Hypothesis
- ✅ Comprehensive audit logging for all operations
- ✅ Barcode scanning and label printing support
- ✅ Thermal receipt printer integration
- ✅ Mobile phone specifications database
- ✅ Quick-add templates for faster data entry
- ✅ IMEI field now optional for repair orders
- ✅ Automatic part linking and checkout receipts for repairs

## 🐛 Bug Reports

Found a bug? Please open an issue with:
- Description of the bug
- Steps to reproduce
- Expected behavior
- Screenshots (if applicable)
- System information (OS, Python version)

## 💡 Feature Requests

Have an idea? Open an issue with the `enhancement` label and describe:
- The feature you'd like to see
- Why it would be useful
- How it might work

---

**Made with ❤️ for phone shop management**


    
