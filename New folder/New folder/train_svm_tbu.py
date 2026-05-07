from matplotlib.colors import ListedColormap
import pandas as pd
import numpy as np
import re
import joblib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import seaborn as sns
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

print("Mulai Proses Training SVM untuk TB/U")

def standardisasi_tb(row):
    tb = row['tb']
    umur = row['usia']
    cara_ukur = str(row['posisi']).lower().strip()
    if umur < 24 and cara_ukur == 'berdiri': return tb + 0.7
    elif umur >= 24 and cara_ukur in ['telentang', 'terlentang']: return tb - 0.7
    return tb

print("Proses Load Data dan Preprocessing data tb")
df = pd.read_csv('data_tb.csv', encoding='utf-8')
print(df.head())
print(df.info())
print("Data berhasil dimuat, memulai preprocessing data...")

df['usia']
df['jk'] = df['jk'].map({'L': 0, 'P': 1})
df['tb_koreksi'] = df.apply(standardisasi_tb, axis=1)

X = df[['tb_koreksi', 'usia', 'jk']]
y = df['TB/U']
le = LabelEncoder()
print(le.fit(y))
print("normalisasi jenis kelamin berhasil, memulai split data...")
y_encoded = le.fit_transform(y) 
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)
print("Split data 80:20 berhasil")
print("proses training model")
langkah_langkah = [
    ('smote', SMOTE(random_state=42, k_neighbors=1)),
    ('scaler', MinMaxScaler()),
    ('svm', SVC(kernel='rbf', C=10, gamma=1, probability=True, random_state=42))
]

pipeline_tbu = ImbPipeline(steps=langkah_langkah)
pipeline_tbu.fit(X_train, y_train)


y_pred = pipeline_tbu.predict(X_test)

print("confusion matrix dan classification report")
cm = confusion_matrix(y_test, y_pred)
labels = le.inverse_transform(np.unique(y_test))

plt.figure(figsize=(10, 7))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
plt.title('Confusion Matrix: Klasifikasi TB/U')
plt.xlabel('Prediksi Model')
plt.ylabel('Kenyataan (Actual)')
plt.show()

print(f"Akurasi Final TB/U: {accuracy_score(y_test, y_pred) * 100:.2f}%\n")
print(classification_report(y_test, y_pred, target_names=le.inverse_transform(np.unique(y_test))))
print(f"\nproses training model selesai, membuat gambar hyperplane SVM")
warna_hex = [
    '#f1c40f',
    '#2ecc71',
    '#e67e22',
    '#c0392b'
]

custom_cmap = ListedColormap(warna_hex)
def plot_decision_boundaries(gender_val, gender_name):
    x_min, x_max = X['usia'].min() - 2, X['usia'].max() + 2
    y_min, y_max = X['tb_koreksi'].min() - 2, X['tb_koreksi'].max() + 2
    xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.5),
                         np.arange(y_min, y_max, 0.2))
    grid_df = pd.DataFrame({
        'tb_koreksi': yy.ravel(),             
        'usia': xx.ravel(),     
        'jk': np.full(xx.ravel().shape, gender_val)
    })
    Z = pipeline_tbu.predict(grid_df)
    Z = Z.reshape(xx.shape)
    plt.contourf(xx, yy, Z, alpha=0.35, cmap=custom_cmap)
    idx = X_test['jk'] == gender_val
    plt.scatter(X_test[idx]['usia'], X_test[idx]['tb_koreksi'], 
                c=y_test[idx], cmap=custom_cmap, s=60, marker='o', 
                alpha=0.9, linewidth=1, edgecolor='black', 
                vmin=0, vmax=len(warna_hex)-1) 
    
    plt.title(f'Batas Keputusan SVM - {gender_name}')
    plt.xlabel('Umur (Bulan)')
    plt.ylabel('TB Terkalibrasi')
plt.figure(figsize=(16, 7))
plt.subplot(1, 2, 1)
plot_decision_boundaries(0, 'Laki-laki')
plt.subplot(1, 2, 2)
plot_decision_boundaries(1, 'Perempuan')
patches = [mpatches.Patch(color=warna_hex[i], label=labels[i]) for i in range(len(labels))]
plt.figlegend(handles=patches, loc='lower center', ncol=len(labels), borderaxespad=0.1)
plt.tight_layout(rect=[0, 0.05, 1, 1]) 
plt.show()

paket_SVM = {'model_pipeline': pipeline_tbu, 'label_encoder': le}
joblib.dump(paket_SVM, 'mesin_svm_tbu.pkl')
print("Model Pipeline berhasil disimpan sebagai mesin_svm_tbu.pkl")