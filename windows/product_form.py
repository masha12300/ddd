import customtkinter as ctk
from tkinter import messagebox, filedialog
import sqlite3
import shutil
import os
from PIL import Image

class ProductForm(ctk.CTkToplevel):
    _edit_window = None
    
    @classmethod
    def open_edit_form(cls, parent, callback, product_id=None):
        """Открывает форму редактирования (только одну)"""
        if cls._edit_window is not None and cls._edit_window.winfo_exists():
            messagebox.showwarning("Внимание", "Окно редактирования уже открыто")
            return
        cls._edit_window = cls(parent, callback, product_id)
        cls._edit_window.protocol("WM_DELETE_WINDOW", cls.close_edit_window)
    
    @classmethod
    def close_edit_window(cls):
        """Закрывает окно редактирования"""
        if cls._edit_window is not None:
            cls._edit_window.destroy()
            cls._edit_window = None

    def __init__(self, parent, refresh_callback, product_id=None):
        super().__init__(parent)

        self.attributes('-topmost', True)  
        self.transient(parent)  
        self.grab_set()
        
        self.parent = parent
        self.refresh_callback = refresh_callback
        self.product_id = product_id
        self.image_path = ""
        self.old_image_path = ""  
        
        self.title("Добавление товара" if not product_id else "Редактирование товара")
        self.geometry("500x750")
        self.configure(fg_color="#FFFFFF")
        
        self.create_form_fields()
        
        if product_id:
            self.load_product_data()
        
        self.button_frame = ctk.CTkFrame(self, fg_color="#FFFFFF")
        self.button_frame.pack(pady=20)
        
        self.save_button = ctk.CTkButton(
            self.button_frame,
            text="Сохранить",
            command=self.save_product,
            fg_color="#546F94",
            hover_color="#3D5A7A",
            font=("Arial", 12),
            width=120
        )
        self.save_button.pack(side="left", padx=10)
        
        self.cancel_button = ctk.CTkButton(
            self.button_frame,
            text="Отмена",
            command=self.destroy,
            fg_color="#ABCFFC",
            text_color="#000000",
            hover_color="#8BB3D6",
            font=("Arial", 12),
            width=120
        )
        self.cancel_button.pack(side="left", padx=10)
    
    def get_categories_list(self):
        """Получает уникальные категории из БД"""
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT category FROM products WHERE category IS NOT NULL AND category != "" ORDER BY category')
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        #если категорий нет добавляем стандартные
        if not categories:
            categories = ["Игровой набор", "Конструктор", "Машинка", "Детский музыкальный инструмент"]
        
        return categories
    
    def get_suppliers_list(self):
        """Получает список поставщиков из БД"""
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM suppliers ORDER BY name')
        suppliers = [row[0] for row in cursor.fetchall()]
        conn.close()
        return suppliers
    
    def create_form_fields(self):
        """Создаёт все поля формы"""
        self.main_frame = ctk.CTkScrollableFrame(self, fg_color="#FFFFFF")
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        #наименование
        ctk.CTkLabel(self.main_frame, text="Наименование:", font=("Arial", 12)).pack(anchor="w", pady=2)
        self.name_entry = ctk.CTkEntry(self.main_frame, width=400, font=("Arial", 12))
        self.name_entry.pack(pady=5, fill="x")
        
        #категория (выпадающий список)
        ctk.CTkLabel(self.main_frame, text="Категория:", font=("Arial", 12)).pack(anchor="w", pady=2)
        self.category_var = ctk.StringVar()
        self.category_combo = ctk.CTkComboBox(
            self.main_frame,
            values=self.get_categories_list(),
            variable=self.category_var,
            width=400,
            font=("Arial", 12)
        )
        self.category_combo.pack(pady=5, fill="x")
        
        #артикул 
        ctk.CTkLabel(self.main_frame, text="Артикул:", font=("Arial", 12)).pack(anchor="w", pady=2)
        self.article_entry = ctk.CTkEntry(self.main_frame, width=400, font=("Arial", 12), placeholder_text="Уникальный артикул товара")
        self.article_entry.pack(pady=5, fill="x")
        
        #описание
        ctk.CTkLabel(self.main_frame, text="Описание:", font=("Arial", 12)).pack(anchor="w", pady=2)
        self.description_text = ctk.CTkTextbox(self.main_frame, height=80, width=400, font=("Arial", 12))
        self.description_text.pack(pady=5, fill="x")
        
        #производитель
        ctk.CTkLabel(self.main_frame, text="Производитель:", font=("Arial", 12)).pack(anchor="w", pady=2)
        self.manufacturer_entry = ctk.CTkEntry(self.main_frame, width=400, font=("Arial", 12))
        self.manufacturer_entry.pack(pady=5, fill="x")
        
        #поставщик тоже список
        ctk.CTkLabel(self.main_frame, text="Поставщик:", font=("Arial", 12)).pack(anchor="w", pady=2)
        self.supplier_var = ctk.StringVar()
        self.supplier_combo = ctk.CTkComboBox(
            self.main_frame,
            values=self.get_suppliers_list(),
            variable=self.supplier_var,
            width=400,
            font=("Arial", 12)
        )
        self.supplier_combo.pack(pady=5, fill="x")
        
        #цена
        ctk.CTkLabel(self.main_frame, text="Цена:", font=("Arial", 12)).pack(anchor="w", pady=2)
        self.price_entry = ctk.CTkEntry(self.main_frame, width=400, font=("Arial", 12))
        self.price_entry.pack(pady=5, fill="x")
        
        #ед измерения
        ctk.CTkLabel(self.main_frame, text="Единица измерения:", font=("Arial", 12)).pack(anchor="w", pady=2)
        self.unit_entry = ctk.CTkEntry(self.main_frame, width=400, font=("Arial", 12), placeholder_text="шт, кг, л...")
        self.unit_entry.pack(pady=5, fill="x")
        
        #кол на складе
        ctk.CTkLabel(self.main_frame, text="Количество на складе:", font=("Arial", 12)).pack(anchor="w", pady=2)
        self.quantity_entry = ctk.CTkEntry(self.main_frame, width=400, font=("Arial", 12))
        self.quantity_entry.pack(pady=5, fill="x")
        
        #скидка
        ctk.CTkLabel(self.main_frame, text="Скидка (%):", font=("Arial", 12)).pack(anchor="w", pady=2)
        self.discount_entry = ctk.CTkEntry(self.main_frame, width=400, font=("Arial", 12), placeholder_text="0-100")
        self.discount_entry.pack(pady=5, fill="x")
        
        #кнопка выбора изображения
        self.image_button = ctk.CTkButton(
            self.main_frame,
            text="Выбрать изображение",
            command=self.select_image,
            fg_color="#ABCFFC",
            text_color="#000000",
            hover_color="#8BB3D6",
            font=("Arial", 12)
        )
        self.image_button.pack(pady=10)
        
        #поле для отображения фото
        self.photo_label = ctk.CTkLabel(self.main_frame, text="", width=100, height=100)
        self.photo_label.pack(pady=10)
        
        #подсказка по размеру фото
        ctk.CTkLabel(
            self.main_frame, 
            text="Размер фото не должен превышать 300x200 пикселей", 
            font=("Arial", 9),
            text_color="gray"
        ).pack(pady=(0, 10))

    def select_image(self):
        """Выбор и сохранение изображения с ограничением 300x200"""
        file_path = filedialog.askopenfilename(
            title="Выберите изображение товара",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if file_path:
            try:
                img = Image.open(file_path)
                #проверка размера 
                if img.width > 300 or img.height > 200:
                    messagebox.showerror("Ошибка", "Изображение не должно превышать 300x200 пикселей")
                    return
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть изображение: {e}")
                return
            
            #сохраняем новое фото
            os.makedirs('images', exist_ok=True)
            filename = os.path.basename(file_path)
            dest_path = os.path.join('images', filename)
            
            #если фото уже есть и оно отличается от нового удаляем старое
            if self.old_image_path and self.old_image_path != dest_path and os.path.exists(self.old_image_path):
                try:
                    os.remove(self.old_image_path)
                except:
                    pass
            
            shutil.copy2(file_path, dest_path)
            
            img = Image.open(dest_path)
            img = img.resize((100, 100))
            photo = ctk.CTkImage(light_image=img, dark_image=img, size=(100, 100))
            self.photo_label.configure(image=photo, text="")
            self.photo_label.image = photo
            
            self.image_path = dest_path
            messagebox.showinfo("Успех", "Изображение выбрано")
    
    def load_product_data(self):
        """Загружает данные товара для редактирования"""
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.id, p.name, p.category, p.description, p.manufacturer, 
                   s.name, p.price, p.unit, p.quantity, p.discount, p.image_path, p.article
            FROM products p
            LEFT JOIN suppliers s ON p.supplier_id = s.id
            WHERE p.id=?
        ''', (self.product_id,))
        product = cursor.fetchone()
        conn.close()
        
        if product:

            self.name_entry.insert(0, product[1] if product[1] else "")
            self.category_var.set(product[2] if product[2] else "")
            self.description_text.insert("1.0", product[3] if product[3] else "")
            self.manufacturer_entry.insert(0, product[4] if product[4] else "")
            self.supplier_var.set(product[5] if product[5] else "")
            self.price_entry.insert(0, str(product[6]) if product[6] else "")
            self.unit_entry.insert(0, product[7] if product[7] else "")
            self.quantity_entry.insert(0, str(product[8]) if product[8] else "")
            self.discount_entry.insert(0, str(product[9]) if product[9] else "")
            self.image_path = product[10] if product[10] else ""
            self.old_image_path = self.image_path
            self.article_entry.insert(0, product[11] if product[11] else "")
            
            #показываем фото если есть
            if self.image_path and os.path.exists(self.image_path):
                try:
                    img = Image.open(self.image_path)
                    img = img.resize((100, 100))
                    photo = ctk.CTkImage(light_image=img, dark_image=img, size=(100, 100))
                    self.photo_label.configure(image=photo, text="")
                    self.photo_label.image = photo
                except:
                    pass
    
    def save_product(self):
        """Сохраняет товар в БД с проверками"""
        name = self.name_entry.get().strip()
        category = self.category_var.get()
        description = self.description_text.get("1.0", "end").strip()
        manufacturer = self.manufacturer_entry.get().strip()
        supplier_name = self.supplier_var.get()
        unit = self.unit_entry.get().strip()
        article = self.article_entry.get().strip()
        
        #проверка обязательных полей
        if not name:
            messagebox.showerror("Ошибка", "Наименование товара обязательно")
            return
        
        if not category:
            messagebox.showerror("Ошибка", "Выберите категорию товара")
            return
        
        if not article:
            messagebox.showerror("Ошибка", "Артикул товара обязателен")
            return
        
        #проверка цены
        try:
            price = float(self.price_entry.get())
            if price < 0:
                messagebox.showerror("Ошибка", "Цена не может быть отрицательной")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную цену")
            return
        
        #проверка кол-ва
        try:
            quantity = int(self.quantity_entry.get())
            if quantity < 0:
                messagebox.showerror("Ошибка", "Количество не может быть отрицательным")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное количество")
            return
        
        #проверка скидки
        try:
            discount = float(self.discount_entry.get()) if self.discount_entry.get() else 0
            if discount < 0 or discount > 100:
                messagebox.showerror("Ошибка", "Скидка должна быть от 0 до 100")
                return
        except ValueError:
            discount = 0
        
        #проверка артикула на уникальность
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        if not self.product_id:
            cursor.execute('SELECT id FROM products WHERE article = ?', (article,))
            if cursor.fetchone():
                messagebox.showerror("Ошибка", "Товар с таким артикулом уже существует")
                conn.close()
                return
        else:
            cursor.execute('SELECT id FROM products WHERE article = ? AND id != ?', (article, self.product_id))
            if cursor.fetchone():
                messagebox.showerror("Ошибка", "Товар с таким артикулом уже существует")
                conn.close()
                return
        
        #находим саплиер id по имени
        supplier_id = None
        if supplier_name:
            cursor.execute('SELECT id FROM suppliers WHERE name = ?', (supplier_name,))
            sup = cursor.fetchone()
            if sup:
                supplier_id = sup[0]
            else:
                #если поставщика нет создаём нового
                cursor.execute('INSERT INTO suppliers (name) VALUES (?)', (supplier_name,))
                supplier_id = cursor.lastrowid
        
        #cохраняем товар
        if self.product_id:
            #обновление
            cursor.execute('''
                UPDATE products 
                SET name=?, category=?, description=?, manufacturer=?, supplier_id=?,
                    price=?, unit=?, quantity=?, discount=?, image_path=?, article=?
                WHERE id=?
            ''', (name, category, description, manufacturer, supplier_id,
                  price, unit, quantity, discount, self.image_path, article, self.product_id))
        else:
            #добавление
            cursor.execute('''
                INSERT INTO products (name, category, description, manufacturer, supplier_id,
                                    price, unit, quantity, discount, image_path, article)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, category, description, manufacturer, supplier_id,
                  price, unit, quantity, discount, self.image_path, article))
        
        conn.commit()
        conn.close()
        
        self.refresh_callback()
        self.destroy()
        messagebox.showinfo("Успех", "Товар сохранён")