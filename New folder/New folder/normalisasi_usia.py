import pandas as pd
import re


df = pd.read_csv('data_untuk_contoh_bab4.csv', encoding='utf-8')

def parse_usia(usia_str):
    if pd.isna(usia_str): return 0
    t_m = re.search(r'(\d+)\s*Tahun', usia_str)
    b_m = re.search(r'(\d+)\s*Bulan', usia_str)
    h_m = re.search(r'(\d+)\s*Hari', usia_str)
    t = int(t_m.group(1)) if t_m else 0
    b = int(b_m.group(1)) if b_m else 0
    h = int(h_m.group(1)) if h_m else 0
    return (t * 12) + b + (h / 30.0)

df['umur_bulan'] = df['Usia Saat Ukur'].apply(parse_usia)
print(df[['Usia Saat Ukur', 'umur_bulan']].head(20))

df.to_csv('data_untuk_contoh_bab4_usia_terkalibrasi.csv', index=False)
print("Data dengan usia terkalibrasi berhasil disimpan ke 'data_untuk_contoh_bab4_usia_terkalibrasi.csv'")
