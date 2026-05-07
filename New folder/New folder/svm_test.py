import pandas as pd
import numpy as np
import joblib
import warnings
warnings.filterwarnings("ignore")

from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score

# =====================================
# 1. LOAD DATA
# =====================================
print("=== LOAD DATA ===")
df = pd.read_csv('DataGabungan.csv')
df.columns = df.columns.str.strip()

print("Kolom:", df.columns.tolist())

# =====================================
# 2. PREPROCESS
# =====================================
df['tgl_lahir'] = pd.to_datetime(df['tgl_lahir'], errors='coerce')
today = pd.to_datetime('today')
df['umur'] = (today - df['tgl_lahir']).dt.days / 30.4375

df = df.dropna(subset=['bb', 'tb', 'umur', 'jk'])

df = df[(df['umur'] >= 0) & (df['umur'] <= 60)]
df = df[(df['bb'] >= 2) & (df['bb'] <= 30)]
df = df[(df['tb'] >= 45) & (df['tb'] <= 120)]

# =====================================
# 3. LOAD WHO TABLE
# =====================================
ref_tables = {
    'bbtb_panjang_L': pd.read_csv('z_score_bbtb_panjang_l.csv'),
    'bbtb_tinggi_L': pd.read_csv('z_score_bbtb_tinggi_l.csv'),
    'bbtb_panjang_P': pd.read_csv('z_score_bbtb_panjang_p.csv'),
    'bbtb_tinggi_P': pd.read_csv('z_score_bbtb_tinggi_p.csv'),
}

def clean(series):
    return pd.to_numeric(series.astype(str).str.replace(',', '.'), errors='coerce')

def get_zscore(bb, tb, jk, umur):
    key = f"bbtb_panjang_{jk}" if umur < 24 else f"bbtb_tinggi_{jk}"
    df_ref = ref_tables[key]

    ref = clean(df_ref.iloc[:, 0])
    neg1 = clean(df_ref.iloc[:, 3])
    median = clean(df_ref.iloc[:, 4])
    pos1 = clean(df_ref.iloc[:, 5])

    idx = (ref - tb).abs().idxmin()
    sd = (pos1.iloc[idx] - neg1.iloc[idx]) / 2

    return (bb - median.iloc[idx]) / sd

# =====================================
# 4. LABEL WHO (TANPA MASUK KE FITUR)
# =====================================
def klasifikasi(z):
    if z < -3: return "Gizi Buruk"
    elif z < -2: return "Gizi Kurang"
    elif z <= 1: return "Gizi Baik"
    elif z <= 2: return "Risiko Gizi Lebih"
    elif z <= 3: return "Gizi Lebih"
    else: return "Obesitas"

print("\n=== GENERATE LABEL ===")

labels = []

for _, row in df.iterrows():
    try:
        z = get_zscore(row['bb'], row['tb'], row['jk'], row['umur'])
        label = klasifikasi(z)
    except:
        label = np.nan

    labels.append(label)

df['label'] = labels
df = df.dropna(subset=['label'])

# gabung kelas ekstrem
df['label'] = df['label'].replace({
    'Gizi Buruk': 'Gizi Kurang'
})

# =====================================
# 5. FITUR (TANPA Z-SCORE 🔥)
# =====================================
print("\n=== MENYIAPKAN FITUR ===")

le_jk = LabelEncoder()
df['jk_enc'] = le_jk.fit_transform(df['jk'])

X = df[['bb', 'tb', 'umur', 'jk_enc']]
y = df['label']

print("\nDistribusi Kelas:")
print(y.value_counts())

# =====================================
# 6. ENCODING LABEL
# =====================================
le = LabelEncoder()
y_enc = le.fit_transform(y)

# =====================================
# 7. SPLIT
# =====================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y_enc,
    test_size=0.2,
    random_state=42,
    stratify=y_enc
)

# =====================================
# 8. SCALING
# =====================================
scaler = MinMaxScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

# =====================================
# 9. CLASS WEIGHT
# =====================================
label_map = dict(zip(le.classes_, range(len(le.classes_))))
weights = {i: 1.0 for i in range(len(le.classes_))}

weights[label_map['Gizi Kurang']] = 3.0
weights[label_map['Risiko Gizi Lebih']] = 2.0
weights[label_map['Gizi Lebih']] = 3.0
weights[label_map['Obesitas']] = 2.0

# =====================================
# 10. TRAIN MODEL
# =====================================
print("\n=== TRAIN SVM VALID ===")

model = SVC(
    kernel='rbf',
    C=10,
    gamma='scale',
    class_weight=weights,
    probability=True
)

model.fit(X_train_s, y_train)

# =====================================
# 11. EVALUASI
# =====================================
y_pred = model.predict(X_test_s)

print(f"\nAkurasi: {accuracy_score(y_test, y_pred)*100:.2f}%")
print(classification_report(y_test, y_pred, target_names=le.classes_))

# =====================================
# 12. SAVE
# =====================================
joblib.dump({
    'model': model,
    'scaler': scaler,
    'label_encoder': le,
    'le_jk': le_jk
}, 'svm_valid_no_leakage.pkl')

print("\n🔥 MODEL VALID TANPA LEAKAGE SIAP")