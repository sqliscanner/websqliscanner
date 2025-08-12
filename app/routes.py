from flask import Blueprint, render_template, request, redirect, session, flash
from app import mysql
import tensorflow as tf
import pickle
from tensorflow.keras.preprocessing.sequence import pad_sequences
from app.utils import clean_text

# Inisialisasi blueprint untuk routing aplikasi
bp = Blueprint('main', __name__)

# Load model CNN untuk deteksi SQLi
model = tf.keras.models.load_model("textcnn_sqli_model.h5")

# Load tokenizer yang digunakan untuk preprocessing input
with open("tokenizer.pkl", "rb") as f:
    tokenizer = pickle.load(f)

# Route landing page utama
@bp.route('/')
def landing():
    return render_template('landing.html')

# Route untuk registrasi user baru
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()

        # Cek apakah username sudah terdaftar
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            flash("Username sudah digunakan.")
            return redirect('/register')

        # Simpan user baru ke database
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        mysql.connection.commit()
        return redirect('/login')
    
    return render_template('register.html')

# Route untuk login user
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()

        # Cek kredensial user
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        
        # Jika valid, simpan user ID di session
        if user:
            session['user_id'] = user[0]
            return redirect('/dashboard')
        else:
            flash("Username atau password salah")
            return redirect('/login')
    
    return render_template('login.html')

# Fungsi untuk menjelaskan alasan klasifikasi SQLi berdasarkan pola teks
def get_reason_from_sentence(sentence):
    sentence_lower = sentence.lower()
    reasons = []

    if "' or '1'='1" in sentence_lower or '" or "1"="1' in sentence_lower:
        reasons.append("Mengandung pola klasik SQL injection seperti 'OR 1=1'.")

    if "union select" in sentence_lower:
        reasons.append("Terdapat UNION SELECT, teknik umum untuk menyatukan hasil query lain.")

    if "--" in sentence_lower or "#" in sentence_lower:
        reasons.append("Mengandung komentar SQL seperti '--' atau '#', bisa digunakan untuk mengabaikan bagian query.")

    if "drop table" in sentence_lower or "delete from" in sentence_lower:
        reasons.append("Perintah destruktif seperti DROP TABLE atau DELETE FROM terdeteksi.")

    if sentence.count("'") >= 3 or sentence.count('"') >= 3:
        reasons.append("Penggunaan kutip berlebihan yang sering digunakan untuk menyisipkan payload.")

    if ";" in sentence_lower:
        reasons.append("Terdapat titik koma, kemungkinan mencoba mengakhiri pernyataan SQL.")

    if not reasons:
        return "Model mendeteksi potensi SQLi, meskipun tidak ada pola klasik yang jelas."
    
    return " & ".join(reasons)

# Route dashboard utama untuk analisis kalimat dengan model
@bp.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    result = None
    reason = ""

    # Jika user belum login, redirect ke login
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        # Ambil kalimat dari form dan lakukan preprocessing
        sentence = request.form['sentence']
        cleaned = clean_text(sentence)
        sequence = tokenizer.texts_to_sequences([cleaned])
        padded = pad_sequences(sequence, maxlen=43, padding='post')

        # Prediksi menggunakan model CNN
        prob = model.predict(padded)[0][0]
        pred = "SQLi" if prob > 0.5 else "Normal"

        # Ambil alasan berdasarkan pola jika prediksi adalah SQLi
        if pred == "SQLi":
            reason = get_reason_from_sentence(sentence)
        else:
            reason = "Kalimat tidak mengandung ciri khas SQL injection yang umum."

        # Simpan hasil ke database
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO scan_reports (user_id, sentence, prediction, probability) VALUES (%s, %s, %s, %s)",
                    (session['user_id'], sentence, pred, prob))
        mysql.connection.commit()

        result = (pred, prob)

    return render_template('dashboard.html', result=result, reason=reason)

# Route untuk logout user dan menghapus session
@bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')
