import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import seaborn as sns
import joblib # Tambahan untuk menyimpan model ke API
from imblearn.combine import SMOTETomek
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from sklearn.model_selection import train_test_split, GridSearchCV
from imblearn.over_sampling import SMOTE # Ganti SMOTETomek ke SMOTE

# ===============================
# BAGIAN 1: PERUBAHAN FUNGSI Z-SCORE (IMT/U -> BB/TB)
# ===============================
# Pastikan Anda punya file z_score_bbtb_l.csv dan z_score_bbtb_p.csv dari WHO
ref_tables = {
    'bbu_L': pd.read_csv('z_score_bbu_l.csv'),
    'bbu_P': pd.read_csv('z_score_bbu_p.csv'),
    'tbu_L': pd.read_csv('z_score_tbu_l.csv'),
    'tbu_P': pd.read_csv('z_score_tbu_p.csv'), 
    'bbtb_panjang_L': pd.read_csv('z_score_bbtb_panjang_l.csv'),
    'bbtb_tinggi_L': pd.read_csv('z_score_bbtb_tinggi_l.csv'),
    'bbtb_panjang_P': pd.read_csv('z_score_bbtb_panjang_p.csv'),
    'bbtb_tinggi_P': pd.read_csv('z_score_bbtb_tinggi_p.csv'),
}

def get_zscore(nilai, nilai_referensi, jk, tipe, kolom_ref='umur', umur=None):
    # 1. Tentukan Key Tabel
    if tipe == 'bbtb':
        key = f"bbtb_panjang_{jk}" if umur < 24 else f"bbtb_tinggi_{jk}"
    else:
        key = f"{tipe}_{jk}"
    
    df = ref_tables[key].copy()

    # 2. Fungsi Pembersihan Data Internal
    def clean_val(series):
        return pd.to_numeric(series.astype(str).str.replace(',', '.').str.strip(), errors='coerce')

    # 3. Ambil data berdasarkan POSISI KOLOM (Indeks) agar tidak KeyError
    # Kolom 0 = Referensi (Umur/Tinggi), Kolom 1 = -3 SD, Kolom 2 = -2 SD ... Kolom 4 = Median
    # Pastikan urutan CSV Anda: [Ref, -3, -2, -1, Median, +1, +2, +3]
    
    col_ref_data = clean_val(df.iloc[:, 0]) # Kolom paling kiri
    col_neg1_data = clean_val(df.iloc[:, 3]) # Kolom ke-4 (-1 SD)
    col_median_data = clean_val(df.iloc[:, 4]) # Kolom ke-5 (Median)
    col_pos1_data = clean_val(df.iloc[:, 5]) # Kolom ke-6 (+1 SD)

    # 4. Cari Baris Terdekat menggunakan Kolom Referensi
    idx = (col_ref_data - nilai_referensi).abs().idxmin()
    
    # 5. Ambil Nilai dari baris tersebut
    median = col_median_data.iloc[idx]
    pos1 = col_pos1_data.iloc[idx]
    neg1 = col_neg1_data.iloc[idx]

    # 6. Hitung Z-Score
    sd = (pos1 - neg1) / 2
    return (nilai - median) / sd

def klasifikasi_bbtb(z_bbtb):
    if z_bbtb < -3: return "Gizi Buruk"
    elif z_bbtb < -2: return "Gizi Kurang"
    elif z_bbtb <= 1: return "Gizi Baik" # Sesuai standar baru Kemenkes/Puskesmas
    elif z_bbtb <= 2: return "Beresiko Gizi Lebih"
    elif z_bbtb <= 3: return "Gizi Lebih"
    else: return "Obesitas"

def diagnosa_balita(data):
    # Koreksi Posisi Pengukuran
    if data['umur'] < 24 and data['posisi'] == 'berdiri':
        tb = data['tb'] + 0.7
    elif data['umur'] >= 24 and data['posisi'] == 'telentang':
        tb = data['tb'] - 0.7
    else:
        tb = data['tb']

    # Z-score (BB/TB patokannya adalah Tinggi Badan 'tb', bukan umur!)
    z_bbu = get_zscore(data['bb'], data['umur'], data['jk'], 'bbu', 'umur')
    z_tbu = get_zscore(tb, data['umur'], data['jk'], 'tbu', 'umur')
    z_bbtb = get_zscore(data['bb'], tb, data['jk'], 'bbtb', 'tinggi') # <-- Perubahan Fatal

    status_bbtb = klasifikasi_bbtb(z_bbtb)

    return {
        'status_akhir': status_bbtb,
        'z_bbu': round(z_bbu, 2),
        'z_tbu': round(z_tbu, 2),
        'z_bbtb': round(z_bbtb, 2)
    }

# ===============================
# BAGIAN 2: MACHINE LEARNING (SVM)
# ===============================
try:
    df = pd.read_csv('DataGabungan.csv', encoding='windows-1252')
    
    # Preprocessing (Regex Aman)
    for col in ['ZS BB/U', 'ZS TB/U', 'ZS BB/TB']:
        df[col] = df[col].astype(str).str.replace(',', '.').str.replace(':', '.')
        df[col] = df[col].str.replace(r'[^\d.-]', '', regex=True)
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    df = df.dropna(subset=['ZS BB/U', 'ZS TB/U', 'ZS BB/TB', 'BB/TB'])
    df = df[df['BB/TB'] != 'Outlier']

