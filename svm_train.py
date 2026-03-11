import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from sklearn.decomposition import PCA
from mpl_toolkits.mplot3d import Axes3D


try:
    df = pd.read_csv('data_siap_training.csv')
    df = print (df.head())
    label_counts = df['status_gizi'].value_counts()
    print("\nDistribusi Kelas pada 'status_gizi':")
    
    colors = ['red', 'green', 'orange']
    label_counts_ordered = label_counts.reindex(['Gizi Buruk', 'Gizi Baik', 'Gizi Lebih'])
    
    plt.bar(label_counts_ordered.index, label_counts_ordered.values, colors=colors)
    
    plt.title("Visualisasi Data Antropometri Balita")
    plt.xlabel("Status GIZI")
    plt.ylabel("Jumlah Balita")
    plt.savefig('visualisasi_data_antropometri.png', dpi=300)
    plt.show()
    
except FileNotFoundError:
    print("Error: File 'data_siap_training.csv' tidak ditemukan.")
    exit()

#PEMILIHAN FITUR DAN TARGET
X = df[['z_bbu', 'z_tbu', 'z_imtu']]
y = df['status_gizi']
le = LabelEncoder()
y_encoded = le.fit_transform(y)

#SPLIT DATA
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# SCALING
scaler = MinMaxScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

#IMPLEMENTASI KERNEL TERBAIK
print("--- Melatih Model SVM Kernel RBF (C=100, Gamma=1) ---")
best_model = SVC(kernel='rbf', C=100, gamma=1, probability=True, random_state=42)
best_model.fit(X_train_s, y_train)

#EVALUASI MULTICLASS & BINER (Tetap untuk log)
y_pred = best_model.predict(X_test_s)
target_label = 'Gizi Buruk'
y_test_bin = np.where(y_test == target_label, 1, 0)
y_pred_bin = np.where(y_pred == target_label, 1, 0)
tn, fp, fn, tp = confusion_matrix(y_test_bin, y_pred_bin).ravel()

print("--- Membuat Pair Plot ---")
sns.set_theme(style="white")
plt.figure(figsize=(12, 10))
pair_plot = sns.pairplot(df, hue="status_gizi", palette="viridis", 
                         diag_kind="kde", markers=["o", "s", "D"],
                         plot_kws={'alpha': 0.6, 's': 40, 'edgecolor': 'w'})
pair_plot.fig.suptitle("Distribusi dan Korelasi Fitur Z-Score", y=1.02, fontsize=16)
plt.savefig('visual_pairplot_pro.png', dpi=300)


print("--- Membuat Professional 3D Scatter ---")
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

ax.xaxis.pane.fill = ax.yaxis.pane.fill = ax.zaxis.pane.fill = False
ax.grid(True, linestyle='--', alpha=0.3)

for status in le.classes_:
    subset = df[df['status_gizi'] == status]
    ax.scatter(subset['z_bbu'], subset['z_tbu'], subset['z_imtu'], 
               label=status, s=60, alpha=0.7, edgecolors='w', linewidth=0.5)

ax.set_xlabel('Z-Score BB/U', fontsize=11)
ax.set_ylabel('Z-Score TB/U', fontsize=11)
ax.set_zlabel('Z-Score IMT/U', fontsize=11)
ax.set_title('Penyebaran Data Balita dalam Ruang 3D', fontsize=14, pad=20)
ax.legend(title="Status Gizi", loc='upper left', bbox_to_anchor=(0.1, 0.9))


ax.view_init(elev=20, azim=135)

plt.tight_layout()
plt.savefig('visual_3d_scatter_clean.png', dpi=300)

pca = PCA(n_components=2)
X_train_pca = pca.fit_transform(X_train_s)
model_viz = SVC(kernel='rbf', C=100, gamma=1).fit(X_train_pca, le.transform(y_train))

fig_kt = plt.figure(figsize=(12, 8))
ax_kt = fig_kt.add_subplot(111, projection='3d')
z_proj = np.max(model_viz.decision_function(X_train_pca), axis=1)
scatter_kt = ax_kt.scatter(X_train_pca[:, 0], X_train_pca[:, 1], z_proj, 
                           c=le.transform(y_train), cmap='coolwarm', edgecolors='k', s=50, alpha=0.8)

# Atur label dan save
ax_kt.set_title('Kernel Trick: Proyeksi Data ke Dimensi Tinggi (Z-Axis)', fontsize=14)
plt.savefig('svm_kernel_trick_pro.png', dpi=300)

print("\n[INFO] Gambar 'visual_pairplot_pro.png' (Analisis Fitur) berhasil dibuat.")
print("[INFO] Gambar 'visual_3d_scatter_clean.png' (Penyebaran Data) berhasil dibuat.")
print("[INFO] Gambar 'svm_kernel_trick_pro.png' (Teknis SVM) berhasil dibuat.")