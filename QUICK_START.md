# ⚡ Quick Start - Phone Store Management System

## 🚀 Get Running in 5 Minutes

### For Windows Users

```cmd
# 1. Download and extract the project
# (or clone: git clone https://github.com/omaribrahim44/Phone-Store-Management-System.git)

# 2. Open Command Prompt in project folder

# 3. Run these commands:
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python db_init.py
python app.py
```

### For macOS/Linux Users

```bash
# 1. Download and extract the project
# (or clone: git clone https://github.com/omaribrahim44/Phone-Store-Management-System.git)

# 2. Open Terminal in project folder

# 3. Run these commands:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python db_init.py
python app.py
```

## 🔑 Default Login

- **Username**: `admin`
- **Password**: `admin123`

⚠️ Change this immediately in Settings!

## 📚 Need More Help?

- **Detailed Instructions**: Read [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Features Overview**: Read [README.md](README.md)
- **Troubleshooting**: Check [SETUP_GUIDE.md#troubleshooting](SETUP_GUIDE.md#troubleshooting)

## ✅ Checklist

- [ ] Python 3.10+ installed
- [ ] Project downloaded/cloned
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Database initialized
- [ ] Application running
- [ ] Admin password changed
- [ ] Shop details configured

## 🆘 Common Issues

**"Python not found"**
→ Install Python from python.org and check "Add to PATH"

**"Module not found"**
→ Make sure virtual environment is activated, then run: `pip install -r requirements.txt`

**"Permission denied"**
→ Run terminal as administrator (Windows) or use `--user` flag

**Database errors**
→ Delete `shop.db` and run `python db_init.py` again

---

**That's it! You're ready to go!** 🎉
