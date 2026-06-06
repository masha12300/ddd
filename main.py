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

#настройка внешнего вида 
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

if __name__ == "__main__":
    create_database()
    
    app = LoginWindow()
    app.mainloop()
