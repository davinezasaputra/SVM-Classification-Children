import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import sklearn
import re
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn import datasets
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.pipeline import Pipeline



load_data = pd.read_csv('DataGabungan.csv', encoding='utf-8')
print(load_data.info())
print(load_data.head())


load_data['jk'] = load_data['jk'].map({'L': 0, 'P': 1})
load_data['status_gizi'] = load_data['BB/TB'].map({'Gizi Baik': 0, 'Risiko Gizi Lebih' : 1, 'Gizi Kurang': 2, 'Gizi Lebih': 3, 'Gizi Buruk': 4, 'Obesitas': 5})
load_data['label_BB'] = load_data['BB/U'].map({'Normal': 0, 'Kurang': 1, 'R1siko Lebih': 2,  'Sangat Kurang': 3})
load_data['label_TB'] = load_data['TB/U'].map({'Normal': 0, 'Pendek': 1, 'Sangat Pendek': 2, 'Tinggi': 4})
load_data['label_Cara_Ukur'] = load_data['Cara Ukur'].map({'Terlentang': 0, 'Berdiri': 1})

print(load_data[['jk', 'status_gizi', 'label_BB', 'label_TB', 'label_Cara_Ukur']].head())

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
load_data['umur_bulan'] = load_data['Usia Saat Ukur'].apply(parse_usia)
print(load_data['umur_bulan'].head())

# Daftar kolom yang ingin diperiksa
cols_to_check = ['BB/U', 'TB/U', 'BB/TB', 'Cara Ukur']
load_data = load_data.copy()

for col in cols_to_check:
    load_data = load_data[~load_data[col].isin(['Outlier', '-'])]

x = load_data.loc[:, ['jk', 'umur_bulan', 'bb', 'tb', 'label_Cara_Ukur']]
y = load_data['status_gizi']

x_train, x_test, y_train, Y_test = train_test_split(x, y, test_size = 0.2, random_state = 0)

Pipeline = ImbPipeline([
    ('scaler', MinMaxScaler()),
    ('SMOTE', SMOTE(random_state = 42, k_neighbors=3)),
    ('SVM', SVC(kernel='rbf',decision_function_shape='ovo'))
])
param_grid = {
    'SVM__C': [0.1, 1, 10],
   'SVM__gamma': [0.01, 0.1, 1, 5, 10, 20, 50]
}

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

grid_seach = GridSearchCV(
    estimator=Pipeline,
    param_grid=param_grid,
    n_jobs=4,
    cv=skf,
    verbose=1,
    scoring='accuracy'
)
grid_seach.fit(x_train, y_train)

best_params = grid_seach.best_params_
print(f"Best Parameters: {best_params}")


accuracy_scores = []

for training_index, test_index in skf.split(x_train, y_train):
    x_train_fold, x_val_fold = x_train.iloc[training_index], x_train.iloc[test_index]
    y_train_fold, y_val_fold = y_train.iloc[training_index], y_train.iloc[test_index]
    
    Pipeline.fit(x_train_fold, y_train_fold)
    y_pred_fold = Pipeline.predict(x_val_fold)
    
    accuracy = accuracy_score(y_val_fold, y_pred_fold)
    accuracy_scores.append(accuracy)
    
for i, accuracy in enumerate(accuracy_scores):
    print(f"Fold {i+1} Accuracy: {accuracy * 100:.2f}%")
    
print(f"Mean Accuracy: {sum(accuracy_scores) / len(accuracy_scores) *100:.2f}%")
print (classification_report(y_val_fold.values.reshape(-1, 1), y_pred_fold))

print(f" accuracy model SVM : {accuracy *100:.2f}%")

cm = confusion_matrix(y_val_fold, y_pred_fold)

plt.figure(figsize=(8,6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.xlabel('Nilai Prediksi')
plt.ylabel('Nilai Aktual')
plt.title('Confusion Matrix')
plt.savefig('confusion_matrix.png')
print("Confusion Matrix telah disimpan sebagai 'confusion_matrix.png'")


df = pd.DataFrame({'kelas': y_train})
jumlah_data_per_kelas = df['kelas'].value_counts()
print(jumlah_data_per_kelas)

df = pd.DataFrame({'Status Gizi': Y_test})
jumlah_data_per_kelas = df['Status Gizi'].value_counts()
print(jumlah_data_per_kelas)



