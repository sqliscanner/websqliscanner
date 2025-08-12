from flask_login import UserMixin
from app import mysql

# Kelas User digunakan untuk mewakili pengguna dalam sistem autentikasi
class User(UserMixin):
    # Konstruktor untuk inisialisasi objek User dengan id dan username
    def __init__(self, id, username):
        self.id = id
        self.username = username

    # Fungsi statis untuk mengambil data pengguna dari database berdasarkan ID
    @staticmethod
    def get_by_id(user_id):
        # Membuka koneksi ke database dan melakukan query pengguna berdasarkan ID
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, username FROM users WHERE id = %s", (user_id,))
        result = cur.fetchone()
        cur.close()

        # Jika ditemukan, kembalikan objek User; jika tidak, kembalikan None
        if result:
            return User(id=result[0], username=result[1])
        return None
