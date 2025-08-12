import re

# Fungsi untuk membersihkan teks dari karakter yang tidak relevan
# Digunakan dalam preprocessing input sebelum dikirim ke model deteksi
def clean_text(text):
    # Ubah teks menjadi huruf kecil dan pastikan dalam bentuk string
    text = str(text).lower()
    
    text = re.sub(r'\s+', ' ', text)  # hanya bersihkan whitespace ganda

    # Hapus spasi di awal dan akhir
    return text.strip()
