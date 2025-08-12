import os
from flask import Flask
from flask_mysqldb import MySQL
from flask_login import LoginManager
from config import Config

# Inisialisasi ekstensi MySQL dan LoginManager
mysql = MySQL()
login_manager = LoginManager()
login_manager.login_view = 'main.login'  # Halaman yang dituju jika pengguna belum login

# Fungsi factory untuk membuat dan mengonfigurasi instance Flask
def create_app():
    # Menentukan direktori dasar dari file ini
    base_dir = os.path.abspath(os.path.dirname(__file__))
    
    # Menentukan jalur untuk folder template dan static
    template_path = os.path.join(base_dir, '..', 'templates')
    static_path = os.path.join(base_dir, '..', 'static')
    
    # Membuat instance Flask dengan folder template dan static yang dikustomisasi
    app = Flask(
        __name__,
        template_folder=template_path,
        static_folder=static_path
    )

    # Mengambil konfigurasi dari class Config
    app.config.from_object(Config)

    # Inisialisasi ekstensi dengan aplikasi Flask
    mysql.init_app(app)
    login_manager.init_app(app)

    # Mendaftarkan blueprint routes
    from app.routes import bp
    app.register_blueprint(bp)

    # Mengimpor model User dan mendefinisikan fungsi untuk memuat pengguna
    from app.models import User

    # Fungsi ini digunakan oleh Flask-Login untuk mengambil user berdasarkan ID
    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)

    # Mengembalikan instance aplikasi Flask
    return app
