# 🚀 Quick Start Guide

Get up and running with Phone Store Management System in 5 minutes!

## Prerequisites

- **Python 3.10+** installed ([Download](https://www.python.org/downloads/))
- **Git** (optional, for cloning)

## Installation

### Option 1: Quick Install (Recommended)

```bash
# 1. Clone or download the repository
git clone https://github.com/omaribrahim44/Phone-Store-Management-System.git
cd Phone-Store-Management-System

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize database
python db_init.py

# 4. Run the application
python app.py
```

### Option 2: With Virtual Environment (Best Practice)

```bash
# 1. Clone or download
git clone https://github.com/omaribrahim44/Phone-Store-Management-System.git
cd Phone-Store-Management-System

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Initialize database
python db_init.py

# 6. Run the application
python app.py
```

## First Login

**Default Credentials:**
- Username: `admin`
- Password: `admin123`

⚠️ **Important**: Change this password immediately after first login!

## Quick Configuration

1. **Go to Settings Tab**
   - Update shop name, address, and phone
   - Choose your preferred theme
   - Configure backup settings

2. **Add Your First Product**
   - Navigate to Inventory tab
   - Click "Add Item"
   - Fill in product details

3. **Create Your First Sale**
   - Go to Sales tab
   - Search and add products
   - Complete the transaction

## Common Issues

### "Python not found"
```bash
# Check Python installation
python --version

# If not installed, download from python.org
```

### "Module not found"
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### "Database error"
```bash
# Reinitialize database
python db_init.py
```

### "Permission denied" (Windows)
```bash
# Run as administrator or use:
python -m pip install -r requirements.txt
```

## Features Overview

### 📊 Dashboard
Real-time business metrics with modern visualizations

### 💰 Sales
Point-of-sale system with receipt generation

### 📦 Inventory
Product catalog with stock tracking

### 🔧 Repairs
Complete repair order management

### 👥 Customers
Unified customer database with VIP tracking

### 📝 Audit Logs
Complete transaction history

### 👤 Users
Multi-user support with roles

### ⚙️ Settings
Shop configuration and backups

## Need Help?

- **Documentation**: See [README.md](README.md) for detailed information
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines
- **Issues**: Open an issue on GitHub
- **Changelog**: See [CHANGELOG.md](CHANGELOG.md) for version history

## Next Steps

1. **Explore the Interface** - Click through all tabs
2. **Add Sample Data** - Create test products and sales
3. **Configure Settings** - Customize for your shop
4. **Read Documentation** - Learn about advanced features
5. **Backup Regularly** - Use Settings → Backup

## System Requirements

- **OS**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 20.04+)
- **Python**: 3.10 or higher
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 500MB free space
- **Display**: 1280x720 minimum resolution

## Quick Tips

💡 **Use keyboard shortcuts** for faster navigation
💡 **Enable auto-backup** in Settings
💡 **Export data regularly** for safety
💡 **Update passwords** for all users
💡 **Check audit logs** for activity tracking

---

**Ready to go?** Run `python app.py` and start managing your phone shop! 🎉
