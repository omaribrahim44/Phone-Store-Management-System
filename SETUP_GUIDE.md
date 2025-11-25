# 📖 Complete Setup Guide - Phone Store Management System

This guide provides detailed step-by-step instructions for setting up and running the Phone Store Management System on your local machine.

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [First Run](#first-run)
4. [Configuration](#configuration)
5. [Troubleshooting](#troubleshooting)
6. [Advanced Setup](#advanced-setup)

---

## 🔧 Prerequisites

### 1. Install Python

**Windows:**
1. Download Python 3.10+ from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. ✅ **IMPORTANT**: Check "Add Python to PATH" during installation
4. Click "Install Now"
5. Verify installation:
   ```cmd
   python --version
   ```

**macOS:**
```bash
# Using Homebrew (recommended)
brew install python@3.10

# Or download from python.org
# Verify installation
python3 --version
```

**Linux (Ubuntu/Debian):**
```bash
# Update package list
sudo apt update

# Install Python 3.10+
sudo apt install python3.10 python3-pip python3-venv python3-tk

# Verify installation
python3 --version
```

### 2. Install Git (Optional but Recommended)

**Windows:**
- Download from [git-scm.com](https://git-scm.com/downloads)
- Run installer with default settings

**macOS:**
```bash
brew install git
```

**Linux:**
```bash
sudo apt install git
```

---

## 💻 Installation

### Method 1: Clone with Git (Recommended)

```bash
# 1. Open terminal/command prompt

# 2. Navigate to where you want to install
cd Desktop  # or any folder you prefer

# 3. Clone the repository
git clone https://github.com/omaribrahim44/Phone-Store-Management-System.git

# 4. Enter the project directory
cd Phone-Store-Management-System
```

### Method 2: Download ZIP

1. Go to https://github.com/omaribrahim44/Phone-Store-Management-System
2. Click the green "Code" button
3. Click "Download ZIP"
4. Extract the ZIP file to your desired location
5. Open terminal/command prompt in the extracted folder

---

## 🚀 Setup Steps

### Step 1: Create Virtual Environment (Recommended)

A virtual environment keeps your project dependencies isolated.

**Windows:**
```cmd
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

**macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# You should see (venv) in your terminal prompt
```

### Step 2: Install Dependencies

```bash
# Upgrade pip first (recommended)
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt

# Wait for installation to complete (may take 2-3 minutes)
```

**Expected Output:**
```
Successfully installed ttkbootstrap-1.10.1 reportlab-4.0.0 qrcode-7.4.2 ...
```

### Step 3: Initialize Database

```bash
# Run database initialization script
python db_init.py
```

**Expected Output:**
```
Database initialized successfully!
Default admin user created.
```

### Step 4: Run the Application

```bash
# Start the application
python app.py
```

**Expected Output:**
```
Application starting...
Loaded configuration. Theme: flatly
```

The application window should open!

---

## 🎯 First Run

### Default Login Credentials

When you first run the application:
- **Username**: `admin`
- **Password**: `admin123`

⚠️ **IMPORTANT**: Change this password immediately!

### Initial Setup Checklist

1. **Change Admin Password**
   - Go to: Settings → Users
   - Select admin user
   - Click "Change Password"
   - Enter new secure password

2. **Configure Shop Details**
   - Go to: Settings
   - Update:
     - Shop Name
     - Shop Address
     - Shop Phone Number
   - Click "Save Configuration"

3. **Add Your First Product**
   - Go to: Inventory
   - Click "Add Item"
   - Fill in product details:
     - Name (e.g., "iPhone 13")
     - Category (e.g., "Smartphones")
     - Cost Price (what you paid)
     - Selling Price (what you charge)
     - Stock Quantity
   - Click "Add Item"

4. **Test a Sale**
   - Go to: Sales
   - Search for your product
   - Add to cart
   - Enter customer details
   - Complete sale
   - Check if PDF receipt is generated

---

## ⚙️ Configuration

### Shop Configuration File

Edit `shop_config.json` to customize:

```json
{
  "name": "Your Phone Shop Name",
  "address": "123 Main Street, City, Country",
  "phone": "+1-234-567-8900",
  "theme": "flatly"
}
```

**Available Themes:**
- `flatly` (default - clean and modern)
- `darkly` (dark theme)
- `cosmo` (colorful)
- `litera` (minimal)
- `minty` (green accent)
- `pulse` (purple accent)
- `sandstone` (warm tones)
- `united` (orange accent)
- `yeti` (blue accent)

### Database Location

The SQLite database is stored at:
```
Phone-Store-Management-System/shop.db
```

**Backup Location:**
```
Phone-Store-Management-System/backups/
```

### Log Files

Application logs are stored at:
```
Phone-Store-Management-System/logs/app.log
```

---

## 🔍 Troubleshooting

### Problem: "Python is not recognized"

**Solution:**
1. Reinstall Python
2. Make sure to check "Add Python to PATH"
3. Restart your terminal/command prompt

**Alternative:**
```bash
# Use full path to Python
C:\Users\YourName\AppData\Local\Programs\Python\Python310\python.exe app.py
```

### Problem: "No module named 'ttkbootstrap'"

**Solution:**
```bash
# Make sure virtual environment is activated
# Then reinstall dependencies
pip install -r requirements.txt
```

### Problem: "Permission denied" (Windows)

**Solution 1:**
```cmd
# Run terminal as Administrator
# Right-click Command Prompt → "Run as administrator"
```

**Solution 2:**
```cmd
# Install with --user flag
pip install --user -r requirements.txt
```

### Problem: "Permission denied" (macOS/Linux)

**Solution:**
```bash
# Don't use sudo with virtual environment
# Instead, ensure venv is activated
source venv/bin/activate
pip install -r requirements.txt
```

### Problem: Database errors

**Solution:**
```bash
# Delete old database and reinitialize
rm shop.db  # or del shop.db on Windows
python db_init.py
```

### Problem: "tkinter not found" (Linux)

**Solution:**
```bash
# Install tkinter
sudo apt-get install python3-tk
```

### Problem: Application window doesn't open

**Solution:**
```bash
# Check for errors in terminal
# Check logs
cat logs/app.log  # or type logs/app.log on Windows
```

### Problem: "ModuleNotFoundError: No module named 'PIL'"

**Solution:**
```bash
# Install Pillow
pip install Pillow
```

---

## 🔬 Advanced Setup

### Running Tests

```bash
# Install testing dependencies (if not already installed)
pip install pytest hypothesis faker pytest-cov

# Run all tests
pytest

# Run specific test file
pytest tests/test_inventory.py

# Run with coverage report
pytest --cov=modules --cov=controllers

# Run with verbose output
pytest -v
```

### Development Mode

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with debug logging
python app.py --debug  # if implemented

# Or check logs
tail -f logs/app.log  # macOS/Linux
# or
Get-Content logs/app.log -Wait  # Windows PowerShell
```

### Creating Executable (Optional)

```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller app.spec

# Executable will be in dist/ folder
```

### Database Backup

```bash
# Manual backup
python -c "from modules.backup_manager import create_backup; create_backup()"

# Backups are stored in backups/ folder
```

### Updating the Application

```bash
# If you cloned with git
git pull origin main

# Reinstall dependencies (in case of updates)
pip install --upgrade -r requirements.txt

# Restart the application
python app.py
```

---

## 📱 Usage Tips

### Keyboard Shortcuts
- `Ctrl+Tab` - Switch between tabs
- `Ctrl+F` - Focus search box (in most views)
- `Esc` - Close dialogs
- `Enter` - Confirm actions

### Best Practices
1. **Regular Backups**: Use Settings → Backup Database weekly
2. **Update Inventory**: Keep stock levels current
3. **Customer Data**: Always capture customer phone for tracking
4. **Receipts**: Store PDF receipts for records
5. **User Accounts**: Create separate accounts for staff

### Performance Tips
- Close unused tabs
- Clear old logs periodically
- Archive old database backups
- Keep inventory under 10,000 items for best performance

---

## 🆘 Getting Help

### Check Documentation
- [README.md](README.md) - Overview and features
- [ENHANCEMENTS_COMPLETE.md](ENHANCEMENTS_COMPLETE.md) - Detailed features
- [tests/README.md](tests/README.md) - Testing guide

### Report Issues
- GitHub Issues: https://github.com/omaribrahim44/Phone-Store-Management-System/issues
- Include:
  - Your OS and Python version
  - Error messages
  - Steps to reproduce
  - Screenshots if applicable

### Community Support
- Check existing issues on GitHub
- Search for similar problems
- Ask questions in discussions

---

## ✅ Quick Reference

### Start Application
```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Run application
python app.py
```

### Stop Application
- Click the X button on the window
- Or press `Ctrl+C` in terminal

### Deactivate Virtual Environment
```bash
deactivate
```

### Update Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Reset Database
```bash
python db_init.py
```

---

## 🎉 Success!

If you've followed all steps, you should now have:
- ✅ Python installed
- ✅ Project downloaded
- ✅ Virtual environment created
- ✅ Dependencies installed
- ✅ Database initialized
- ✅ Application running

**Enjoy managing your phone store!** 📱✨

---

**Need more help?** Open an issue on GitHub or check the documentation files.
