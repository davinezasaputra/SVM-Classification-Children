import pandas as pd
import numpy as np
import re
import joblib
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import matplotlib.patches as mpatches
import seaborn as sns
from sklearn.metrics import confusion_matrix
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.svm import SVC
from sklearn.model_selection import learning_curve
from sklearn.metrics import classification_report, accuracy_score
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


def standardisasi_tb(row):
    tb = row['tb']
    umur = row['usia']
    cara_ukur = str(row['posisi']).lower().strip()
    if umur < 24 and cara_ukur == 'berdiri': return tb + 0.7
    elif umur >= 24 and cara_ukur in ['telentang', 'terlentang']: return tb - 0.7
    return tb

# load data
df = pd.read_csv('data_bbtb.csv', encoding='utf-8')

#ada tambahan print untuk doksi skripsi berikan komentar jika tidak diperlukan ~by davin




# standarisasi data umur, jenis kelamin, dan tinggi badan

df['tb_koreksi'] = df.apply(standardisasi_tb, axis=1)
#print("preprocessing data jenis kelamin")
#jenis_kelamin = {'L (Laki-laki':0, 'P (Perempuan)': 1}
#print("hasil preprocessing data jenis kelamin:", jenis_kelamin)
df['jk'] = df['jk'].map({'L': 0, 'P': 1})

# print("total data jenis kelamin setelah preprocessing:")
# print(df['jk'].value_counts())
# print ("\n")

# print("preprocessing data posisi pengukuran untuk tinggi badan")
# kondisi_tambah = df[(df['usia'] < 24) & (df['posisi'].str.lower().str.strip() == 'berdiri')].head(2)
# kondisi_kurang = df[(df['usia'] >= 24) & (df['posisi'].str.lower().str.strip().isin(['telentang', 'terlentang']))].head(2)
# kondisi_normal = df.head(1)
# contoh_data_representatif = pd.concat([kondisi_normal, kondisi_tambah, kondisi_kurang])
# print("Data Asli:")
# print(contoh_data_representatif[['usia', 'posisi', 'tb', 'tb_koreksi']])
# print("\n")

# cleaning data
df = df.dropna(subset=['BB/TB'])
df_gizi_buruk = df[df['BB/TB'] == 'Gizi Buruk']
df_gizi_buruk_cloned = pd.concat([df_gizi_buruk] * 5, ignore_index=True)
df = pd.concat([df, df_gizi_buruk_cloned], ignore_index=True)


# pemilihan fitur
df = df.dropna(subset=['bb', 'tb_koreksi', 'jk'])
X = df[['bb', 'tb_koreksi', 'jk']]
y = df['BB/TB']

# print("preprocessing data label")

le = LabelEncoder()
y_encoded = le.fit_transform(y) 
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)
#print("Daftar Label Asli:", le.classes_)
#kamus_label = dict(zip(le.classes_, le.transform(le.classes_)))
#print("Hasil preprocessing label:", kamus_label)
#print("\n")

print("--- Menjalankan SMOTE & Training Model via Pipeline (BB/U) ---")
langkah_langkah = [
    ('smote', SMOTE(random_state=42, k_neighbors=1)),
    ('scaler', MinMaxScaler()),
    ('svm', SVC(kernel='rbf', C=10, gamma=1, probability=True, random_state=42))
]



pipeline_bbtb = ImbPipeline(steps=langkah_langkah)
pipeline_bbtb.fit(X_train, y_train)


#print("Hasil Preprocessing: MinMax Scaler")
# 1. Mengambil alat scaler dari dalam pipeline
#alat_scaler = pipeline_bbu.named_steps['scaler']

# 2. Menampilkan nilai Min dan Max yang dipelajari mesin (BB, Umur, JK)
# print("Nilai Minimum (BB, TB, Usia, JK):", alat_scaler.data_min_)
# print("Nilai Maksimum (BB, TB, Usia, JK):", alat_scaler.data_max_)
# print("\n")

# 3. Membuktikan wujud data yang sudah berubah menjadi 0 - 1
# print("Contoh 5 Data Asli:")
# print(X_test.head())
# print("\n")

# data_ternormalisasi = alat_scaler.transform(X_test.head())
# print("Contoh 5 Data Setelah Normalisasi:")
# print(data_ternormalisasi)

y_pred = pipeline_bbtb.predict(X_test)
print(f"Akurasi Final BB/TB: {accuracy_score(y_test, y_pred) * 100:.2f}%\n")
print(classification_report(y_test, y_pred, target_names=le.inverse_transform(np.unique(y_test))))

# confusion matrix
cm = confusion_matrix(y_test, y_pred)
labels = le.inverse_transform(np.unique(y_test))

