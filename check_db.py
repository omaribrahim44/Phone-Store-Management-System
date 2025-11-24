import sqlite3

conn = sqlite3.connect('shop.db')
c = conn.cursor()

print("Sales table columns:")
c.execute('PRAGMA table_info(sales)')
for row in c.fetchall():
    print(row)

print("\nCustomers table exists:")
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='customers'")
result = c.fetchone()
print(result)

if result:
    print("\nCustomers table columns:")
    c.execute('PRAGMA table_info(customers)')
    for row in c.fetchall():
        print(row)

conn.close()
