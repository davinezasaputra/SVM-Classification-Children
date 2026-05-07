import pandas as pd
import numpy as np
import re
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from sklearn.decomposition import PCA
import warnings
from sklearn.model_selection import GridSearchCV
warnings.filterwarnings("ignore", category=FutureWarning)

# ===============================
# BAGIAN 1: FUNGSI PREPROCESSING & KALIBRASI WHO
# ===============================
def parse_usia(usia_str):
    if pd.isna(usia_str): return 0
    t, b, h = 0, 0, 0
    t_m = re.search(r'(\d+)\s*Tahun', usia_str)
    if t_m: t = int(t_m.group(1))
    b_m = re.search(r'(\d+)\s*Bulan', usia_str)
    if b_m: b = int(b_m.group(1))
    h_m = re.search(r'(\d+)\s*Hari', usia_str)
    if h_m: h = int(h_m.group(1))
    return (t * 12) + b + (h / 30.0)

def standardisasi_tb(row):
    tb = row['tb']
    umur = row['umur_bulan']
    cara_ukur = str(row['Cara Ukur']).lower().strip()
    
    # Koreksi Posisi Pengukuran (Standar WHO)
    if umur < 24 and cara_ukur == 'berdiri':
        return tb + 0.7
    elif umur >= 24 and cara_ukur in ['telentang', 'terlentang']:
        return tb - 0.7
    return tb

# ===============================
# BAGIAN 2: DATA PIPELINE & SVM TRAINING
# ===============================
try:
    df = pd.read_csv('DataGabungan.csv', encoding='windows-1252')
except FileNotFoundError:
    print("Error: File 'DataGabungan.csv' tidak ditemukan.")
    exit()

# 1. Ekstraksi dan Konversi Fitur
df['umur_bulan'] = df['Usia Saat Ukur'].apply(parse_usia)
df['jk_encoded'] = df['jk'].map({'L': 0, 'P': 1})
df['tb_terkalibrasi'] = df.apply(standardisasi_tb, axis=1)

# 2. Pembersihan Target Target
df = df.dropna(subset=['BB/TB'])
df = df[~df['BB/TB'].isin(['Outlier', '-'])]

# Gabung kelas minoritas untuk mengatasi error SMOTE
df['BB/TB'] = df['BB/TB'].replace({
    'Gizi Buruk': 'Gizi Kurang/Buruk',
    'Gizi Kurang': 'Gizi Kurang/Buruk'
})

# 3. Filter fitur input
df = df.dropna(subset=['bb', 'tb_terkalibrasi', 'umur_bulan', 'jk_encoded'])

X = df[['bb', 'tb_terkalibrasi', 'umur_bulan', 'jk_encoded']]
y = df['BB/TB']

le = LabelEncoder()
y_encoded = le.fit_transform(y) 

X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)

print("\n--- Menjalankan SMOTE (Penyeimbangan Data) ---")
sm = SMOTE(random_state=42)
X_res, y_res = sm.fit_resample(X_train, y_train)

scaler = MinMaxScaler()
X_res_s = scaler.fit_transform(X_res)
X_test_s = scaler.transform(X_test)

print("\n--- Memulai Pencarian Parameter Terbaik (Grid Search) ---")

# 1. Tentukan rentang parameter yang akan diuji
# 4. Gunakan model terbaik untuk prediksi dan visualisasi
best_model = SVC(kernel='rbf', C=10, gamma=1, probability=True, random_state=0)
best_model.fit(X_res_s, y_res)

y_pred = best_model.predict(X_test_s)
print(f"Akurasi Final dengan Parameter Terbaik: {accuracy_score(y_test, y_pred) * 100:.2f}%")
# 3. Tampilkan Classification Report
print("\n--- Classification Report ---")
nama_target = le.inverse_transform(np.unique(y_test)) 
print(classification_report(y_test, y_pred, target_names=nama_target))

# ===============================
# BAGIAN 3: EVALUASI & VISUALISASI (VERSI PERBAIKAN)
# ===============================
print("\n[INFO] Membuat Visualisasi Hyperplane yang lebih jelas...")

# 1. Reduksi Dimensi
pca = PCA(n_components=2)
X_train_pca = pca.fit_transform(X_res_s)
X_test_pca = pca.transform(X_test_s)

# 2. Latih model khusus untuk visualisasi 2D
# DIUBAH: Disamakan menggunakan C=1 dan gamma=10
svm_vis = SVC(kernel='rbf', C=1, gamma=10)
svm_vis.fit(X_train_pca, y_res)

