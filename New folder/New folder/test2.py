import pandas as pd
import joblib
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

# 1. Load Data
df = pd.read_csv('DataGabungan.csv', encoding='windows-1252')

# 2. Preprocessing Z-Score (Mengabaikan ZS BB/TB)
for col in ['ZS BB/U', 'ZS TB/U']:
    df[col] = df[col].astype(str).str.replace(',', '.').str.replace(':', '.')
    df[col] = df[col].str.replace(r'[^\d.-]', '', regex=True)
    df[col] = pd.to_numeric(df[col], errors='coerce')
df = df.dropna(subset=['BB/TB']) # Pastikan target tidak kosong

# 1. Hapus label yang tidak masuk akal ('Outlier' dan '-')
df = df[~df['BB/TB'].isin(['Outlier', '-'])]

# 2. GABUNGKAN Gizi Buruk (1 data) ke Gizi Kurang biar bisa di-split!
df['BB/TB'] = df['BB/TB'].replace({
    'Gizi Buruk': 'Gizi Kurang/Buruk',
    'Gizi Kurang': 'Gizi Kurang/Buruk'
})

# Lanjut hapus missing values di fitur input sesuai skenario
# Kalau Skenario 1:
df = df.dropna(subset=['ZS BB/U', 'ZS TB/U'])
X_zs = df[['ZS BB/U', 'ZS TB/U']] # Hanya menggunakan 2 indikator
y_zs = df['BB/TB']

# 3. Model Training Pipeline
le_zs = LabelEncoder()
y_zs_encoded = le_zs.fit_transform(y_zs)

X_train, X_test, y_train, y_test = train_test_split(X_zs, y_zs_encoded, test_size=0.2, random_state=42, stratify=y_zs_encoded)

sm = SMOTE(random_state=42)
X_res, y_res = sm.fit_resample(X_train, y_train)

scaler = MinMaxScaler()
X_res_s = scaler.fit_transform(X_res)
X_test_s = scaler.transform(X_test)

svm_zs = SVC(kernel='rbf', C=1, gamma=10, probability=True, random_state=42)
svm_zs.fit(X_res_s, y_res)

print(f"Akurasi Skenario 2 (Z-Score): {accuracy_score(y_test, svm_zs.predict(X_test_s)) * 100:.2f}%")

# 4. Export untuk API
paket_ai_zs = {'model_svm': svm_zs, 'scaler': scaler, 'label_encoder': le_zs}
joblib.dump(paket_ai_zs, 'svm_puskesmas_zscore.pkl')