except FileNotFoundError:
    print("Error: File 'data_gizi.csv' tidak ditemukan.")
    exit()

X = df[['ZS BB/U', 'ZS TB/U', 'ZS BB/TB']]
y = df['BB/TB']

# 1. Simpan LabelEncoder agar API tahu "0" itu apa, "1" itu apa
le = LabelEncoder()
y_encoded = le.fit_transform(y) 

X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)

print("\n--- Menjalankan SMOTE (Penyeimbangan Data) ---")
sm = SMOTE(random_state=42)
X_res, y_res = sm.fit_resample(X_train, y_train)

scaler = MinMaxScaler()
X_res_s = scaler.fit_transform(X_res)
X_test_s = scaler.transform(X_test)

print("--- Melatih Model SVM dengan Parameter Terbaik (C=1000, Gamma=10) ---")
# Langsung masukkan hasil GridSearchCV ke sini
best_model = SVC(kernel='rbf', C=10, gamma=1, probability=True, random_state=42)
best_model.fit(X_res_s, y_res)


print(f"Akurasi Final: {accuracy_score(y_test, best_model.predict(X_test_s)) * 100:.2f}%")

# ===============================
# BAGIAN 3: EXPORT KE DALAM SATU PAKET (SANGAT RAPI)
# ===============================
print("\n--- Mengekspor Paket AI untuk API Flask ---")

# Bungkus semua komponen ke dalam satu dictionary
paket_ai = {
    'model_svm': best_model,
    'scaler': scaler,
    'label_encoder': le
}

# Simpan sebagai satu file saja
joblib.dump(paket_ai, 'mesin_svm_puskesmas.pkl')

print("[INFO] Paket AI (Model, Scaler, Encoder) berhasil disatukan dalam 'mesin_svm_puskesmas.pkl'!")
# ===============================
# BAGIAN 4: TESTING PREDIKSI 1 DATA MENTAH (RAW DATA)
# ===============================
print("\n==================================================")
print("UJI COBA PREDIKSI 1 DATA BALITA (ANGKA MENTAH)")
print("==================================================")

# 1. Masukkan Data Mentah Balita
data_mentah = {
    'bb': 20,          # Berat Badan Ideal untuk 36 bulan
    'tb': 40,          # Tinggi Badan Ideal untuk 36 bulan
    'umur': 37,          
    'jk': 'P',           
    'posisi': 'berdiri'  
}

print(f"Data Input   : BB = {data_mentah['bb']} kg | TB = {data_mentah['tb']} cm | Umur = {data_mentah['umur']} bulan")

# 2. Koreksi TB berdasarkan posisi & umur (Sesuai Standar WHO)
tb_koreksi = data_mentah['tb']
if data_mentah['umur'] < 24 and data_mentah['posisi'] == 'berdiri':
    tb_koreksi += 0.7
elif data_mentah['umur'] >= 24 and data_mentah['posisi'] == 'telentang':
    tb_koreksi -= 0.7

# 3. Sistem Otomatis Menghitung Z-Score (Memanggil Fungsi Bagian 1)
z_bbu = get_zscore(data_mentah['bb'], data_mentah['umur'], data_mentah['jk'], 'bbu', 'umur')
z_tbu = get_zscore(tb_koreksi, data_mentah['umur'], data_mentah['jk'], 'tbu', 'umur')

# PENTING: Untuk bbtb, parameter kolom_ref tidak perlu diisi karena sudah otomatis di dalam fungsi
z_bbtb = get_zscore(data_mentah['bb'], tb_koreksi, data_mentah['jk'], 'bbtb', umur=data_mentah['umur'])

print(f"Z-Score Auto : BB/U = {z_bbu:.2f} | TB/U = {z_tbu:.2f} | BB/TB = {z_bbtb:.2f}")

# 4. Bungkus ke DataFrame agar tidak kena Warning merah
data_tes = pd.DataFrame([[z_bbu, z_tbu, z_bbtb]], columns=['ZS BB/U', 'ZS TB/U', 'ZS BB/TB'])

# 5. Normalisasi (Scaling)
data_tes_scaled = scaler.transform(data_tes)

# 6. AI Melakukan Prediksi
prediksi_idx = best_model.predict(data_tes_scaled)[0]
hasil_status = le.inverse_transform([prediksi_idx])[0]

# 7. Hitung Tingkat Keyakinan AI
probabilitas = best_model.predict_proba(data_tes_scaled)[0]
tingkat_keyakinan = probabilitas[prediksi_idx] * 100

print(f"Hasil SVM    : >>> {hasil_status.upper()} <<<")
print(f"Keyakinan AI : {tingkat_keyakinan:.2f}%")
print("==================================================\n")

print("[INFO] Model SVM, Scaler, dan LabelEncoder berhasil diekspor!")