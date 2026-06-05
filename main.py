#python --version 
# pip install customtkinter                                                                                                                              pip install customtkinter
#pip install Pillow
#pip install openpyxl
import sys
import warnings
warnings.filterwarnings("ignore")
import customtkinter as ctk
from database import create_database
from windows.login_window import LoginWindow

# Настройка внешнего вида (по заданию: цвета #FFFFFF, #ABCFFCE, #546F94)
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

if __name__ == "__main__":
    # Создаём БД при первом запуске
    create_database()
    
    # Запускаем окно входа
    app = LoginWindow()
    app.mainloop()
