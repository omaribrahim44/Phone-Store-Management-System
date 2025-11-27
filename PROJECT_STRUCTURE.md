# 📁 Project Structure

## Overview
This document describes the organization of the Phone Management System project.

## Root Directory

```
Phone-Store-Management-System/
│
├── 📄 INSTALL_AND_RUN.bat          ⭐ Main installer & launcher (START HERE!)
├── 📄 README.md                     Main documentation
├── 📄 LICENSE                       MIT License
├── 📄 requirements.txt              Python dependencies
├── 📄 .env.example                  Environment configuration template
├── 📄 .gitignore                    Git ignore rules
├── 📄 pytest.ini                    Pytest configuration
│
├── 🐍 app.py                        Application entry point
├── 🐍 config.py                     Configuration management
├── 🐍 db_init.py                    Database initialization
│
├── 🖼️  app_icon.ico                  Application icon
│
├── 📊 shop.db                       SQLite database (gitignored)
├── 📊 shop_config.json              Shop configuration (gitignored)
│
├── 📁 controllers/                  Business logic controllers
│   ├── auth_controller.py
│   ├── inventory_controller.py
│   ├── repair_controller.py
│   └── ...
│
├── 📁 modules/                      Core functionality modules
│   ├── models.py
│   ├── validators.py
│   ├── barcode_manager.py
│   ├── mobile_spec_manager.py
│   └── reports/
│       ├── receipt_generator.py
│       ├── thermal_printer.py
│       └── label_printer.py
│
├── 📁 ui/                           User interface components
│   ├── main.py
│   ├── dashboard_view.py
│   ├── sales_view.py
│   ├── inventory_view.py
│   ├── repairs_view.py
│   ├── customers_view.py
│   ├── users_view.py
│   ├── login_view.py
│   ├── styles.py
│   └── table_styles.py
│
├── 📁 tests/                        Test suite
│   ├── conftest.py
│   ├── generators.py
│   ├── test_inventory.py
│   ├── test_sales.py
│   ├── test_repairs.py
│   └── ...
│
├── 📁 docs/                         Documentation
│   ├── INSTALL.md
│   ├── QUICK_START.md
│   ├── CONTRIBUTING.md
│   ├── CHANGELOG.md
│   ├── CLEANUP_SUMMARY.md
│   ├── GITHUB_UPLOAD_CHECKLIST.md
│   └── INSTALLATION_VERIFICATION.md
│
├── 📁 scripts/                      Utility scripts
│   ├── CLEAN_DATABASE.bat
│   ├── RESET_DATABASE.bat
│   ├── clean_database.py
│   ├── check_database.py
│   └── create_shortcut_with_icon.vbs
│
├── 📁 config/                       Configuration examples
│   ├── shop_config.example.json
│   ├── barcode_scanner_config.example.json
│   ├── label_preferences.example.json
│   ├── quick_add_templates.example.json
│   └── barcode_products.example.json
│
├── 📁 backups/                      Database backups (gitignored)
├── 📁 logs/                         Application logs (gitignored)
├── 📁 receipts/                     Generated receipts (gitignored)
├── 📁 reports/                      Generated reports (gitignored)
└── 📁 labels/                       Generated labels (gitignored)
```

## Directory Purposes

### 🎯 Core Application Files (Root)
- **INSTALL_AND_RUN.bat** - One-click installer and launcher
- **app.py** - Main application entry point
- **config.py** - Configuration management
- **db_init.py** - Database initialization
- **requirements.txt** - Python package dependencies

### 📚 Documentation (`docs/`)
All user-facing documentation:
- Installation guides
- Quick start guide
- Contributing guidelines
- Changelog
- Project summaries

### 🔧 Utility Scripts (`scripts/`)
Helper scripts for maintenance:
- Database cleaning and reset tools
- Shortcut creation scripts
- Database inspection tools

### ⚙️ Configuration (`config/`)
Example configuration files:
- Shop settings template
- Barcode scanner configuration
- Label printing preferences
- Quick-add templates

### 🎨 User Interface (`ui/`)
All GUI components:
- Main window
- View components (dashboard, sales, inventory, etc.)
- Styling and themes

### 🧠 Business Logic (`controllers/`)
Application controllers:
- Authentication
- Inventory management
- Sales processing
- Repair tracking

### 🔨 Core Modules (`modules/`)
Reusable functionality:
- Data models
- Validators
- Barcode management
- Report generation
- Mobile specifications

### 🧪 Tests (`tests/`)
Comprehensive test suite:
- Unit tests
- Property-based tests
- Integration tests
- Test data generators

### 📦 Generated/Runtime Files (Gitignored)
- **backups/** - Database backups
- **logs/** - Application logs
- **receipts/** - Generated PDF receipts
- **reports/** - Generated PDF reports
- **labels/** - Generated barcode labels
- **shop.db** - SQLite database
- **shop_config.json** - User configuration

## File Naming Conventions

### Python Files
- `snake_case.py` - All Python files
- `test_*.py` - Test files (in tests/ folder)

### Batch Files
- `UPPERCASE.bat` - Batch scripts for Windows

### Documentation
- `UPPERCASE.md` - Important docs (README, LICENSE, CONTRIBUTING)
- `Title_Case.md` - Other documentation

### Configuration
- `lowercase.json` - Configuration files
- `*.example.json` - Example configurations (in config/)

## Quick Navigation

### For Users
1. **Getting Started**: `INSTALL_AND_RUN.bat`
2. **Documentation**: `README.md` → `docs/QUICK_START.md`
3. **Configuration**: `config/` folder for examples

### For Developers
1. **Source Code**: `controllers/`, `modules/`, `ui/`
2. **Tests**: `tests/` folder
3. **Contributing**: `docs/CONTRIBUTING.md`

### For Maintenance
1. **Database Tools**: `scripts/` folder
2. **Logs**: `logs/` folder
3. **Backups**: `backups/` folder

## Best Practices

### Adding New Features
1. **Controllers** - Add business logic in `controllers/`
2. **UI** - Add views in `ui/`
3. **Models** - Add data models in `modules/models.py`
4. **Tests** - Add tests in `tests/`
5. **Docs** - Update relevant documentation

### Configuration
- Never commit actual config files (use .gitignore)
- Always provide `.example` versions in `config/`
- Document all config options

### Documentation
- Keep README.md concise and user-focused
- Detailed docs go in `docs/` folder
- Update CHANGELOG.md for all releases

## Clean Architecture

```
┌─────────────────────────────────────┐
│         User Interface (ui/)        │
│  Dashboard, Sales, Inventory, etc.  │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Controllers (controllers/)     │
│   Business Logic & Orchestration    │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│        Modules (modules/)           │
│  Models, Validators, Utilities      │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│       Database (shop.db)            │
│         SQLite Storage              │
└─────────────────────────────────────┘
```

## Summary

✅ **Well-Organized** - Clear separation of concerns
✅ **Easy to Navigate** - Logical folder structure
✅ **Professional** - Industry-standard layout
✅ **Maintainable** - Easy to find and update files
✅ **User-Friendly** - Simple for end users
✅ **Developer-Friendly** - Clear for contributors

---

**Last Updated**: 2025-11-27
**Version**: 2.0