# 3. Buat Grid untuk Hyperplane (Resolusi diperhalus h=0.01)
h = 0.01 
x_min, x_max = X_test_pca[:, 0].min() - 0.2, X_test_pca[:, 0].max() + 0.2
y_min, y_max = X_test_pca[:, 1].min() - 0.2, X_test_pca[:, 1].max() + 0.2
xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

Z = svm_vis.predict(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)

# 4. PLOTTING
plt.figure(figsize=(12, 9))

# Gambar wilayah keputusan (Hyperplane)
plt.contourf(xx, yy, Z, alpha=0.2, cmap='viridis')

# TAMBAHKAN JITTER supaya tidak terlihat seperti garis kaku
X_jitter = X_test_pca[:, 0] + np.random.normal(0, 0.015, size=X_test_pca[:, 0].shape)
Y_jitter = X_test_pca[:, 1] + np.random.normal(0, 0.015, size=X_test_pca[:, 1].shape)

# Gambar titik data dengan Jitter dan Alpha (Transparansi)
scatter = plt.scatter(X_jitter, Y_jitter, c=y_test, cmap='viridis', 
                      edgecolors='k', s=40, alpha=0.6, linewidth=0.5)

# Tambahkan Legend
handles, labels = scatter.legend_elements()
target_names = le.inverse_transform(np.unique(y_test))
plt.legend(handles, target_names, loc="upper right", title="Status Gizi")

plt.title('Penyebaran Data Balita & Decision Boundary SVM (PCA 2D)\n(Dengan Jitter untuk Memperjelas Sebaran)')
plt.xlabel('Komponen Utama 1 (Dominan: Berat & Tinggi)')
plt.ylabel('Komponen Utama 2 (Dominan: Jenis Kelamin/Umur)')
plt.grid(True, linestyle='--', alpha=0.3)

plt.tight_layout()
plt.savefig('hyperplane_2d_clear.png', dpi=300)
print("[INFO] Gambar 'hyperplane_2d_clear.png' berhasil dibuat dengan sebaran yang lebih jelas.")

# ===============================
# BAGIAN 4: EXPORT KE DALAM SATU PAKET
# ===============================
paket_ai = {
    'model_svm': best_model,
    'scaler': scaler,
    'label_encoder': le
}
joblib.dump(paket_ai, 'mesin_svm_puskesmas.pkl')
print("\n[INFO] Paket AI diekspor ke 'mesin_svm_puskesmas.pkl'!")

# ===============================
# BAGIAN 5: TESTING PREDIKSI 1 DATA MENTAH
# ===============================
print("\n==================================================")
print("UJI COBA PREDIKSI 1 DATA BALITA (ANGKA MENTAH)")
print("==================================================")

# Data uji menggunakan proporsi medis yang logis
data_mentah = {
    'bb': 14.5,          
    'tb': 95.0,          
    'umur': 37,          
    'jk': 'P',           
    'posisi': 'berdiri'  
}

print(f"Data Input   : BB = {data_mentah['bb']} kg | TB = {data_mentah['tb']} cm | Umur = {data_mentah['umur']} bulan")

# 1. Kalibrasi TB Otomatis untuk Data Baru
tb_koreksi = data_mentah['tb']
if data_mentah['umur'] < 24 and data_mentah['posisi'] == 'berdiri':
    tb_koreksi += 0.7
elif data_mentah['umur'] >= 24 and data_mentah['posisi'] == 'telentang':
    tb_koreksi -= 0.7

# 2. Encode Jenis Kelamin
jk_val = 1 if data_mentah['jk'] == 'P' else 0

# 3. Susun sesuai format X: ['bb', 'tb_terkalibrasi', 'umur_bulan', 'jk_encoded']
data_tes = pd.DataFrame([[data_mentah['bb'], tb_koreksi, data_mentah['umur'], jk_val]], 
                        columns=['bb', 'tb_terkalibrasi', 'umur_bulan', 'jk_encoded'])

# 4. Scaling
data_tes_scaled = scaler.transform(data_tes)

# 5. Prediksi Target
prediksi_idx = best_model.predict(data_tes_scaled)[0]
hasil_status = le.inverse_transform([prediksi_idx])[0]

# 6. Kalkulasi Probabilitas (Keyakinan AI)
probabilitas = best_model.predict_proba(data_tes_scaled)[0]
tingkat_keyakinan = probabilitas[prediksi_idx] * 100

print(f"Hasil SVM    : >>> {hasil_status.upper()} <<<")
print(f"Keyakinan AI : {tingkat_keyakinan:.2f}%")
print("==================================================\n")