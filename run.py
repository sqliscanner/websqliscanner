from app import create_app

# Membuat instance aplikasi Flask menggunakan application factory
app = create_app()

# Menjalankan server Flask jika file ini dijalankan langsung
if __name__ == '__main__':
    app.run(debug=True)  
