from matplotlib.colors import ListedColormap
import pandas as pd
import numpy as np
import re
import joblib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import seaborn as sns
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
#ada tambahan print untuk doksi skripsi berikan komentar jika tidak diperlukan ~by davin

df = pd.read_csv('data_bb.csv', encoding='utf-8')

df['usia']
df['jk'] = df['jk'].map({'L': 0, 'P': 1})

# print("preprocessing data jenis kelamin")
# jenis_kelamin = {'L (Laki-laki':0, 'P (Perempuan)': 1}
# print("hasil preprocessing data jenis kelamin:", jenis_kelamin)
# print("total data jenis kelamin setelah preprocessing:")
# print(df['jk'].value_counts())
# print ("\n")


X = df[['bb', 'usia', 'jk']]
y = df['BB/U']

# print("preprocessing data label")

le = LabelEncoder()
y_encoded = le.fit_transform(y) 
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)


# print("Daftar Label Asli:", le.classes_)

# kamus_label = dict(zip(le.classes_, le.transform(le.classes_)))
# print("Hasil preprocessing label:", kamus_label)

# print("\n")

print("--- Menjalankan SMOTE & Training Model via Pipeline (BB/U) ---")
langkah_langkah = [
    ('smote', SMOTE(random_state=42, k_neighbors=1)),
    ('scaler', MinMaxScaler()),
    ('svm', SVC(kernel='rbf', C=10, gamma=1, probability=True, random_state=42))
]

pipeline_bbu = ImbPipeline(steps=langkah_langkah)
pipeline_bbu.fit(X_train, y_train)
# print("Hasil Preprocessing: MinMax Scaler")

# # 1. Mengambil alat scaler dari dalam pipeline
# alat_scaler = pipeline_bbu.named_steps['scaler']

# # 2. Menampilkan nilai Min dan Max yang dipelajari mesin (BB, Umur, JK)
# print("Nilai Minimum (BB, Usia, JK):", alat_scaler.data_min_)
# print("Nilai Maksimum (BB, Usia, JK):", alat_scaler.data_max_)
# print("\n")

# # 3. Membuktikan wujud data yang sudah berubah menjadi 0 - 1
# print("Contoh 5 Data Asli:")
# print(X_test.head())
# print("\n")

# # Kita suruh scaler mengubah 5 data tersebut hanya untuk dicetak ke layar
# data_ternormalisasi = alat_scaler.transform(X_test.head())
# print("Contoh 5 Data Setelah Normalisasi:")
# print(data_ternormalisasi)



y_pred = pipeline_bbu.predict(X_test)

cm = confusion_matrix(y_test, y_pred)
labels = le.inverse_transform(np.unique(y_test))

plt.figure(figsize=(10, 7))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
plt.title('Confusion Matrix: Klasifikasi BB/U')
plt.xlabel('Prediksi Model')
plt.ylabel('Kenyataan (Actual)')
plt.show()

print(f"Akurasi Final BB/U: {accuracy_score(y_test, y_pred) * 100:.2f}%\n")
print(classification_report(y_test, y_pred, target_names=le.inverse_transform(np.unique(y_test))))
warna_hex = [
    '#f1c40f',
    '#2ecc71',
    '#e67e22',
    '#c0392b'
]

custom_cmap = ListedColormap(warna_hex)

def plot_decision_boundaries(gender_val, gender_name):

    x_min, x_max = X['usia'].min() - 2, X['usia'].max() + 2
    y_min, y_max = X['bb'].min() - 2, X['bb'].max() + 2
    
    xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.5),
                         np.arange(y_min, y_max, 0.2))



    grid_df = pd.DataFrame({
        'bb': yy.ravel(),             
        'usia': xx.ravel(),     
        'jk': np.full(xx.ravel().shape, gender_val)
    })
    

    Z = pipeline_bbu.predict(grid_df)
    Z = Z.reshape(xx.shape)


    plt.contourf(xx, yy, Z, alpha=0.35, cmap=custom_cmap)
    

    idx = X_test['jk'] == gender_val
    plt.scatter(X_test[idx]['usia'], X_test[idx]['bb'], 
                c=y_test[idx], cmap=custom_cmap, s=60, marker='o', 
                alpha=0.9, linewidth=1, edgecolor='black', 
                vmin=0, vmax=len(warna_hex)-1) 
    
    plt.title(f'Batas Keputusan SVM - {gender_name}')
    plt.xlabel('Usia')
    plt.ylabel('Berat Badan (kg)')


plt.figure(figsize=(16, 7))

plt.subplot(1, 2, 1)
plot_decision_boundaries(0, 'Laki-laki')

plt.subplot(1, 2, 2)
plot_decision_boundaries(1, 'Perempuan')


patches = [mpatches.Patch(color=warna_hex[i], label=labels[i]) for i in range(len(labels))]
plt.figlegend(handles=patches, loc='lower center', ncol=len(labels), borderaxespad=0.1)

plt.tight_layout(rect=[0, 0.05, 1, 1]) 
plt.show()

paket_SVM = {'model_pipeline': pipeline_bbu, 'label_encoder': le}
joblib.dump(paket_SVM, 'mesin_svm_bbu.pkl')
print("Model Pipeline berhasil disimpan sebagai mesin_svm_bbu.pkl")