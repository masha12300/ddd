import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from windows.products_window import ProductsWindow

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Авторизация - Магазин игрушек")
        self.geometry("400x350")
        
        # Установка цвета фона (по заданию: #FFFFFF)
        self.configure(fg_color="#FFFFFF")
        
        # Заголовок
        self.title_label = ctk.CTkLabel(
            self, 
            text="Добро пожаловать!", 
            font=("Comic Sans MS", 20, "bold"),
            text_color="#000000"
        )
        self.title_label.pack(pady=20)
        
        # Поле для логина
        self.login_entry = ctk.CTkEntry(
            self, 
            placeholder_text="Логин",
            width=250,
            height=40,
            font=("Comic Sans MS", 14)
        )
        self.login_entry.pack(pady=10)
        
        # Поле для пароля
        self.password_entry = ctk.CTkEntry(
            self, 
            placeholder_text="Пароль",
            show="*",
            width=250,
            height=40,
            font=("Comic Sans MS", 14)
        )
        self.password_entry.pack(pady=10)
        
        # Кнопка "Войти" (цвет акцента: #546F94)
        self.login_button = ctk.CTkButton(
            self,
            text="Войти",
            command=self.login,
            width=250,
            height=40,
            fg_color="#546F94",
            hover_color="#3D5A7A",
            font=("Comic Sans MS", 14)
        )
        self.login_button.pack(pady=10)
        
        # Кнопка "Продолжить как гость"
        self.guest_button = ctk.CTkButton(
            self,
            text="Продолжить как гость",
            command=self.guest_login,
            width=250,
            height=40,
            fg_color="#ABCFFC",
            text_color="#000000",
            hover_color="#8BB3D6",
            font=("Comic Sans MS", 12)
        )
        self.guest_button.pack(pady=5)
        
        # Надпись с подсказкой
        self.hint_label = ctk.CTkLabel(
            self,
            text="Тестовый вход: admin / admin123",
            font=("Comic Sans MS", 10),
            text_color="gray"
        )
        self.hint_label.pack(pady=20)
    
    def login(self):
        login = self.login_entry.get()
        password = self.password_entry.get()
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, full_name, role FROM users WHERE login=? AND password=?',
            (login, password)
        )
        user = cursor.fetchone()
        conn.close()
        
        if user:
            user_id, full_name, role = user
            self.destroy()
            app = ProductsWindow(user_id, full_name, role)
            app.mainloop()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")
    
    def guest_login(self):
        self.destroy()
        app = ProductsWindow(None, "Гость", "guest")
        app.mainloop()