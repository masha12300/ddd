import customtkinter as ctk
from tkinter import messagebox, filedialog
import sqlite3
import os
from PIL import Image
from windows.product_form import ProductForm
from windows.orders_window import OrdersWindow
from database import import_products_from_excel, import_users_from_excel, import_orders_from_excel

class ProductsWindow(ctk.CTk):
    def __init__(self, user_id, full_name, role):
        super().__init__()
        
        self.user_id = user_id
        self.full_name = full_name
        self.role = role 
        self.product_cards = {}
        
        self.title(f"Магазин игрушек - {full_name if full_name else 'Гость'}")
        self.geometry("1300x700")
        self.configure(fg_color="#FFFFFF")
        
        #ФИО в правом углу
        self.user_label = ctk.CTkLabel(
            self,
            text=f"Пользователь: {full_name if full_name else 'Гость'}",
            font=("Arial", 12),
            fg_color="#ABCFFC",
            corner_radius=10,
            padx=10,
            pady=5
        )
        self.user_label.pack(anchor="ne", padx=10, pady=10)
        
        #поиск и фильтры только для менеджера и админа
        if role in ['manager', 'admin']:
            self.create_search_filters()
        
        #контейнер для карточек товаров
        self.products_container = ctk.CTkScrollableFrame(
            self, 
            fg_color="#FFFFFF",
            orientation="vertical"
        )
        self.products_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        #кнопки управления
        self.create_buttons()
        
        #загружаем товары
        self.load_products()
    
    def get_suppliers_list(self):
        """Получает список поставщиков для фильтра (с пунктом 'Все поставщики')"""
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM suppliers ORDER BY name')
        suppliers = ['Все поставщики'] + [row[0] for row in cursor.fetchall()]
        conn.close()
        return suppliers
    
    def create_search_filters(self):
        """Создаёт панель поиска и фильтров (только для менеджера и админа)"""
        self.search_frame = ctk.CTkFrame(self, fg_color="#ABCFFC", corner_radius=10)
        self.search_frame.pack(fill="x", padx=10, pady=5)
        
        #поиск
        ctk.CTkLabel(self.search_frame, text="Поиск:", font=("Arial", 12)).pack(side="left", padx=5)
        self.search_entry = ctk.CTkEntry(self.search_frame, width=300, font=("Arial", 12), placeholder_text="Название, категория, описание...")
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind('<KeyRelease>', lambda e: self.load_products())
        
        #фильтр по поставщику
        ctk.CTkLabel(self.search_frame, text="Поставщик:", font=("Arial", 12)).pack(side="left", padx=20)
        self.supplier_var = ctk.StringVar(value="Все поставщики")
        self.supplier_combo = ctk.CTkComboBox(
            self.search_frame,
            values=self.get_suppliers_list(),
            variable=self.supplier_var,
            width=200,
            font=("Arial", 12),
            command=lambda e: self.load_products()
        )
        self.supplier_combo.pack(side="left", padx=5)
        
        #сортировка
        ctk.CTkLabel(self.search_frame, text="Сортировка:", font=("Arial", 12)).pack(side="left", padx=20)
        self.sort_var = ctk.StringVar(value="Без сортировки")
        self.sort_combo = ctk.CTkComboBox(
            self.search_frame,
            values=["Без сортировки", "Цена ↑", "Цена ↓", "Количество ↑", "Количество ↓"],
            variable=self.sort_var,
            width=150,
            font=("Arial", 12),
            command=lambda e: self.load_products()
        )
        self.sort_combo.pack(side="left", padx=5)
    
    def create_buttons(self):
        """Создаёт кнопки управления"""
        self.button_frame = ctk.CTkFrame(self, fg_color="#FFFFFF")
        self.button_frame.pack(fill="x", padx=10, pady=10)
        
        if self.role == 'admin':
            ctk.CTkButton(self.button_frame, text="Добавить товар", command=self.add_product, fg_color="#546F94").pack(side="left", padx=5)
            ctk.CTkButton(self.button_frame, text="Импорт товаров", command=self.import_products, fg_color="#546F94").pack(side="left", padx=5)
            ctk.CTkButton(self.button_frame, text="Импорт пользователей", command=self.import_users, fg_color="#546F94").pack(side="left", padx=5)
            ctk.CTkButton(self.button_frame, text="Импорт заказов", command=self.import_orders, fg_color="#546F94").pack(side="left", padx=5)
            ctk.CTkButton(self.button_frame, text="Заказы", command=self.open_orders, fg_color="#546F94").pack(side="left", padx=5)
        
        elif self.role == 'manager':
            ctk.CTkButton(self.button_frame, text="Заказы", command=self.open_orders, fg_color="#546F94").pack(side="left", padx=5)
        
        #кнопка назад
        ctk.CTkButton(self.button_frame, text="Выход", command=self.logout, fg_color="#ABCFFC", text_color="#000000").pack(side="right", padx=5)
    
    def load_products(self):
        """Загружает товары и создаёт карточки"""
        for widget in self.products_container.winfo_children():
            widget.destroy()
        self.product_cards.clear()
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        #для гостя и клиента 
        if self.role in ['guest', 'client']:
            query = '''
                SELECT p.id, p.name, p.category, p.description, p.manufacturer, 
                       s.name as supplier_name, p.price, p.unit, p.quantity, p.discount, p.image_path
                FROM products p
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                ORDER BY p.name
            '''
            cursor.execute(query)
        else:
            #для менеджера и админа
            query = '''
                SELECT p.id, p.name, p.category, p.description, p.manufacturer, 
                       s.name as supplier_name, p.price, p.unit, p.quantity, p.discount, p.image_path
                FROM products p
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                WHERE 1=1
            '''
            params = []
            
            #поиск
            if hasattr(self, 'search_entry') and self.search_entry.get():
                search = f"%{self.search_entry.get()}%"
                query += ' AND (p.name LIKE ? OR p.category LIKE ? OR p.description LIKE ? OR p.manufacturer LIKE ?)'
                params.extend([search, search, search, search])
            
            #фильтр по поставщику 
            if hasattr(self, 'supplier_var') and self.supplier_var.get() and self.supplier_var.get() != "Все поставщики":
                query += ' AND s.name = ?'
                params.append(self.supplier_var.get())
            
            #сортировка
            if hasattr(self, 'sort_var') and self.sort_var.get():
                if self.sort_var.get() == "Цена ↑":
                    query += ' ORDER BY p.price ASC'
                elif self.sort_var.get() == "Цена ↓":
                    query += ' ORDER BY p.price DESC'
                elif self.sort_var.get() == "Количество ↑":
                    query += ' ORDER BY p.quantity ASC'
                elif self.sort_var.get() == "Количество ↓":
                    query += ' ORDER BY p.quantity DESC'
                else:
                    query += ' ORDER BY p.name'
            else:
                query += ' ORDER BY p.name'
            
            cursor.execute(query, params)
        
        rows = cursor.fetchall()
        conn.close()
        
        #создаём карточки товаров
        for idx, row in enumerate(rows):
            product_id, name, category, description, manufacturer, supplier_name, price, unit, quantity, discount, image_path = row
            
            card = self.create_product_card(
                product_id, name, category, description, manufacturer, 
                supplier_name, price, unit, quantity, discount, image_path
            )
            
            row_num = idx // 2
            col_num = idx % 2
            card.grid(row=row_num, column=col_num, padx=15, pady=10, sticky="nsew")
            
            self.products_container.grid_columnconfigure(0, weight=1)
            self.products_container.grid_columnconfigure(1, weight=1)            
            self.product_cards[product_id] = card
    
    def create_product_card(self, product_id, name, category, description, manufacturer, supplier_name, price, unit, quantity, discount, image_path):
        """Создаёт карточку товара с горизонтальным расположением"""
        
        card = ctk.CTkFrame(
            self.products_container,
            fg_color="#F0F0F0",
            corner_radius=10,
            border_width=1,
            border_color="#ABCFFC",
            width=550  
        )
        card.pack_propagate(False)  
        card.configure(height=180)   
        
        #подсветка фона
        if quantity == 0:
            card.configure(fg_color="#ADD8E6")  
        elif discount > 17:
            card.configure(fg_color="#FFDEAD")  
        
        left_frame = ctk.CTkFrame(card, fg_color="transparent", width=120, height=160)
        left_frame.pack(side="left", padx=10, pady=10)
        left_frame.pack_propagate(False)
        
        photo_image = self.load_photo(image_path)
        if photo_image:
            photo_label = ctk.CTkLabel(left_frame, image=photo_image, text="")
            photo_label.image = photo_image
            photo_label.pack(expand=True)
        else:
            placeholder_img = self.load_placeholder()
            if placeholder_img:
                photo_label = ctk.CTkLabel(left_frame, image=placeholder_img, text="")
                photo_label.image = placeholder_img
                photo_label.pack(expand=True)
            else:
                placeholder = ctk.CTkLabel(left_frame, text="Нет фото", font=("Arial", 10))
                placeholder.pack(expand=True)
        
        center_frame = ctk.CTkFrame(card, fg_color="transparent")
        center_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            center_frame, 
            text=name, 
            font=("Arial", 13, "bold"),
            anchor="w",
            justify="left",
            wraplength=280
        ).pack(anchor="w", pady=(0, 5))
        
        ctk.CTkLabel(
            center_frame, 
            text=f"Категория: {category}", 
            font=("Arial", 11),
            text_color="gray",
            anchor="w"
        ).pack(anchor="w", pady=(0, 3))
        
        if manufacturer:
            ctk.CTkLabel(
                center_frame, 
                text=f"Производитель: {manufacturer}", 
                font=("Arial", 10),
                text_color="#555555",
                anchor="w"
            ).pack(anchor="w", pady=(0, 2))
        
        if supplier_name:
            ctk.CTkLabel(
                center_frame, 
                text=f"Поставщик: {supplier_name}", 
                font=("Arial", 10),
                text_color="#555555",
                anchor="w"
            ).pack(anchor="w", pady=(0, 2))
        
        if description:
            desc_text = description[:80] + "..." if len(description) > 80 else description
            ctk.CTkLabel(
                center_frame, 
                text=desc_text, 
                font=("Arial", 9),
                text_color="#777777",
                anchor="w",
                wraplength=280,
                justify="left"
            ).pack(anchor="w", pady=(0, 3))
        
        if discount > 0:
            final_price = price * (100 - discount) / 100
            price_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
            price_frame.pack(anchor="w", pady=(5, 0))
            
            old_price_label = ctk.CTkLabel(
                price_frame,
                text=f"{price:.2f} руб.",
                font=("Arial", 10),
                text_color="red"
            )
            old_price_label.pack(side="left", padx=(0, 5))
            old_price_label.configure(font=("Arial", 10, "overstrike"))
            
            ctk.CTkLabel(
                price_frame,
                text=f"{final_price:.2f} руб.",
                font=("Arial", 13, "bold"),
                text_color="black"
            ).pack(side="left")
        else:
            ctk.CTkLabel(
                center_frame,
                text=f"{price:.2f} руб.",
                font=("Arial", 13, "bold"),
                text_color="black",
                anchor="w"
            ).pack(anchor="w", pady=(5, 0))
        
        bottom_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        bottom_frame.pack(anchor="w", pady=(5, 0))
        
        qty_color = "red" if quantity == 0 else "black"
        ctk.CTkLabel(
            bottom_frame, 
            text=f"{quantity} {unit}", 
            font=("Arial", 11),
            text_color=qty_color
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(
            bottom_frame, 
            text=f"Ед.изм.: {unit}", 
            font=("Arial", 10),
            text_color="#555555"
        ).pack(side="left")
        
        right_frame = ctk.CTkFrame(card, fg_color="transparent", width=80, height=160)
        right_frame.pack(side="right", padx=10, pady=10)
        right_frame.pack_propagate(False)
        
        if discount > 0:
            ctk.CTkLabel(
                right_frame,
                text=f"{discount:.0f}%",
                font=("Arial", 22, "bold"),
                text_color="orange"
            ).pack(expand=True, pady=(0, 5))
            
            ctk.CTkLabel(
                right_frame,
                text="СКИДКА",
                font=("Arial", 9, "bold"),
                text_color="orange"
            ).pack()
        else:
            ctk.CTkLabel(
                right_frame,
                text="0%",
                font=("Arial", 18, "bold"),
                text_color="gray"
            ).pack(expand=True)
        
        if self.role == 'admin':
            button_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
            button_frame.pack(side="bottom", pady=5)
            
            ctk.CTkButton(
                button_frame,
                text="Ред.",
                width=45,
                height=28,
                fg_color="#546F94",
                font=("Arial", 10),
                command=lambda pid=product_id: self.edit_product_by_id(pid)
            ).pack(side="left", padx=2)
            
            ctk.CTkButton(
                button_frame,
                text="Уд.",
                width=45,
                height=28,
                fg_color="#FF6B6B",
                font=("Arial", 10),
                command=lambda pid=product_id: self.delete_product_by_id(pid)
            ).pack(side="left", padx=2)
        
        if self.role == 'admin':
            for widget in [card, left_frame, center_frame, right_frame]:
                widget.bind("<Double-Button-1>", lambda e, pid=product_id: self.edit_product_by_id(pid))
        
        return card
    
    def load_photo(self, image_path):
        """Загружает фото из файла"""
        if image_path and os.path.exists(image_path):
            try:
                img = Image.open(image_path)
                img = img.resize((100, 100))
                return ctk.CTkImage(light_image=img, dark_image=img, size=(100, 100))
            except:
                return None
        return None
    
    def load_placeholder(self):
        """Загружает картинку-заглушку"""
        placeholder_path = 'images/picture.png'
        if os.path.exists(placeholder_path):
            try:
                img = Image.open(placeholder_path)
                img = img.resize((150, 150))
                return ctk.CTkImage(light_image=img, dark_image=img, size=(150, 150))
            except:
                pass
        return None
    
    def edit_product_by_id(self, product_id):
        ProductForm.open_edit_form(self, self.load_products, product_id)
    
    def delete_product_by_id(self, product_id):
        if not messagebox.askyesno("Подтверждение", "Удалить товар?"):
            return
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM order_products WHERE product_id=?', (product_id,))
        if cursor.fetchone()[0] > 0:
            messagebox.showerror("Ошибка", "Нельзя удалить товар, который есть в заказах")
            conn.close()
            return
        
        cursor.execute('DELETE FROM products WHERE id=?', (product_id,))
        conn.commit()
        conn.close()
        self.load_products()
        messagebox.showinfo("Успех", "Товар удалён")
    
    def add_product(self):
        ProductForm.open_edit_form(self, self.load_products)
    
    def import_products(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx")])
        if file_path:
            count = import_products_from_excel(file_path)
            self.load_products()
            messagebox.showinfo("Импорт", f"Импортировано товаров: {count}")
    
    def import_users(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx")])
        if file_path:
            count = import_users_from_excel(file_path)
            messagebox.showinfo("Импорт", f"Импортировано пользователей: {count}")
    
    def import_orders(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx")])
        if file_path:
            count = import_orders_from_excel(file_path)
            messagebox.showinfo("Импорт", f"Импортировано заказов: {count}")
    
    def open_orders(self):
        OrdersWindow(self, self.role)
    
    def logout(self):
        self.destroy()
        from windows.login_window import LoginWindow
        LoginWindow().mainloop()