# Installation Guide

## For Windows Users (Easiest Method) ⭐

### One-Click Install (5 Minutes)

1. **Download the Repository**
   - Click the green "Code" button on GitHub
   - Select "Download ZIP"
   - Extract to any folder (e.g., `C:\PhoneManagementSystem`)

2. **Install Python** (if not already installed)
   - Download from [python.org](https://www.python.org/downloads/)
   - **IMPORTANT**: Check "Add Python to PATH" during installation
   - Restart your computer after installation

3. **Run One-Click Installer**
   - Double-click `INSTALL_AND_RUN.bat` ⭐
   - Wait for installation to complete (2-3 minutes)
   - Desktop shortcut will be created automatically
   - Application will start automatically

4. **From Now On**
   - Just double-click the desktop shortcut "Phone Management System"
   - The installer detects if already installed and just launches the app

5. **Login**
   - Username: `admin`
   - Password: `admin123`
   - **Change password immediately** in Settings → Users

### Manual Installation (Windows)

If the batch file doesn't work:

```cmd
# 1. Open Command Prompt in the project folder
# (Shift + Right-click in folder → "Open PowerShell window here")

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize database
python db_init.py

# 4. Run application
python app.py
```

## For macOS/Linux Users

### Installation Steps

```bash
# 1. Clone or download the repository
git clone https://github.com/omaribrahim44/Phone-Store-Management-System.git
cd Phone-Store-Management-System

# 2. Create virtual environment (recommended)
python3 -m venv venv

# 3. Activate virtual environment
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Initialize database
python db_init.py

# 6. Run application
python app.py
```

### Creating a Desktop Launcher (macOS)

Create a file `Phone-Management-System.command`:

```bash
#!/bin/bash
cd /path/to/Phone-Store-Management-System
source venv/bin/activate
python app.py
```

Make it executable:
```bash
chmod +x Phone-Management-System.command
```

### Creating a Desktop Launcher (Linux)

Create a file `phone-management.desktop`:

```ini
[Desktop Entry]
Type=Application
Name=Phone Management System
Exec=/path/to/venv/bin/python /path/to/app.py
Path=/path/to/Phone-Store-Management-System
Icon=/path/to/app_icon.ico
Terminal=false
Categories=Office;
```

## Troubleshooting

### "Python is not recognized"

**Windows:**
1. Reinstall Python with "Add to PATH" checked
2. Or add Python manually to PATH:
   - Search "Environment Variables" in Windows
   - Edit "Path" variable
   - Add Python installation directory

**macOS/Linux:**
- Use `python3` instead of `python`
- Install Python via package manager:
  ```bash
  # macOS
  brew install python3
  
  # Ubuntu/Debian
  sudo apt-get install python3 python3-pip
  ```

### "pip is not recognized"

```bash
# Windows
python -m pip install -r requirements.txt

# macOS/Linux
python3 -m pip install -r requirements.txt
```

### "Module not found" errors

```bash
# Reinstall all dependencies
pip install -r requirements.txt --upgrade

# Or install individually
pip install ttkbootstrap reportlab qrcode Pillow bcrypt
```

### "Permission denied" errors

**Windows:**
- Run Command Prompt as Administrator
- Or use: `python -m pip install --user -r requirements.txt`

**macOS/Linux:**
```bash
# Use --user flag
pip install --user -r requirements.txt

# Or use sudo (not recommended)
sudo pip install -r requirements.txt
```

### Database errors

```bash
# Delete old database and reinitialize
# Windows
del shop.db
python db_init.py

# macOS/Linux
rm shop.db
python db_init.py
```

### Application won't start

1. **Check Python version:**
   ```bash
   python --version
   # Should be 3.10 or higher
   ```

2. **Check dependencies:**
   ```bash
   pip list
   # Should show ttkbootstrap, reportlab, etc.
   ```

3. **Check for errors:**
   ```bash
   python app.py
   # Read any error messages
   ```

4. **Check database:**
   ```bash
   # Verify shop.db exists in project folder
   ```

## System Requirements

### Minimum
- **OS**: Windows 10, macOS 10.14, or Ubuntu 20.04
- **Python**: 3.10 or higher
- **RAM**: 4GB
- **Storage**: 500MB free space
- **Display**: 1280x720 resolution

### Recommended
- **OS**: Windows 11, macOS 12+, or Ubuntu 22.04
- **Python**: 3.11 or higher
- **RAM**: 8GB
- **Storage**: 1GB free space
- **Display**: 1920x1080 resolution

## Verification

After installation, verify everything works:

```bash
# 1. Check Python
python --version

# 2. Check dependencies
pip list | grep ttkbootstrap

# 3. Check database
python -c "import sqlite3; conn = sqlite3.connect('shop.db'); print('Database OK')"

# 4. Test application
python -c "import app; print('Application OK')"
```

## First-Time Setup

After successful installation:

1. **Login** with admin/admin123
2. **Change Password** (Settings → Users)
3. **Configure Shop** (Settings → Shop Details)
4. **Add Products** (Inventory → Add Item)
5. **Create First Sale** (Sales → New Sale)

## Getting Help

- **Quick Start**: See [QUICK_START.md](QUICK_START.md)
- **Full Documentation**: See [README.md](README.md)
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)
- **Issues**: Open an issue on GitHub

## Uninstallation

### Windows
1. Delete the project folder
2. Delete desktop shortcut (if created)
3. (Optional) Uninstall Python if not needed

### macOS/Linux
```bash
# Remove project folder
rm -rf Phone-Store-Management-System

# Remove virtual environment
rm -rf venv

# Remove desktop launcher (if created)
rm ~/Desktop/phone-management.desktop
```

---

**Need help?** Open an issue on GitHub or check the documentation!
