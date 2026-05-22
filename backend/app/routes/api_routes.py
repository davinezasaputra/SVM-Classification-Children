import io
import pandas as pd
from datetime import date , datetime
from sqlalchemy import func
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from app import db
from app.models import Anak, PemantauanPerkembanganGiziAnak, LogAktivitas
from app.utils import kalkulasi_z_score, check_outlier_data


from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from flask import send_file, make_response

from app.SVM import pipeline_bbu, label_bbu, pipeline_tbu, label_tbu, pipeline_bbtb, label_bbtb

api = Blueprint('api', __name__)

@api.route('/api/v1/predict', methods=['POST'])
@login_required
def api_predict():
    data = request.get_json()
    try:
        tanggal_lahir = datetime.strptime(data['tanggal_lahir'], '%Y-%m-%d').date()
        tanggal_ukur = date.today()
        selisih_hari = (tanggal_ukur - tanggal_lahir).days
        umur_bulan = selisih_hari / 30.4375 
        nama_ibu = data['nama_ibu']
        nama_anak = data['nama_anak']
        jk = data['jk'].upper() 
        bb = float(data['berat_badan'])
        tb_input = float(data['tinggi_badan'])
        posisi = data['posisi_pengukuran'].lower()
        
        if umur_bulan < 24:
            posisi = 'telentang' 
            
        tb_terkalibrasi = tb_input
        if umur_bulan < 24 and posisi == 'berdiri': 
            tb_terkalibrasi += 0.7
        elif umur_bulan >= 24 and posisi in ['telentang', 'terlentang']: 
            tb_terkalibrasi -= 0.7

        # bagian normalisasi jenis kelamin untuk model SVM
        jk_encoded = 1 if jk == 'P' else 0
        
        # bagian untuk mempersiapkan data sesuai dengan pipeline SVM
        df_bbu = pd.DataFrame({'bb': [bb], 'usia': [umur_bulan], 'jk': [jk_encoded]})
        df_tbu = pd.DataFrame({'tb_koreksi': [tb_terkalibrasi], 'usia': [umur_bulan], 'jk': [jk_encoded]})
        df_bbtb = pd.DataFrame({'bb': [bb], 'tb_koreksi': [tb_terkalibrasi], 'jk': [jk_encoded]})

        # prediksi SVM untuk seluruh indikator
        pred_bbu_idx = pipeline_bbu.predict(df_bbu)[0]
        status_bbu_SVM = label_bbu.inverse_transform([pred_bbu_idx])[0]

        pred_tbu_idx = pipeline_tbu.predict(df_tbu)[0]
        status_tbu_SVM = label_tbu.inverse_transform([pred_tbu_idx])[0]

        pred_bbtb_idx = pipeline_bbtb.predict(df_bbtb)[0]
        status_bbtb_SVM = label_bbtb.inverse_transform([pred_bbtb_idx])[0]
        
        prob_bbtb = max(pipeline_bbtb.predict_proba(df_bbtb)[0]) * 100
        if prob_bbtb < 40:
            status_bbtb_SVM = "model svm kurang akurat untuk data ini, tolong periksa kembali secara manual"

        # proses kalkulasi z-score
        z_bbu = kalkulasi_z_score(bb, umur_bulan, jk, 'bbu')
        z_tbu = kalkulasi_z_score(tb_terkalibrasi, umur_bulan, jk, 'tbu')
        z_bbtb = kalkulasi_z_score(bb, tb_terkalibrasi, jk, 'bbtb', umur=umur_bulan)
        
        is_outlier = check_outlier_data(z_bbu, z_tbu, z_bbtb)
        if is_outlier:
            status_bbu_SVM = "Outlier"
            status_tbu_SVM = "Outlier"
            status_bbtb_SVM = "Outlier"
            prob_bbtb = 0
            
        nik_balita = data.get('nik_balita')
        nama_ayah = data.get('nama_ayah')
        bb_lahir = float(data.get('bb_lahir')) if data.get('bb_lahir') else None
        tb_lahir = float(data.get('tb_lahir')) if data.get('tb_lahir') else None
        
        desa = data.get('desa')
        latitude = float(data.get('latitude')) if data.get('latitude') else None
        longitude = float(data.get('longitude')) if data.get('longitude') else None
        
        ntob = data.get('ntob', 'B')
        imunisasi = data.get('imunisasi', 'Tidak')
        vit_a = data.get('vit_a', 'Tidak')
        # bagian simpan data
        anak = Anak.query.filter_by(nik_balita=nik_balita).first()
        
        if not anak:
            # Jika belum ada, buat record anak baru
            anak = Anak(
                nik_balita=nik_balita, 
                nama_anak=nama_anak, 
                jk=jk, 
                tanggal_lahir=tanggal_lahir,
                nama_ibu=nama_ibu,
                nama_ayah=nama_ayah,
                bb_lahir=bb_lahir,
                tb_lahir=tb_lahir,
                desa=desa, 
                latitude=latitude, 
                longitude=longitude
            )
            db.session.add(anak)
            db.session.flush()

        catatan = PemantauanPerkembanganGiziAnak(
            anak_id=anak.id, 
            usia_bulan=round(umur_bulan, 2), 
            bb=bb, 
            tb=tb_input, 
            posisi_ukur=posisi, 
            ntob=ntob,              # Simpan status NTOB
            imunisasi=imunisasi,    # Simpan status Imunisasi
            vit_a=vit_a,            # Simpan status Vitamin A
            z_bbu=z_bbu, status_bbu=status_bbu_SVM, 
            z_tbu=z_tbu, status_tbu=status_tbu_SVM, 
            z_bbtb=z_bbtb, kesimpulan_svm=status_bbtb_SVM
        )
        db.session.add(catatan)
        message_log = f"menambahkan data pengukuran gizi untuk anak: {nama_anak} (NIK: {nik_balita}) oleh {current_user.nama}"
        db.session.add(LogAktivitas(user_id=current_user.id, aksi=message_log))
        db.session.commit()

        return jsonify({
            'status': 'success',
            'is_outlier' : is_outlier,
            'hasil_indikator': {
                'bbu': {'z': round(z_bbu, 2), 'status': status_bbu_SVM},
                'tbu': {'z': round(z_tbu, 2), 'status': status_tbu_SVM},
                'bbtb': {'z': round(z_bbtb, 2), 'status': status_bbtb_SVM}
            },
            'kesimpulan_svm': status_bbtb_SVM,
            'confidence': f"{round(prob_bbtb, 2)}%" if not is_outlier else "0%"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400

@api.route('/api/v1/anak', methods=['GET'])
@login_required
def api_get_semua_anak():
    try:
        semua_anak = Anak.query.order_by(Anak.tanggal_daftar.desc()).all()
        hasil = []
        for anak in semua_anak:
            kia = PemantauanPerkembanganGiziAnak.query.filter_by(anak_id=anak.id).order_by(PemantauanPerkembanganGiziAnak.tanggal_ukur.desc()).first()
            hasil.append({
                'id': anak.id, 
                'nik_balita': anak.nik_balita, 
                'nama_ibu': anak.nama_ibu, 
                'nama_ayah': anak.nama_ayah,
                'nama_anak': anak.nama_anak, 
                'jk': 'Laki-laki' if anak.jk == 'L' else 'Perempuan',
                'status_terakhir': kia.kesimpulan_svm if kia else 'Belum ada data',
                'bb': kia.bb if kia else '',
                'tb': kia.tb if kia else '',
                'posisi_ukur': kia.posisi_ukur if kia else 'berdiri',
                'desa': anak.desa or '',
                'tanggal_lahir': anak.tanggal_lahir.strftime('%Y-%m-%d') if anak.tanggal_lahir else ''
            })
        return jsonify({'status': 'success', 'data': hasil})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api.route('/api/v1/anak/<int:id_anak>', methods=['DELETE'])
@login_required
def hapus_anak(id_anak):
    anak = Anak.query.get_or_404(id_anak)
    db.session.delete(anak)
    message_log = f"menghapus seluruh data anak termasuk data perkembangan anak: {anak.nama_anak} (NIK Ibu: {anak.nik_ibu}) oleh {current_user.nama}"
    new_log = LogAktivitas(user_id=current_user.id, aksi= message_log)
    db.session.add(new_log)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Data dihapus'})

@api.route('/api/v1/anak/<int:id_anak>', methods=['PUT'])
@login_required
def edit_anak(id_anak):
    data = request.get_json()
    anak = Anak.query.get_or_404(id_anak)
    
    try:
        if 'nama_anak' in data: anak.nama_anak = data['nama_anak']
        if 'nama_ibu' in data: anak.nama_ibu = data['nama_ibu']
        if 'nama_ayah' in data: anak.nama_ayah = data['nama_ayah']
        if 'jk' in data: anak.jk = data['jk']
        if 'desa' in data: anak.desa = data['desa']
        if 'tanggal_lahir' in data and data['tanggal_lahir']:
            anak.tanggal_lahir = datetime.strptime(data['tanggal_lahir'], '%Y-%m-%d').date()
        kia = PemantauanPerkembanganGiziAnak.query.filter_by(anak_id=anak.id).order_by(PemantauanPerkembanganGiziAnak.tanggal_ukur.desc()).first()
        
        if kia and ('berat_badan' in data or 'tinggi_badan' in data or 'posisi_pengukuran' in data):
            bb = float(data.get('berat_badan', kia.bb))
            tb_input = float(data.get('tinggi_badan', kia.tb))
            posisi = data.get('posisi_pengukuran', kia.posisi_ukur).lower()
            tgl_lahir = anak.tanggal_lahir
            tgl_ukur = kia.tanggal_ukur.date() if isinstance(kia.tanggal_ukur, datetime) else kia.tanggal_ukur
            selisih_hari = (tgl_ukur - tgl_lahir).days
            umur_bulan = selisih_hari / 30.4375
            
            if umur_bulan < 24:
                posisi = 'telentang'
                
            tb_terkalibrasi = tb_input
            if umur_bulan < 24 and posisi == 'berdiri': 
                tb_terkalibrasi += 0.7
            elif umur_bulan >= 24 and posisi in ['telentang', 'terlentang']: 
                tb_terkalibrasi -= 0.7

            jk_encoded = 1 if anak.jk == 'P' else 0
            df_bbu = pd.DataFrame({'bb': [bb], 'usia': [umur_bulan], 'jk': [jk_encoded]})
            df_tbu = pd.DataFrame({'tb_koreksi': [tb_terkalibrasi], 'usia': [umur_bulan], 'jk': [jk_encoded]})
            df_bbtb = pd.DataFrame({'bb': [bb], 'tb_koreksi': [tb_terkalibrasi], 'jk': [jk_encoded]})
            
            z_bbu = kalkulasi_z_score(bb, umur_bulan, anak.jk, 'bbu')
            z_tbu = kalkulasi_z_score(tb_terkalibrasi, umur_bulan, anak.jk, 'tbu')
            z_bbtb = kalkulasi_z_score(bb, tb_terkalibrasi, anak.jk, 'bbtb', umur=umur_bulan)
            
            is_outlier = check_outlier_data(z_bbu, z_tbu, z_bbtb)
            
            if is_outlier:
                status_bbu_SVM = "Outlier"
                status_tbu_SVM = "Outlier"
                status_bbtb_SVM = "Outlier"
            else:
                pred_bbu_idx = pipeline_bbu.predict(df_bbu)[0]
                status_bbu_SVM = label_bbu.inverse_transform([pred_bbu_idx])[0]

                pred_tbu_idx = pipeline_tbu.predict(df_tbu)[0]
                status_tbu_SVM = label_tbu.inverse_transform([pred_tbu_idx])[0]

                pred_bbtb_idx = pipeline_bbtb.predict(df_bbtb)[0]
                status_bbtb_SVM = label_bbtb.inverse_transform([pred_bbtb_idx])[0]

            # Update ke baris tabel database
            kia.bb = bb
            kia.tb = tb_input
            kia.posisi_ukur = posisi
            kia.z_bbu = z_bbu
            kia.status_bbu = status_bbu_SVM
            kia.z_tbu = z_tbu
            kia.status_tbu = status_tbu_SVM
            kia.z_bbtb = z_bbtb
            kia.kesimpulan_svm = status_bbtb_SVM

        message_log = f"Mengedit data profil & perbaikan nilai ukur anak: {anak.nama_anak} oleh {current_user.nama}"
        db.session.add(LogAktivitas(user_id=current_user.id, aksi=message_log))
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': 'Profil dan data perbaikan gizi berhasil diperbarui!'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400

@api.route('/api/v1/search', methods=['GET'])
@login_required
def api_search():
    try:
        query = request.args.get('q', '').strip()
        if not query: return jsonify({'status': 'success', 'data': []})

        hasil = Anak.query.filter((Anak.nik_balita.like(f'%{query}%')) | (Anak.nama_anak.like(f'%{query}%'))).limit(20).all()
        
        data_list = []
        for a in hasil:
            kia = PemantauanPerkembanganGiziAnak.query.filter_by(anak_id=a.id).order_by(PemantauanPerkembanganGiziAnak.tanggal_ukur.desc()).first()
            data_list.append({
                'nik_balita': a.nik_balita, 'nama_anak': a.nama_anak, 'nama_ibu': a.nama_ibu, 'nama_ayah': a.nama_ayah,
                'status_terakhir': kia.kesimpulan_svm if kia else 'Belum Diukur'
            })
        return jsonify({'status': 'success', 'data': data_list})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api.route('/api/v1/stats')
@login_required
def get_stats():
    try:
        desa_stats = db.session.query(Anak.desa, func.count(Anak.id)).group_by(Anak.desa).all()
        semua_anak = Anak.query.all()
        
        total_anak = len(semua_anak)
        gizi_buruk = 0
        stunting = 0
        gizi_baik = 0
        
        map_data = []
        gizi_kategori = {} # Menyimpan jumlah tiap kategori gizi untuk Pie Chart
        
        for a in semua_anak:
            # Ambil hanya pengukuran (PemantauanPerkembanganGiziAnak) paling terakhir/terbaru untuk anak ini
            kia = PemantauanPerkembanganGiziAnak.query.filter_by(anak_id=a.id).order_by(PemantauanPerkembanganGiziAnak.tanggal_ukur.desc()).first()
            
            if kia:
                # A. Kumpulkan data untuk Pie Chart
                status = kia.kesimpulan_svm if kia.kesimpulan_svm else "Belum Diukur"
                gizi_kategori[status] = gizi_kategori.get(status, 0) + 1
                
                # B. Hitung untuk 4 Kartu Angka di Dashboard Atas
                status_lower = status.lower()
                if 'buruk' in status_lower or 'kurang' in status_lower:
                    gizi_buruk += 1
                elif 'pendek' in status_lower or 'stunting' in status_lower:
                    stunting += 1
                elif 'baik' in status_lower or 'normal' in status_lower:
                    gizi_baik += 1
                
                # C. Kumpulkan titik koordinat untuk Peta Sebaran
                if a.latitude and a.longitude:
                    map_data.append({
                        'lat': a.latitude, 
                        'lng': a.longitude,
                        'nama': a.nama_anak, 
                        'status': status
                    })

        return jsonify({
            'status': 'success',
            'desa': dict(desa_stats), 
            'gizi': gizi_kategori, 
            'map': map_data,
            'summary': {
                'total': total_anak,
                'buruk': gizi_buruk,
                'stunting': stunting,
                'baik': gizi_baik
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api.route('/api/v1/cek-balita', methods=['GET'])
@login_required
def cek_balita():
    nik = request.args.get('nik')
    nama = request.args.get('nama')
    
    data_lama = None
    
    if nik:
        data_lama = Anak.query.filter_by(nik_balita=nik).first()
    elif nama:
        data_lama = Anak.query.filter(Anak.nama_anak.ilike(f"%{nama}%")).first()

    if data_lama:
        return jsonify({
            'exists': True,
            'balita': {
                'nik_balita': data_lama.nik_balita,
                'nama_balita': data_lama.nama_anak,
                'nama_ibu': data_lama.nama_ibu,
                'nama_ayah': data_lama.nama_ayah,
                'tanggal_lahir': data_lama.tanggal_lahir.strftime('%Y-%m-%d') if data_lama.tanggal_lahir else None,
                'jk': data_lama.jk,
                'bb_lahir': data_lama.bb_lahir,
                'tb_lahir': data_lama.tb_lahir,
                'desa': data_lama.desa,
                'lat': data_lama.latitude,
                'lng': data_lama.longitude
            }
        })
        
    return jsonify({'exists': False})

@api.route('/api/v1/export-excel', methods=['GET'])
@login_required
def export_excel():
    try:
        # Tarik seluruh riwayat pengukuran (PemantauanPerkembanganGiziAnak) beserta data Anak-nya
        semua_catatan = db.session.query(PemantauanPerkembanganGiziAnak, Anak).join(Anak).order_by(PemantauanPerkembanganGiziAnak.tanggal_ukur.desc()).all()
        
        data_excel = []
        ada_alert_toleransi = False 
        no = 1
        
        for catatan, anak in semua_catatan:
            # 1. Hitung format usia (Tahun, Bulan, Hari) presisi tinggi
            tgl_ukur = catatan.tanggal_ukur.date()
            tgl_lahir = anak.tanggal_lahir
            selisih = relativedelta(tgl_ukur, tgl_lahir)
            
            usia_format = f"{selisih.years} tahun {selisih.months} bulan {selisih.days} hari"
            
            # 2. Cek untuk Alert Toleransi (Total Bulan)
            total_bulan = (selisih.years * 12) + selisih.months
            if 60 < total_bulan <= 70:
                ada_alert_toleransi = True
            
            # 3. Format Baris Excel sesuai header yang kamu minta
            data_excel.append({
               'No': no,
                'NIK Balita': anak.nik_balita,
                'Nama Balita': anak.nama_anak,
                'Jenis Kelamin': 'Laki-Laki' if anak.jk == 'L' else 'Perempuan',
                'Nama Ibu': anak.nama_ibu or '-',
                'Nama Ayah': anak.nama_ayah or '-',
                'Desa/Domisili': anak.desa or '-',
                'Tgl Lahir': tgl_lahir.strftime('%Y-%m-%d'),
                'BB Lahir (kg)': anak.bb_lahir if anak.bb_lahir else '-',
                'TB Lahir (cm)': anak.tb_lahir if anak.tb_lahir else '-',
                'Tgl Pengukuran': tgl_ukur.strftime('%Y-%m-%d'),
                'Usia Detail': usia_format,
                'Usia (Bulan)': catatan.usia_bulan,
                'BB Ukur (kg)': catatan.bb,
                'TB Ukur (cm)': catatan.tb,
                'Posisi Ukur': catatan.posisi_ukur.capitalize() if catatan.posisi_ukur else '-',
                'Tren N/T/O/B': catatan.ntob or '-',
                'Imunisasi': catatan.imunisasi or '-',
                'Vitamin A': catatan.vit_a or '-',
                'Z-Score BB/U': round(catatan.z_bbu, 2) if catatan.z_bbu is not None else '-',
                'Status BB/U': catatan.status_bbu or '-',
                'Z-Score TB/U': round(catatan.z_tbu, 2) if catatan.z_tbu is not None else '-',
                'Status TB/U': catatan.status_tbu or '-',
                'Z-Score BB/TB': round(catatan.z_bbtb, 2) if catatan.z_bbtb is not None else '-',
                'Kesimpulan Gizi (SVM)': catatan.kesimpulan_svm or '-'
            })
            no += 1

        df = pd.DataFrame(data_excel)
        
        # Simpan ke memori (tidak membuat file fisik di laptop)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Data Pengukuran Balita')
            
            # Merapikan lebar kolom otomatis
            worksheet = writer.sheets['Data Pengukuran Balita']
            for i, col in enumerate(df.columns):
                column_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(i, i, column_len)

        output.seek(0)
        
        # Kembalikan file Excel sebagai response
        response = make_response(send_file(output, as_attachment=True, download_name=f"Data_Export_SVM_{date.today()}.xlsx", mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))
        
        # Sisipkan custom header untuk memicu alert di JavaScript
        if ada_alert_toleransi:
            response.headers['X-Alert-Usia-Toleransi'] = 'true'
            response.headers['Access-Control-Expose-Headers'] = 'X-Alert-Usia-Toleransi'
            
        # Catat aktivitas ke log admin
        message_log = "Mengunduh (Export) seluruh data riwayat pengukuran balita ke Excel."
        db.session.add(LogAktivitas(user_id=current_user.id, aksi=message_log))
        db.session.commit()
            
        return response

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500