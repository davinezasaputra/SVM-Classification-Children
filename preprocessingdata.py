import pandas as pd
import numpy as np

# ===============================
# LOAD REFERENSI WHO
# ===============================
ref_tables = {
    'bbu_L': pd.read_csv('z_score_bbu_l.csv'),
    'bbu_P': pd.read_csv('z_score_bbu_p.csv'),
    'tbu_L': pd.read_csv('z_score_tbu_l.csv'),
    'tbu_P': pd.read_csv('z_score_tbu_p.csv'),
    'imtu_L': pd.read_csv('z_score_imtu_l.csv'),
    'imtu_P': pd.read_csv('z_score_imtu_p.csv')
}

# ===============================
# FUNGSI Z-SCORE (STABIL)
# ===============================
def get_zscore(nilai, umur, jk, tipe):

    key = f"{tipe}_{jk}"
    df = ref_tables[key]

    # Ambil umur terdekat
    idx = (df['umur'] - umur).abs().idxmin()
    row = df.loc[idx]

    median = row['Median']
    pos1 = row['+1 SD']
    neg1 = row['-1 SD']

    # SD rata-rata
    sd = (pos1 - neg1) / 2

    z = (nilai - median) / sd
    return z


# ===============================
# KATEGORI DETAIL
# ===============================
def klasifikasi(z_bbu, z_tbu, z_imtu):

    # BB/U
    if z_bbu < -3: bbu = "Gizi Buruk"
    elif z_bbu < -2: bbu = "Gizi Kurang"
    elif z_bbu <= 2: bbu = "Normal"
    else: bbu = "Gizi Lebih"

    # TB/U
    if z_tbu < -3: tbu = "Sangat Pendek"
    elif z_tbu < -2: tbu = "Pendek"
    elif z_tbu <= 3: tbu = "Normal"
    else: tbu = "Tinggi"

    # IMT/U
    if z_imtu < -3: imtu = "Sangat Kurus"
    elif z_imtu < -2: imtu = "Kurus"
    elif z_imtu <= 1: imtu = "Normal"
    elif z_imtu <= 2: imtu = "Gemuk"
    else: imtu = "Obesitas"

    return bbu, tbu, imtu


# ===============================
# STATUS UTAMA (WHO)
# ===============================
def status_utama(z_bbu, z_imtu):

    # Gizi Buruk
    if z_bbu < -3 or z_imtu < -3:
        return 0, "Gizi Buruk"

    # Gizi Lebih
    elif z_imtu > 2:
        return 2, "Gizi Lebih"

    # Normal
    else:
        return 1, "Normal"


# ===============================
# DIAGNOSA
# ===============================
def diagnosa(data):

    # Koreksi TB/PB
    if data['umur'] < 24 and data['posisi'] == 'berdiri':
        tb = data['tb'] + 0.7
    elif data['umur'] >= 24 and data['posisi'] == 'telentang':
        tb = data['tb'] - 0.7
    else:
        tb = data['tb']

    # IMT
    imt = data['bb'] / ((tb / 100) ** 2)

    # Z-score
    z_bbu = get_zscore(data['bb'], data['umur'], data['jk'], 'bbu')
    z_tbu = get_zscore(tb, data['umur'], data['jk'], 'tbu')
    z_imtu = get_zscore(imt, data['umur'], data['jk'], 'imtu')

    # Detail
    bbu, tbu, imtu_cat = klasifikasi(z_bbu, z_tbu, z_imtu)

    kode, status = status_utama(z_bbu, z_imtu)

    return {
        'status': status,
        'kode': kode,
        'z_bbu': round(z_bbu,2),
        'z_tbu': round(z_tbu,2),
        'z_imtu': round(z_imtu,2),
        'detail': (bbu, tbu, imtu_cat)
    }


# ===============================
# CONTOH
# ===============================
data = {
    'bb':12.5,
    'tb':90,
    'umur':24,
    'jk':'L',
    'posisi':'berdiri'
}

hasil = diagnosa(data)

print("\n=== HASIL DIAGNOSA ===")
print("Status :", hasil['status'])
print("Z BB/U :", hasil['z_bbu'])
print("Z TB/U :", hasil['z_tbu'])
print("Z IMT/U:", hasil['z_imtu'])
print("Detail :", hasil['detail'])
