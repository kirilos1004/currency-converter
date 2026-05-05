# Импорт библиотек
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json

# Список валют
currencies = ["USD", "EUR", "RUB", "GBP", "JPY"]

# Файл истории
HISTORY_FILE = "history.json"


# Загрузка истории из JSON
def load_history():
    try:
        with open(HISTORY_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


# Сохранение истории
def save_history(data):
    with open(HISTORY_FILE, "w") as file:
        json.dump(data, file, indent=4)


# Основная функция конвертации
def convert_currency():
    amount = entry_amount.get().strip()

    # Проверка ввода
    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Ошибка", "Введите положительное число")
        return

    from_cur = combo_from.get()
    to_cur = combo_to.get()

    # Если валюты одинаковые
    if from_cur == to_cur:
        label_result.config(text=f"Результат: {amount} {to_cur}")
        return

    # API запрос
    url = f"https://api.exchangerate-api.com/v4/latest/{from_cur}"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # проверка HTTP ошибок

        data = response.json()

        rate = data["rates"][to_cur]
        result = amount * rate

        label_result.config(text=f"Результат: {round(result, 2)} {to_cur}")

        # Сохранение в историю
        history = load_history()
        record = f"{amount} {from_cur} → {round(result, 2)} {to_cur}"
        history.append(record)
        save_history(history)

        update_table()

    except requests.exceptions.Timeout:
        messagebox.showerror("Ошибка", "Превышено время ожидания")
    except requests.exceptions.ConnectionError:
        messagebox.showerror("Ошибка", "Нет подключения к интернету")
    except requests.exceptions.HTTPError:
        messagebox.showerror("Ошибка", "Ошибка сервера API")
    except requests.exceptions.RequestException:
        messagebox.showerror("Ошибка", "Ошибка при запросе к API")
    except KeyError:
        messagebox.showerror("Ошибка", "Ошибка данных от API")


# Обновление таблицы
def update_table():
    for row in table.get_children():
        table.delete(row)

    history = load_history()

    for item in history:
        table.insert("", tk.END, values=(item,))


# ================= GUI =================

root = tk.Tk()
root.title("Currency Converter")
root.geometry("400x420")

# Поле ввода суммы
entry_amount = tk.Entry(root)
entry_amount.pack(pady=5)

# Выбор валют
combo_from = ttk.Combobox(root, values=currencies, state="readonly")
combo_from.set("USD")
combo_from.pack(pady=5)

combo_to = ttk.Combobox(root, values=currencies, state="readonly")
combo_to.set("EUR")
combo_to.pack(pady=5)

# Кнопка конвертации
btn = tk.Button(root, text="Конвертировать", command=convert_currency)
btn.pack(pady=10)

# Результат
label_result = tk.Label(root, text="Результат:")
label_result.pack(pady=5)

# Таблица истории
table = ttk.Treeview(root, columns=("History"), show="headings")
table.heading("History", text="История")
table.pack(pady=10)

# Загрузка истории при запуске
update_table()

# Запуск приложения
root.mainloop()
