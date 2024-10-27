import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime


def get_user_profile(user_id):
    conn = sqlite3.connect('db.py')  # اتصال به دیتابیس
    cursor = conn.cursor()

    # دریافت اطلاعات کاربر با توجه به user_id
    cursor.execute("SELECT username, email FROM users WHERE user_id = ?", (user_id,))
    user_data = cursor.fetchone()

    conn.close()  # بستن اتصال به دیتابیس

    # اگر کاربر وجود نداشت، None برمی‌گردد
    if user_data is None:
        print("User not found.")
    else:
        print("User Profile:")
        print("Username:", user_data[0])
        print("Email:", user_data[1])

    return user_data


def update_user_profile(user_id, new_username, new_email):
    conn = sqlite3.connect('db.py')  # اتصال به دیتابیس
    cursor = conn.cursor()

    # به‌روزرسانی اطلاعات کاربر
    cursor.execute(
        "UPDATE users SET username = ?, email = ? WHERE user_id = ?",
        (new_username, new_email, user_id)
    )
    conn.commit()  # ذخیره تغییرات

    # بستن اتصال
    conn.close()
    print("User profile updated successfully.")


def get_user_quiz_scores(user_id):
    conn = sqlite3.connect('db.py')  # اتصال به دیتابیس
    cursor = conn.cursor()

    # دریافت نمرات کوییز کاربر از جدول quiz_scores
    cursor.execute("SELECT quiz_id, score FROM quiz_scores WHERE user_id = ?", (user_id,))
    quiz_scores = cursor.fetchall()

    conn.close()  # بستن اتصال به دیتابیس

    # نمایش نمرات یا پیام مناسب در صورت نبود نمره
    if quiz_scores:
        print("Quiz Scores:")
        for quiz in quiz_scores:
            print(f"Quiz ID: {quiz[0]}, Score: {quiz[1]}")
    else:
        print("No quiz scores found for this user.")

    return quiz_scores


def close_connection(conn):
    # بستن اتصال به دیتابیس در صورت وجود
    if conn:
        conn.close()
        print("Database connection closed.")


# توابع مشاهده و ویرایش پروفایل کاربر و نمرات

def get_user_profile(user_id):
    conn = sqlite3.connect('db.py')
    cursor = conn.cursor()
    cursor.execute("SELECT username, email FROM users WHERE user_id = ?", (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    if user_data is None:
        print("User not found.")
    else:
        print("User Profile:")
        print("Username:", user_data[0])
        print("Email:", user_data[1])
    return user_data

def edit_user_profile(user_id, new_username, new_email):
    conn = sqlite3.connect('db.py')
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET username = ?, email = ? WHERE user_id = ?",
        (new_username, new_email, user_id)
    )
    conn.commit()
    conn.close()
    print("User profile updated successfully.")

def get_user_quiz_scores(user_id):
    conn = sqlite3.connect('db.py')
    cursor = conn.cursor()
    cursor.execute("SELECT quiz_id, score FROM quiz_scores WHERE user_id = ?", (user_id,))
    quiz_scores = cursor.fetchall()
    conn.close()
    if quiz_scores:
        print("Quiz Scores:")
        for quiz in quiz_scores:
            print(f"Quiz ID: {quiz[0]}, Score: {quiz[1]}")
    else:
        print("No quiz scores found for this user.")
    return quiz_scores

# توابع دریافت نمرات با تاریخ و رسم نمودار

def get_user_quiz_scores_with_dates(user_id):
    conn = sqlite3.connect('db.py')
    cursor = conn.cursor()
    cursor.execute("SELECT date, score FROM quiz_scores WHERE user_id = ? ORDER BY date", (user_id,))
    quiz_data = cursor.fetchall()
    conn.close()
    return quiz_data

def plot_user_scores_over_time(user_id):
    quiz_data = get_user_quiz_scores_with_dates(user_id)
    if not quiz_data:
        print("No quiz scores found for this user.")
        return
    dates = [datetime.strptime(row[0], '%Y-%m-%d') for row in quiz_data]
    scores = [row[1] for row in quiz_data]
    plt.figure(figsize=(10, 5))
    plt.plot(dates, scores, marker='o', color='b', linestyle='-')
    plt.xlabel('Date')
    plt.ylabel('Score')
    plt.title(f'Quiz Scores Over Time for User ID {user_id}')
    plt.grid(True)
    plt.show()
