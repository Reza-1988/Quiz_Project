# create_tables.py
import sqlite3

def create_tables():
    # اتصال به دیتابیس db.py
    conn = sqlite3.connect('db.py')
    cursor = conn.cursor()

    # ایجاد جدول کاربران
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    ''')

    # ایجاد جدول نمرات کوییز
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS quiz_scores (
        score_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        quiz_id INTEGER,
        score REAL,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    ''')

    # ذخیره تغییرات و بستن اتصال
    conn.commit()
    conn.close()


def add_date_column():
    conn = sqlite3.connect('db.py')
    cursor = conn.cursor()
    
    # اضافه کردن ستون تاریخ به جدول quiz_scores در صورت نیاز
    cursor.execute('''
    ALTER TABLE quiz_scores ADD COLUMN date TEXT
    ''')

    conn.commit()
    conn.close()

# اضافه کردن ستون تاریخ
if __name__ == "__main__":
    add_date_column()
    print("Date column added to quiz_scores table.")
# ایجاد جداول هنگام اجرای فایل
if __name__ == "__main__":
    create_tables()
    print("Tables created successfully in db.py.")
