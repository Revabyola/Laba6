from tkinter import *
import re
import sqlite3

DB_PATH = r"C:\Users\Иван\Desktop\students.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            surname TEXT,
            phone TEXT,
            gpa REAL
        )
    """)
    conn.commit()
    conn.close()

def is_only_russian(s: str) -> bool:
    if not s:
        return True
    pattern = r'^[а-яА-ЯёЁ]+$'
    return bool(re.fullmatch(pattern, s))

def is_valid_phone(s: str) -> bool:
    if not s:
        return True
    pattern = r'^\+?[0-9]*$'
    return bool(re.fullmatch(pattern, s)) and len(s) <= 13

def is_valid_gpa(s: str) -> bool:
    if not s:
        return True
    pattern = r'^[0-9]*\.?[0-9]*$'
    return bool(re.fullmatch(pattern, s))

def submit_data():
    name = entry_name.get()
    surname = entry_surname.get()
    phone = entry_phone.get()
    gpa_str = entry_gpa.get()

    if not name or not surname or not phone or not gpa_str:
        label_result["text"] = "Ошибка: заполните все поля!"
        return

    if not re.fullmatch(r'^[а-яА-ЯёЁ]+$', name) or not re.fullmatch(r'^[а-яА-ЯёЁ]+$', surname):
        label_result["text"] = "Ошибка: Имя и Фамилия должны содержать только кириллицу!"
        return

    phone_pattern = r'^\+375(29|33|44|25)\d{7}$'
    if not re.fullmatch(phone_pattern, phone):
        label_result["text"] = "Ошибка: Телефон должен быть в формате +375291234567!"
        return

    try:
        gpa = float(gpa_str)
        if not (0.0 <= gpa <= 10.0):
            raise ValueError()
    except ValueError:
        label_result["text"] = "Ошибка: Балл должен быть числом от 0.0 до 10!"
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO students (name, surname, phone, gpa) VALUES (?, ?, ?, ?)", (name, surname, phone, gpa))
        conn.commit()
        conn.close()
        label_result["text"] = f"Успешно сохранено в БД! Студент: {surname} {name}"
    except Exception as e:
        label_result["text"] = f"Ошибка базы данных: {e}"

def search_student():
    surname_to_search = entry_surname.get()
    if not surname_to_search:
        label_result["text"] = "Ошибка: введите фамилию для поиска!"
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name, surname, phone, gpa FROM students WHERE surname = ?", (surname_to_search,))
        rows = cursor.fetchall()
        conn.close()

        if rows:
            result_text = f"Найдено записей: {len(rows)}\n"
            for row in rows:
                result_text += f"{row[1]} {row[0]}, Тел: {row[2]}, Балл: {row[3]}\n"
            label_result["text"] = result_text
        else:
            label_result["text"] = "Студенты с такой фамилией не найдены."
    except Exception as e:
        label_result["text"] = f"Ошибка поиска: {e}"

def clear_all():
    entry_name.delete(0, END)
    entry_surname.delete(0, END)
    entry_phone.delete(0, END)
    entry_gpa.delete(0, END)
    label_result["text"] = ""

init_db()

root = Tk()
root.title("База данных студентов")
root.geometry("380x480")

main_menu = Menu()
file_menu = Menu()
file_menu.add_command(label="Запись в базу", command=submit_data)
file_menu.add_command(label="Поиск по фамилии", command=search_student)
file_menu.add_separator()
file_menu.add_command(label="Выход", command=root.quit)
main_menu.add_cascade(label="Файл", menu=file_menu)
main_menu.add_cascade(label="Редактировать")
main_menu.add_cascade(label="Вид")
root.config(menu=main_menu)

Label(text="Имя (кириллица):").pack(anchor=NW, padx=10, pady=(10, 0))
check_name = (root.register(is_only_russian), "%P")
entry_name = Entry(validate="key", validatecommand=check_name, width=32)
entry_name.pack(anchor=NW, padx=10, pady=5)

Label(text="Фамилия (кириллица):").pack(anchor=NW, padx=10, pady=5)
check_surname = (root.register(is_only_russian), "%P")
entry_surname = Entry(validate="key", validatecommand=check_surname, width=32)
entry_surname.pack(anchor=NW, padx=10, pady=5)

Label(text="Телефон (+375...):").pack(anchor=NW, padx=10, pady=5)
check_phone = (root.register(is_valid_phone), "%P")
entry_phone = Entry(validate="key", validatecommand=check_phone, width=32)
entry_phone.pack(anchor=NW, padx=10, pady=5)

Label(text="Средний балл (0.0 - 10):").pack(anchor=NW, padx=10, pady=5)
check_gpa = (root.register(is_valid_gpa), "%P")
entry_gpa = Entry(validate="key", validatecommand=check_gpa, width=32)
entry_gpa.pack(anchor=NW, padx=10, pady=5)

btn_submit = Button(text="Запись в базу", command=submit_data, width=15, bg="#d0f0c0")
btn_submit.pack(anchor=NW, padx=10, pady=10)

btn_search = Button(text="Поиск по фамилии", command=search_student, width=15, bg="#d0e0ff")
btn_search.pack(anchor=NW, padx=10, pady=0)

btn_clear = Button(text="Очистить", command=clear_all, width=15, bg="#ffd1d1")
btn_clear.pack(anchor=NW, padx=10, pady=10)

label_result = Label(text="", fg="blue", wraplength=350, justify=LEFT)
label_result.pack(anchor=NW, padx=10, pady=5)

root.mainloop()