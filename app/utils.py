import os
import math
import pandas as pd

def inisialisasi_data_who():
    base_direct = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    base = os.path.join(base_direct, "data_who/")
    try:
        print("Memuat data referensi WHO")
        return {
            'bbu_L': pd.read_csv(base+'z_score_bbu_l.csv'), 'bbu_P': pd.read_csv(base+'z_score_bbu_p.csv'),
            'tbu_L': pd.read_csv(base+'z_score_tbu_l.csv'), 'tbu_P': pd.read_csv(base+'z_score_tbu_p.csv'),
            'bbtb_panjang_L': pd.read_csv(base+'z_score_bbtb_panjang_l.csv'),
            'bbtb_tinggi_L': pd.read_csv(base+'z_score_bbtb_tinggi_l.csv'),
            'bbtb_panjang_P': pd.read_csv(base+'z_score_bbtb_panjang_p.csv'),
            'bbtb_tinggi_P': pd.read_csv(base+'z_score_bbtb_tinggi_p.csv'),
        }
    except Exception as e:
        print(f"Warning: File CSV WHO gagal dimuat. Error: {e}")
        return None

referensi_who = inisialisasi_data_who()

def kalkulasi_z_score(nilai, ref_val, jk, tipe, umur=None):
    if referensi_who is None:
        return 0

    if tipe == 'bbtb':
        key = f"bbtb_panjang_{jk}" if umur < 24 else f"bbtb_tinggi_{jk}"
    else:
        key = f"{tipe}_{jk}"
    
    df = referensi_who[key]
    def clean(s): return pd.to_numeric(s.astype(str).str.replace(',', '.').str.strip(), errors='coerce')
    
    col_ref = clean(df.iloc[:, 0])
    exact_match = df[col_ref == ref_val]
    
    if not exact_match.empty:
        idx = exact_match.index[0]
        L, M, S = clean(df.iloc[:, 1]).iloc[idx], clean(df.iloc[:, 2]).iloc[idx], clean(df.iloc[:, 3]).iloc[idx]
    else:
        bawah = df[col_ref < ref_val]
        atas = df[col_ref > ref_val]
        
        if bawah.empty:
            idx = atas.index[0]
            L, M, S = clean(df.iloc[:, 1]).iloc[idx], clean(df.iloc[:, 2]).iloc[idx], clean(df.iloc[:, 3]).iloc[idx]
        elif atas.empty:
            idx = bawah.index[-1]
            L, M, S = clean(df.iloc[:, 1]).iloc[idx], clean(df.iloc[:, 2]).iloc[idx], clean(df.iloc[:, 3]).iloc[idx]
        else:
            idx1, idx2 = bawah.index[-1], atas.index[0]
            x1, x2 = col_ref.iloc[idx1], col_ref.iloc[idx2]
            L1, L2 = clean(df.iloc[:, 1]).iloc[idx1], clean(df.iloc[:, 1]).iloc[idx2]
            M1, M2 = clean(df.iloc[:, 2]).iloc[idx1], clean(df.iloc[:, 2]).iloc[idx2]
            S1, S2 = clean(df.iloc[:, 3]).iloc[idx1], clean(df.iloc[:, 3]).iloc[idx2]
            
            rasio = (ref_val - x1) / (x2 - x1)
            L = L1 + rasio * (L2 - L1)
            M = M1 + rasio * (M2 - M1)
            S = S1 + rasio * (S2 - S1)

    if L == 0:
        z_ind = math.log(nilai / M) / S
    else:
        z_ind = (((nilai / M)**L) - 1) / (L * S)

    if z_ind > 3:
        sd3_pos = M * (1 + L * S * 3)**(1/L)
        sd2_pos = M * (1 + L * S * 2)**(1/L)
        z_final = 3 + ((nilai - sd3_pos) / (sd3_pos - sd2_pos))
    elif z_ind < -3:
        sd3_neg = M * (1 + L * S * -3)**(1/L)
        sd2_neg = M * (1 + L * S * -2)**(1/L)
        z_final = -3 + ((nilai - sd3_neg) / (sd2_neg - sd3_neg))
    else:
        z_final = z_ind

    return z_final
    
def check_outlier_data(z_bbu, z_tbu, z_bbtb):
    if abs(z_bbu) > 5 or abs(z_tbu) > 5 or abs(z_bbtb) > 5:
        return True
    return False