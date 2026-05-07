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
        nik_ibu = data['nik_ibu']
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

        if check_outlier_data(z_bbu, z_tbu, z_bbtb):
            return jsonify({
                'status': 'warning',
                'message': 'Data terdeteksi Outlier! Periksa kembali input Berat dan Tinggi Badan.',
                'z_score': {'bbu': round(z_bbu, 2), 'tbu': round(z_tbu, 2), 'bbtb': round(z_bbtb, 2)}
            }), 200
        desa = data.get('desa')
        lat_input = data.get('latitude')
        lng_input = data.get('longitude')
        
        latitude = float(lat_input) if lat_input else None
        longitude = float(lng_input) if lng_input else None
        # bagian simpan data
        anak = Anak.query.filter_by(nik_ibu=nik_ibu, nama_anak=nama_anak).first()
        if not anak:
            ibu_ada = Anak.query.filter_by(nik_ibu=nik_ibu).first()
            if ibu_ada:
                desa_final = ibu_ada.desa
                lat_final = ibu_ada.latitude
                lng_final = ibu_ada.longitude
            else:
                desa_final = desa
                lat_final = latitude
                lng_final = longitude

            anak = Anak(
                nik_ibu=nik_ibu, nama_ibu=nama_ibu, nama_anak=nama_anak, 
                jk=jk, tanggal_lahir=tanggal_lahir,
                desa=desa_final, latitude=lat_final, longitude=lng_final # <-- Simpan lokasi di sini
            )
            db.session.add(anak)
            db.session.flush()

        catatan = PemantauanPerkembanganGiziAnak(
            anak_id=anak.id, usia_bulan=round(umur_bulan, 2), bb=bb, tb=tb_input, 
            posisi_ukur=posisi, 
            z_bbu=z_bbu, status_bbu=status_bbu_SVM, 
            z_tbu=z_tbu, status_tbu=status_tbu_SVM, 
            z_bbtb=z_bbtb, kesimpulan_svm=status_bbtb_SVM
        )
        db.session.add(catatan)
        message_log = f"menambahkan data pengukuran gizi untuk anak: {nama_anak} (NIK Ibu: {nik_ibu}) oleh {current_user.nama}"
        new_log = LogAktivitas(user_id=current_user.id, aksi= message_log)
        db.session.add(new_log)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'hasil_indikator': {
                'bbu': {'z': round(z_bbu, 2), 'status': status_bbu_SVM},
                'tbu': {'z': round(z_tbu, 2), 'status': status_tbu_SVM},
            },
            'kesimpulan_svm': status_bbtb_SVM,
            'confidence': f"{round(prob_bbtb, 2)}%"
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
                'id': anak.id, 'nik_ibu': anak.nik_ibu, 'nama_ibu': anak.nama_ibu, 
                'nama_anak': anak.nama_anak, 'jk': 'Laki-laki' if anak.jk == 'L' else 'Perempuan',
                'status_terakhir': kia.kesimpulan_svm if kia else 'Belum ada data'
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
    new_log = LogAktivitas(user_id=current_user.id, action= message_log)
    db.session.add(new_log)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Data dihapus'})

@api.route('/api/v1/search', methods=['GET'])
@login_required
def api_search():
    try:
        query = request.args.get('q', '').strip()
        if not query: return jsonify({'status': 'success', 'data': []})

        hasil = Anak.query.filter(
            (Anak.nik_ibu.like(f'%{query}%')) | (Anak.nama_anak.like(f'%{query}%'))
        ).limit(20).all()
        
        data_list = []
        for a in hasil:
            kia = PemantauanPerkembanganGiziAnak.query.filter_by(anak_id=a.id).order_by(PemantauanPerkembanganGiziAnak.tanggal_ukur.desc()).first()
            data_list.append({
                'nik_ibu': a.nik_ibu, 'nama_anak': a.nama_anak, 'nama_ibu': a.nama_ibu,
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

@api.route('/api/v1/cek-ortu/<nik_ibu>', methods=['GET'])
@login_required
def cek_ortu(nik_ibu):
    # Cari apakah ada anak yang terdaftar dengan NIK ibu tersebut
    data_lama = Anak.query.filter_by(nik_ibu=nik_ibu).first()
    if data_lama:
        return jsonify({
            'exists': True,
            'desa': data_lama.desa,
            'lat': data_lama.latitude,
            'lng': data_lama.longitude
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
                'no': no,
                'nik_ibu': anak.nik_ibu,
                'nama_ibu': anak.nama_ibu,
                'nama_anak': anak.nama_anak,
                'jk': anak.jk,
                'tgl_lahir': tgl_lahir.strftime('%Y-%m-%d'),
                'BB Lahir': '-',  # Kosongkan jika belum ada di database
                'TB Lahir': '-',  # Kosongkan jika belum ada di database
                'usia': usia_format,
                'Tanggal Pengukuran': tgl_ukur.strftime('%Y-%m-%d'),
                'bb': catatan.bb,
                'tb': catatan.tb,
                'Cara Ukur': catatan.posisi_ukur.capitalize(),
                'LiLA': '-',      # Kosongkan jika belum ada di database
                'BB/U': catatan.status_bbu,
                'ZS BB/U': round(catatan.z_bbu, 2) if catatan.z_bbu else '',
                'TB/U': catatan.status_tbu,
                'ZS TB/U': round(catatan.z_tbu, 2) if catatan.z_tbu else '',
                'BB/TB': catatan.kesimpulan_svm,
                'z_bbtb': round(catatan.z_bbtb, 2) if catatan.z_bbtb else ''
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