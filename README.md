# 📱 Phone Store Management System

A comprehensive desktop application for managing mobile phone shop operations including inventory, sales, repairs, and customer relationships.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)](https://github.com/omaribrahim44/Phone-Store-Management-System)

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

## 🚀 Installation

### Prerequisites
- **Python 3.10+** installed
- **pip** package manager

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/omaribrahim44/Phone-Store-Management-System.git
   cd Phone-Store-Management-System
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database**
   ```bash
   python db_init.py
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

## 📋 Requirements

Key dependencies include:
- `ttkbootstrap` - Modern UI components
- `reportlab` - PDF generation
- `qrcode` - QR code generation
- `matplotlib` - Data visualization
- `hypothesis` - Property-based testing
- `pytest` - Testing framework

See `requirements.txt` for complete list.

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

- **[ENHANCEMENTS_COMPLETE.md](ENHANCEMENTS_COMPLETE.md)** - Complete feature documentation
- **[CLEANUP_SUMMARY.md](CLEANUP_SUMMARY.md)** - Project cleanup details
- **[tests/README.md](tests/README.md)** - Testing documentation

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

### Recent Updates
- ✅ Complete UI/UX modernization
- ✅ Unified customer management system
- ✅ Enhanced data visualization
- ✅ Property-based testing infrastructure
- ✅ Comprehensive audit logging
- ✅ Professional documentation

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


    
