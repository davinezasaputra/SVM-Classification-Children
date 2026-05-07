# Library import
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import seaborn as sns
import re
from imblearn.combine import SMOTETomek
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from sklearn.decomposition import PCA
from mpl_toolkits.mplot3d import Axes3D
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Load dan Preprosesing data
try:
    df = pd.read_csv('data_gizi.csv', encoding='windows-1252')
    print(df.head())
    
    
    for col in ['ZS BB/U', 'ZS TB/U', 'ZS BB/TB']:
        df[col] = df[col].astype(str).str.replace(',', '.').str.replace(':', '.')
        df[col] = df[col].str.replace(r'[^\d.-]', '', regex=True)
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    df = df.dropna(subset=['ZS BB/U', 'ZS TB/U', 'ZS BB/TB', 'BB/TB'])
    
    
    df = df[df['BB/TB'] != 'Outlier']

    label_counts = df['BB/TB'].value_counts()
    print("\nDistribusi Kelas pada 'BB/TB' (Setelah Cleaning):")
    print(label_counts)
    
    
    colors = ['red', 'green', 'orange', 'blue', 'purple'][:len(label_counts)]
    
    plt.bar(label_counts.index, label_counts.values, color=colors)
    plt.title("Visualisasi Data Antropometri Balita")
    plt.xlabel("Status GIZI")
    plt.ylabel("Jumlah Balita")
    plt.savefig('visualisasi_data_antropometri.png', dpi=300)
    plt.close() 
    
except FileNotFoundError:
    print("Error: File 'data_gizi.csv' tidak ditemukan.")
    exit()


X = df[['ZS BB/U', 'ZS TB/U', 'ZS BB/TB']]
y = df['BB/TB']

le = LabelEncoder()
y_encoded = le.fit_transform(y) 


X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)

#smote dan tomek data imbalance
print("\n--- Menjalankan SMOTE & Tomek Links ---")
smt = SMOTETomek(random_state=42)
X_train_resampled, y_train_resampled = smt.fit_resample(X_train, y_train)

print(f"Jumlah data training SEBELUM SMOTE: {len(X_train)}")
print(f"Jumlah data training SESUDAH SMOTE: {len(X_train_resampled)}")


scaler = MinMaxScaler()
X_train_s = scaler.fit_transform(X_train_resampled)
X_test_s = scaler.transform(X_test)
#training model svm dengan kernel rbf 

print("\n--- Melatih Model SVM Kernel RBF (C=100, Gamma=1) ---")
best_model = SVC(kernel='rbf', C=100, gamma=1, probability=True, random_state=42)

best_model.fit(X_train_s, y_train_resampled) 

y_pred = best_model.predict(X_test_s)

print("\n==================================================")
print("HASIL EVALUASI MODEL SVM")
print("==================================================")
akurasi = accuracy_score(y_test, y_pred)
print(f"Akurasi Model : {akurasi * 100:.2f}%\n")

print("Classification Report:")
target_names = le.inverse_transform(np.unique(y_test))
print(classification_report(y_test, y_pred, target_names=target_names, zero_division=0))
print("==================================================\n")



try:
    target_label_encoded = le.transform(['Gizi Kurang'])[0]
    y_test_bin = np.where(y_test == target_label_encoded, 1, 0)
    y_pred_bin = np.where(y_pred == target_label_encoded, 1, 0)
    tn, fp, fn, tp = confusion_matrix(y_test_bin, y_pred_bin).ravel()
except ValueError:
    pass 


print("--- Membuat Pair Plot ---")
sns.set_theme(style="white")
plt.figure(figsize=(12, 10))

pair_plot = sns.pairplot(df[['ZS BB/U', 'ZS TB/U', 'ZS BB/TB', 'BB/TB']], hue="BB/TB", palette="viridis", 
                         plot_kws={'alpha': 0.6, 's': 40, 'edgecolor': 'w'})
pair_plot.fig.suptitle("Distribusi dan Korelasi Fitur Z-Score", y=1.02, fontsize=16)
plt.savefig('visual_pairplot_pro.png', dpi=300)
plt.close()

# visualisasi
print("--- Membuat Professional 3D Scatter ---")
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
ax.xaxis.pane.fill = ax.yaxis.pane.fill = ax.zaxis.pane.fill = False
ax.grid(True, linestyle='--', alpha=0.3)

for status in le.classes_:
    subset = df[df['BB/TB'] == status]
    ax.scatter(subset['ZS BB/U'], subset['ZS TB/U'], subset['ZS BB/TB'], 
               label=status, s=60, alpha=0.7, edgecolors='w', linewidth=0.5)

ax.set_xlabel('Z-Score BB/U', fontsize=11)
ax.set_ylabel('Z-Score TB/U', fontsize=11)
ax.set_zlabel('Z-Score BB/TB', fontsize=11)
ax.set_title('Penyebaran Data Balita dalam Ruang 3D', fontsize=14, pad=20)
ax.legend(title="Status Gizi", loc='upper left', bbox_to_anchor=(0.1, 0.9))
ax.view_init(elev=20, azim=135)
plt.tight_layout()
plt.savefig('visual_3d_scatter_clean.png', dpi=300)
plt.close()


print("--- Membuat Visualisasi Confusion Matrix ---")
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=target_names, yticklabels=target_names,
            linewidths=0.5, linecolor='black')
plt.title('Confusion Matrix - Model SVM (Kernel RBF)', fontsize=14, pad=15)
plt.xlabel('Prediksi (Predicted Label)', fontsize=12)
plt.ylabel('Aktual (True Label)', fontsize=12)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('visual_confusion_matrix.png', dpi=300)
plt.close()

pca = PCA(n_components=2)
X_train_pca = pca.fit_transform(X_train_s)
model_viz = SVC(kernel='rbf', C=100, gamma=1).fit(X_train_pca, y_train_resampled)

fig_kt = plt.figure(figsize=(12, 8))
ax_kt = fig_kt.add_subplot(111, projection='3d')
z_proj = np.max(model_viz.decision_function(X_train_pca), axis=1)
scatter_kt = ax_kt.scatter(X_train_pca[:, 0], X_train_pca[:, 1], z_proj, 
                           c=y_train_resampled, cmap='coolwarm', edgecolors='k', s=50, alpha=0.8)

ax_kt.set_title('Kernel Trick: Proyeksi Data ke Dimensi Tinggi (Z-Axis)', fontsize=14)
plt.savefig('svm_kernel_trick_pro.png', dpi=300)
plt.close()




print("\n--- Menyimpan Data Hasil SMOTE ke CSV ---")

df_smote = pd.DataFrame(X_train_resampled, columns=['ZS BB/U', 'ZS TB/U', 'ZS BB/TB'])


df_smote['BB/TB'] = le.inverse_transform(y_train_resampled)


df_smote.to_csv('data_hasil_smotetomek.csv', index=False, sep=';')

print("[INFO] File 'data_hasil_smotetomek.csv' berhasil dibuat! Silakan cek folder project Anda.")


print("\n[INFO] SEMUA PROSES SELESAI. Cek folder untuk melihat gambar PNG-nya.")