import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class OrdersWindow(ctk.CTkToplevel):
    def __init__(self, parent, role):
        super().__init__(parent)
        
        self.attributes('-topmost', True)
        self.transient(parent)
        self.role = role
        self.title("Управление заказами")
        self.geometry("900x500")
        self.configure(fg_color="#FFFFFF")
        
        #таблица заказов
        self.tree_frame = ctk.CTkFrame(self, fg_color="#FFFFFF")
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        columns = ('id', 'article', 'status', 'pickup_address', 'order_date', 'issue_date')
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show='headings')
        
        self.tree.heading('id', text='ID')
        self.tree.heading('article', text='Артикул')
        self.tree.heading('status', text='Статус')
        self.tree.heading('pickup_address', text='Адрес выдачи')
        self.tree.heading('order_date', text='Дата заказа')
        self.tree.heading('issue_date', text='Дата выдачи')
        
        for col in columns:
            self.tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.load_orders()
        
        #кнопки для админа
        if role == 'admin':
            self.button_frame = ctk.CTkFrame(self, fg_color="#FFFFFF")
            self.button_frame.pack(fill="x", padx=10, pady=10)
            
            self.add_button = ctk.CTkButton(
                self.button_frame,
                text="Добавить заказ",
                command=self.add_order,
                fg_color="#546F94",
                hover_color="#3D5A7A",
                font=("Comic Sans MS", 12)
            )
            self.add_button.pack(side="left", padx=5)
            
            self.edit_button = ctk.CTkButton(
                self.button_frame,
                text="Редактировать",
                command=self.edit_order,
                fg_color="#546F94",
                hover_color="#3D5A7A",
                font=("Comic Sans MS", 12)
            )
            self.edit_button.pack(side="left", padx=5)
            
            self.delete_button = ctk.CTkButton(
                self.button_frame,
                text="Удалить",
                command=self.delete_order,
                fg_color="#546F94",
                hover_color="#3D5A7A",
                font=("Comic Sans MS", 12)
            )
            self.delete_button.pack(side="left", padx=5)
            
            self.tree.bind('<Double-1>', lambda e: self.edit_order())
        
        self.back_button = ctk.CTkButton(
            self.button_frame if role == 'admin' else self,
            text="Назад",
            command=self.destroy,
            fg_color="#ABCFFC",
            text_color="#000000",
            hover_color="#8BB3D6",
            font=("Comic Sans MS", 12)
        )
        self.back_button.pack(side="right", padx=5)
    
    def load_orders(self):
        """Загружает заказы в таблицу"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders')
        orders = cursor.fetchall()
        conn.close()
        
        for order in orders:
            self.tree.insert('', 'end', values=order)
    
    def add_order(self):
        """Добавление заказа (простая форма)"""
        self.open_order_form()
    
    def edit_order(self):
        """Редактирование выбранного заказа"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите заказ для редактирования")
            return
        
        order_id = self.tree.item(selected[0])['values'][0]
        self.open_order_form(order_id)
    
    def delete_order(self):
        """Удаление заказа"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите заказ для удаления")
            return
        
        order_id = self.tree.item(selected[0])['values'][0]
        
        if messagebox.askyesno("Подтверждение", "Удалить заказ?"):
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('DELETE FROM order_products WHERE order_id=?', (order_id,))
            cursor.execute('DELETE FROM orders WHERE id=?', (order_id,))
            conn.commit()
            conn.close()
            self.load_orders()
    
    def open_order_form(self, order_id=None):
        """Открывает форму для добавления/редактирования заказа"""
        form = ctk.CTkToplevel(self)
        form.attributes('-topmost', True)
        form.transient(self) 
        form.grab_set() 
        form.title("Добавление заказа" if not order_id else "Редактирование заказа")
        form.geometry("500x450")
        form.configure(fg_color="#FFFFFF")
        
        #артикул
        ctk.CTkLabel(form, text="Артикул:", font=("Comic Sans MS", 12)).pack(anchor="w", padx=20, pady=5)
        article_entry = ctk.CTkEntry(form, width=400, font=("Comic Sans MS", 12))
        article_entry.pack(padx=20, pady=5)
        
        #статус
        ctk.CTkLabel(form, text="Статус:", font=("Comic Sans MS", 12)).pack(anchor="w", padx=20, pady=5)
        status_var = ctk.StringVar(value="Новый")
        status_combo = ctk.CTkComboBox(
            form, values=["Новый", "В обработке", "Выдан"],
            variable=status_var, width=400, font=("Comic Sans MS", 12)
        )
        status_combo.pack(padx=20, pady=5)
        
        #адрес выдачи
        ctk.CTkLabel(form, text="Адрес пункта выдачи:", font=("Comic Sans MS", 12)).pack(anchor="w", padx=20, pady=5)
        address_entry = ctk.CTkEntry(form, width=400, font=("Comic Sans MS", 12))
        address_entry.pack(padx=20, pady=5)
        
        #дата заказа
        ctk.CTkLabel(form, text="Дата заказа (ГГГГ-ММ-ДД):", font=("Comic Sans MS", 12)).pack(anchor="w", padx=20, pady=5)
        order_date_entry = ctk.CTkEntry(form, width=400, font=("Comic Sans MS", 12), placeholder_text=datetime.now().strftime("%Y-%m-%d"))
        order_date_entry.pack(padx=20, pady=5)
        
        #дата выдачи
        ctk.CTkLabel(form, text="Дата выдачи (ГГГГ-ММ-ДД):", font=("Comic Sans MS", 12)).pack(anchor="w", padx=20, pady=5)
        issue_date_entry = ctk.CTkEntry(form, width=400, font=("Comic Sans MS", 12))
        issue_date_entry.pack(padx=20, pady=5)
        
        #если редактируем — загружаем данные
        if order_id:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM orders WHERE id=?', (order_id,))
            order = cursor.fetchone()
            conn.close()
            if order:
                article_entry.insert(0, order[1])
                status_var.set(order[2])
                address_entry.insert(0, order[3])
                order_date_entry.insert(0, order[4])
                if order[5]:
                    issue_date_entry.insert(0, order[5])
        
        #кнопки
        btn_frame = ctk.CTkFrame(form, fg_color="#FFFFFF")
        btn_frame.pack(pady=20)
        
        def save():
            article = article_entry.get()
            status = status_var.get()
            address = address_entry.get()
            order_date = order_date_entry.get()
            issue_date = issue_date_entry.get() if issue_date_entry.get() else None
            
            if not article or not address:
                messagebox.showerror("Ошибка", "Заполните артикул и адрес выдачи")
                return
            
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            
            if order_id:
                cursor.execute('''
                    UPDATE orders SET article=?, status=?, pickup_address=?, order_date=?, issue_date=?
                    WHERE id=?
                ''', (article, status, address, order_date, issue_date, order_id))
            else:
                cursor.execute('''
                    INSERT INTO orders (article, status, pickup_address, order_date, issue_date)
                    VALUES (?,?,?,?,?)
                ''', (article, status, address, order_date, issue_date))
            
            conn.commit()
            conn.close()
            
            self.load_orders()
            form.destroy()
            messagebox.showinfo("Успех", "Заказ сохранён")
        
        ctk.CTkButton(btn_frame, text="Сохранить", command=save, fg_color="#546F94", font=("Comic Sans MS", 12), width=120).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Отмена", command=form.destroy, fg_color="#ABCFFCE", text_color="#000000", font=("Comic Sans MS", 12), width=120).pack(side="left", padx=10)