plt.figure(figsize=(10, 7))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
plt.title('Confusion Matrix: Klasifikasi BB/TB')
plt.xlabel('Prediksi Model')
plt.ylabel('Kenyataan (Actual)')
plt.show()

# 0: Gizi Baik, 1: Gizi Buruk, 2: Gizi Kurang, 3: Gizi Lebih, 4: Obesitas, 5: Risiko Gizi Lebih
# Array mulai dai 0 ya
warna_hex = ['#2ecc71',
             '#c0392b',
             '#e67e22',
             '#3498db',
             '#8e44ad',
             '#f1c40f']

custom_cmap = ListedColormap(warna_hex)

# fungsi pemetaan decission bouundary jenis kelamin 
def plot_decision_boundaries(gender_val, gender_name):
    x_min, x_max = X['bb'].min() - 1, X['bb'].max() + 1
    y_min, y_max = X['tb_koreksi'].min() - 5, X['tb_koreksi'].max() + 5
    xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.2),
                         np.arange(y_min, y_max, 1.0))

    grid_df = pd.DataFrame({
        'bb': xx.ravel(),
        'tb_koreksi': yy.ravel(),
        'jk': np.full(xx.ravel().shape, gender_val)
    })
    Z = pipeline_bbtb.predict(grid_df)
    Z = Z.reshape(xx.shape)
    # map
    plt.contourf(xx, yy, Z, alpha=0.35, cmap=custom_cmap)
    idx = X_test['jk'] == gender_val
    plt.scatter(X_test[idx]['bb'], X_test[idx]['tb_koreksi'], 
                c=y_test[idx], cmap=custom_cmap, s=60, marker='o', 
                alpha=0.9, linewidth=1, edgecolor='black', 
                vmin=0, vmax=len(warna_hex)-1) 
    plt.title(f'Batas Keputusan SVM - {gender_name}')
    plt.xlabel('Berat Badan (kg)')
    plt.ylabel('Tinggi Badan (cm)')
plt.figure(figsize=(16, 7))
plt.subplot(1, 2, 1)
plot_decision_boundaries(0, 'Laki-laki')
plt.subplot(1, 2, 2)
plot_decision_boundaries(1, 'Perempuan')
patches = [mpatches.Patch(color=warna_hex[i], label=labels[i]) for i in range(len(warna_hex))]
plt.figlegend(handles=patches, loc='lower center', ncol=6, borderaxespad=0.1)
plt.tight_layout(rect=[0, 0.05, 1, 1]) 
plt.show()

# =====================================================================
# VISUALISASI LEARNING CURVE
# (Berguna untuk analisis Overfitting/Underfitting di Skripsi)
# =====================================================================
print("--- Membuat Visualisasi Learning Curve ---")

# Menghitung skor training dan validasi dengan 5-fold Cross Validation
train_sizes, train_scores, test_scores = learning_curve(
    estimator=pipeline_bbtb,
    X=X_train, 
    y=y_train,
    train_sizes=np.linspace(0.4, 1.0, 10), # Membagi data latih ke dalam 10 titik evaluasi
    cv=5,                                  # 5-Fold Cross Validation
    n_jobs=-1,                             # Gunakan seluruh core CPU agar lebih cepat
    random_state=42
)

# Menghitung nilai rata-rata dan standar deviasi
train_mean = np.mean(train_scores, axis=1)
train_std = np.std(train_scores, axis=1)
test_mean = np.mean(test_scores, axis=1)
test_std = np.std(test_scores, axis=1)

# Mulai Menggambar Plot
plt.figure(figsize=(10, 6))

# Plot Akurasi Training
plt.plot(train_sizes, train_mean, color='#3498db', marker='o', 
         markersize=5, label='Akurasi Training (Pelatihan)')
plt.fill_between(train_sizes, train_mean + train_std, train_mean - train_std, 
                 alpha=0.15, color='#3498db')

# Plot Akurasi Validasi (Cross-Validation)
plt.plot(train_sizes, test_mean, color='#2ecc71', linestyle='--', marker='s', 
         markersize=5, label='Akurasi Validasi (Pengujian)')
plt.fill_between(train_sizes, test_mean + test_std, test_mean - test_std, 
                 alpha=0.15, color='#2ecc71')

plt.title('Learning Curve - SVM Klasifikasi Gizi (BB/TB)')
plt.xlabel('Jumlah Sampel Data Latih')
plt.ylabel('Skor Akurasi')
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(loc='lower right')
plt.tight_layout()
plt.show()
print("Visualisasi Learning Curve selesai ditampilkan.\n")

# # simpan model
# paket_SVM = {'model_pipeline': pipeline_bbtb, 'label_encoder': le}
# joblib.dump(paket_SVM, 'mesin_svm_bbtb.pkl')
# print("Model Pipeline berhasil disimpan sebagai mesin_svm_bbtb.pkl")