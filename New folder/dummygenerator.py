import pandas as pd
import numpy as np

np.random.seed(42)
num_samples = 1000

# 1. Simulasi Identitas & Data Mentah
umur_bulan = np.random.randint(0, 61, num_samples)

# Logika simulasi posisi ukur:
# Secara SOP: < 24 bulan (telentang), >= 24 bulan (berdiri)
# Kita buat 90% sesuai SOP dan 10% variasi untuk menguji fungsi koreksi 0.7cm
posisi_ukur = []
for u in umur_bulan:
    if u < 24:
        posisi_ukur.append(np.random.choice(['telentang', 'berdiri'], p=[0.9, 0.1]))
    else:
        posisi_ukur.append(np.random.choice(['berdiri', 'telentang'], p=[0.9, 0.1]))

data = {
    'id_anak': [f'ST-{i+1:04d}' for i in range(num_samples)],
    'jenis_kelamin': np.random.choice(['L', 'P'], num_samples),
    'umur_bulan': umur_bulan,
    'berat_badan': np.random.uniform(2.0, 25.0, num_samples), # dalam Kg
    'tinggi_badan': np.random.uniform(45.0, 120.0, num_samples), # dalam Cm
    'posisi_ukur': posisi_ukur
}

df_raw = pd.DataFrame(data)

# 2. Logic Tambahan: Hitung IMT Mentah
# (Ini IMT sebelum koreksi 0.7cm, hanya untuk kelengkapan data mentah)
df_raw['imt'] = df_raw['berat_badan'] / ((df_raw['tinggi_badan'] / 100) ** 2)

# Simpan sebagai file mentah dari Puskesmas
df_raw.to_csv('data_mentah_puskesmas.csv', index=False)
print("File 'data_mentah_puskesmas.csv' berhasil dibuat dengan kolom 'posisi_ukur'.")