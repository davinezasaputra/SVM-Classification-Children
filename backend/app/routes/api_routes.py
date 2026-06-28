import io
import pandas as pd
from datetime import date, datetime
from sqlalchemy import func
from flask import Blueprint, request, jsonify, send_file, make_response
from flask_login import login_required, current_user
from dateutil.relativedelta import relativedelta
from app import db
from app.models import Anak, PemantauanPerkembanganGiziAnak, LogAktivitas, OrangTua, LayananMedis
from app.utils import kalkulasi_z_score, check_outlier_data
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
        
        nama_ibu = data.get('nama_ibu')
        nama_ayah = data.get('nama_ayah')
        nama_anak = data['nama_anak']
        jk = data['jk'].upper() 
        bb = float(data['berat_badan'])
        tb_input = float(data['tinggi_badan'])
        posisi = data['posisi_pengukuran'].lower()
        
        if umur_bulan < 24: posisi = 'telentang' 
            
        tb_terkalibrasi = tb_input
        if umur_bulan < 24 and posisi == 'berdiri': tb_terkalibrasi += 0.7
        elif umur_bulan >= 24 and posisi in ['telentang', 'terlentang']: tb_terkalibrasi -= 0.7

        jk_encoded = 1 if jk == 'P' else 0
        df_bbu = pd.DataFrame({'bb': [bb], 'usia': [umur_bulan], 'jk': [jk_encoded]})
        df_tbu = pd.DataFrame({'tb_koreksi': [tb_terkalibrasi], 'usia': [umur_bulan], 'jk': [jk_encoded]})
        df_bbtb = pd.DataFrame({'bb': [bb], 'tb_koreksi': [tb_terkalibrasi], 'jk': [jk_encoded]})

        pred_bbu_idx = pipeline_bbu.predict(df_bbu)[0]
        status_bbu_SVM = label_bbu[pred_bbu_idx]

        pred_tbu_idx = pipeline_tbu.predict(df_tbu)[0]
        status_tbu_SVM = label_tbu[pred_tbu_idx]

        pred_bbtb_idx = pipeline_bbtb.predict(df_bbtb)[0]
        status_bbtb_SVM = label_bbtb[pred_bbtb_idx]

        prob_bbtb = max(pipeline_bbtb.predict_proba(df_bbtb)[0]) * 100
        if prob_bbtb < 40:
            status_bbtb_SVM = "model svm kurang akurat untuk data ini, tolong periksa kembali secara manual"

        z_bbu = kalkulasi_z_score(bb, umur_bulan, jk, 'bbu')
        z_tbu = kalkulasi_z_score(tb_terkalibrasi, umur_bulan, jk, 'tbu')
        z_bbtb = kalkulasi_z_score(bb, tb_terkalibrasi, jk, 'bbtb', umur=umur_bulan)
        
        is_outlier = check_outlier_data(z_bbu, z_tbu, z_bbtb)
        if is_outlier:
            status_bbu_SVM = status_tbu_SVM = status_bbtb_SVM = "Outlier"
            prob_bbtb = 0
            
        nik_balita = data.get('nik_balita')
        bb_lahir = float(data.get('bb_lahir')) if data.get('bb_lahir') else None
        tb_lahir = float(data.get('tb_lahir')) if data.get('tb_lahir') else None
        desa = data.get('desa')
        latitude = float(data.get('latitude')) if data.get('latitude') else None
        longitude = float(data.get('longitude')) if data.get('longitude') else None
        anak = Anak.query.filter_by(nik_balita=nik_balita).first()
        if not anak:
            orangtua = OrangTua.query.filter_by(nama_ibu=nama_ibu, nama_ayah=nama_ayah).first()
            if not orangtua:
                orangtua = OrangTua(nama_ibu=nama_ibu, nama_ayah=nama_ayah, desa=desa, latitude=latitude, longitude=longitude)
                db.session.add(orangtua)
                db.session.flush() 
                
            anak = Anak(orangtua_id=orangtua.id, nik_balita=nik_balita, nama_anak=nama_anak, jk=jk, 
                        tanggal_lahir=tanggal_lahir, bb_lahir=bb_lahir, tb_lahir=tb_lahir)
            db.session.add(anak)
            db.session.flush()

        catatan = PemantauanPerkembanganGiziAnak(
            anak_id=anak.id, kader_id=current_user.id,
            usia_bulan=round(umur_bulan, 2), bb=bb, tb=tb_input, posisi_ukur=posisi, ntob=data.get('ntob', 'B'),              
            z_bbu=z_bbu, status_bbu=status_bbu_SVM, z_tbu=z_tbu, status_tbu=status_tbu_SVM, 
            z_bbtb=z_bbtb, kesimpulan_svm=status_bbtb_SVM
        )
        db.session.add(catatan)
        db.session.flush()
        imunisasi = data.get('imunisasi', 'Tidak')
        vit_a = data.get('vit_a', 'Tidak')
        
        if imunisasi and imunisasi.lower() != 'tidak':
            for im in [i.strip() for i in imunisasi.split(',') if i.strip()]:
                db.session.add(LayananMedis(pemantauan_id=catatan.id, jenis_layanan=f"Imunisasi: {im}"))
        
        if vit_a and vit_a.lower() != 'tidak':
            for vit in [v.strip() for v in vit_a.split(',') if v.strip()]:
                db.session.add(LayananMedis(pemantauan_id=catatan.id, jenis_layanan=f"Vitamin A: {vit}"))

        message_log = f"menambahkan data pengukuran gizi untuk anak: {nama_anak} (NIK: {nik_balita}) oleh {current_user.nama}"
        db.session.add(LogAktivitas(user_id=current_user.id, aksi=message_log))
        db.session.commit()

        return jsonify({
            'status': 'success', 'is_outlier': is_outlier,
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
            ortu = anak.profil_orangtua
            hasil.append({
                'id': anak.id, 'nik_balita': anak.nik_balita, 'nama_anak': anak.nama_anak, 
                'nama_ibu': ortu.nama_ibu if ortu else '', 'nama_ayah': ortu.nama_ayah if ortu else '',
                'jk': 'Laki-laki' if anak.jk == 'L' else 'Perempuan',
                'status_terakhir': kia.kesimpulan_svm if kia else 'Belum ada data',
                'bb': kia.bb if kia else '', 'tb': kia.tb if kia else '',
                'posisi_ukur': kia.posisi_ukur if kia else 'berdiri',
                'desa': ortu.desa if ortu else '',
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
    message_log = f"menghapus seluruh data anak termasuk data perkembangan anak: {anak.nama_anak} oleh {current_user.nama}"
    db.session.add(LogAktivitas(user_id=current_user.id, aksi=message_log))
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Data dihapus'})

@api.route('/api/v1/anak/<int:id_anak>', methods=['PUT'])
@login_required
def edit_anak(id_anak):
    data = request.get_json()
    anak = Anak.query.get_or_404(id_anak)
    try:
        if 'nama_anak' in data: anak.nama_anak = data['nama_anak']
        if 'jk' in data: anak.jk = data['jk']
        if 'tanggal_lahir' in data and data['tanggal_lahir']:
            anak.tanggal_lahir = datetime.strptime(data['tanggal_lahir'], '%Y-%m-%d').date()
            
        if anak.profil_orangtua:
            if 'nama_ibu' in data: anak.profil_orangtua.nama_ibu = data['nama_ibu']
            if 'nama_ayah' in data: anak.profil_orangtua.nama_ayah = data['nama_ayah']
            if 'desa' in data: anak.profil_orangtua.desa = data['desa']

        kia = PemantauanPerkembanganGiziAnak.query.filter_by(anak_id=anak.id).order_by(PemantauanPerkembanganGiziAnak.tanggal_ukur.desc()).first()
        if kia and ('berat_badan' in data or 'tinggi_badan' in data or 'posisi_pengukuran' in data):
            bb = float(data.get('berat_badan', kia.bb))
            tb_input = float(data.get('tinggi_badan', kia.tb))
            posisi = data.get('posisi_pengukuran', kia.posisi_ukur).lower()
            
            tgl_lahir = anak.tanggal_lahir
            tgl_ukur = kia.tanggal_ukur.date() if isinstance(kia.tanggal_ukur, datetime) else kia.tanggal_ukur
            umur_bulan = (tgl_ukur - tgl_lahir).days / 30.4375
            
            if umur_bulan < 24: posisi = 'telentang'
            tb_terkalibrasi = tb_input
            if umur_bulan < 24 and posisi == 'berdiri': tb_terkalibrasi += 0.7
            elif umur_bulan >= 24 and posisi in ['telentang', 'terlentang']: tb_terkalibrasi -= 0.7

            jk_encoded = 1 if anak.jk == 'P' else 0
            df_bbu = pd.DataFrame({'bb': [bb], 'usia': [umur_bulan], 'jk': [jk_encoded]})
            df_tbu = pd.DataFrame({'tb_koreksi': [tb_terkalibrasi], 'usia': [umur_bulan], 'jk': [jk_encoded]})
            df_bbtb = pd.DataFrame({'bb': [bb], 'tb_koreksi': [tb_terkalibrasi], 'jk': [jk_encoded]})
            
            z_bbu = kalkulasi_z_score(bb, umur_bulan, anak.jk, 'bbu')
            z_tbu = kalkulasi_z_score(tb_terkalibrasi, umur_bulan, anak.jk, 'tbu')
            z_bbtb = kalkulasi_z_score(bb, tb_terkalibrasi, anak.jk, 'bbtb', umur=umur_bulan)
            
            if check_outlier_data(z_bbu, z_tbu, z_bbtb):
                kia.status_bbu = kia.status_tbu = kia.kesimpulan_svm = "Outlier"
            else:
                kia.status_bbu = label_bbu.inverse_transform([pipeline_bbu.predict(df_bbu)[0]])[0]
                kia.status_tbu = label_tbu.inverse_transform([pipeline_tbu.predict(df_tbu)[0]])[0]
                kia.kesimpulan_svm = label_bbtb.inverse_transform([pipeline_bbtb.predict(df_bbtb)[0]])[0]

            kia.bb = bb; kia.tb = tb_input; kia.posisi_ukur = posisi
            kia.z_bbu = z_bbu; kia.z_tbu = z_tbu; kia.z_bbtb = z_bbtb

        db.session.add(LogAktivitas(user_id=current_user.id, aksi=f"Mengedit data profil anak: {anak.nama_anak}"))
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Profil berhasil diperbarui!'})
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
            ortu = a.profil_orangtua
            data_list.append({
                'nik_balita': a.nik_balita, 'nama_anak': a.nama_anak, 
                'nama_ibu': ortu.nama_ibu if ortu else '', 'nama_ayah': ortu.nama_ayah if ortu else '',
                'status_terakhir': kia.kesimpulan_svm if kia else 'Belum Diukur'
            })
        return jsonify({'status': 'success', 'data': data_list})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api.route('/api/v1/stats')
@login_required
def get_stats():
    try:
        desa_stats = db.session.query(OrangTua.desa, func.count(Anak.id)).join(Anak, Anak.orangtua_id == OrangTua.id).group_by(OrangTua.desa).all()
        semua_anak = Anak.query.all()
        total_anak = len(semua_anak)
        gizi_buruk = stunting = gizi_baik = 0
        map_data = []
        gizi_kategori = {}
        
        for a in semua_anak:
            kia = PemantauanPerkembanganGiziAnak.query.filter_by(anak_id=a.id).order_by(PemantauanPerkembanganGiziAnak.tanggal_ukur.desc()).first()
            if kia:
                status = kia.kesimpulan_svm if kia.kesimpulan_svm else "Belum Diukur"
                gizi_kategori[status] = gizi_kategori.get(status, 0) + 1
                if 'pendek' in (kia.status_tbu or "").lower() or 'stunting' in (kia.status_tbu or "").lower(): stunting += 1
                if 'buruk' in status.lower() or 'kurang' in status.lower(): gizi_buruk += 1
                elif 'baik' in status.lower() or 'normal' in status.lower(): gizi_baik += 1
                
                ortu = a.profil_orangtua
                if ortu and ortu.latitude and ortu.longitude:
                    map_data.append({'lat': ortu.latitude, 'lng': ortu.longitude, 'nama': a.nama_anak, 'status': status})

        return jsonify({'status': 'success', 'desa': dict(desa_stats), 'gizi': gizi_kategori, 'map': map_data, 'summary': {'total': total_anak, 'buruk': gizi_buruk, 'stunting': stunting, 'baik': gizi_baik}})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api.route('/api/v1/cek-balita', methods=['GET'])
@login_required
def cek_balita():
    nik = request.args.get('nik')
    nama = request.args.get('nama')
    data_lama = Anak.query.filter_by(nik_balita=nik).first() if nik else Anak.query.filter(Anak.nama_anak.ilike(f"%{nama}%")).first()

    if data_lama:
        ortu = data_lama.profil_orangtua
        return jsonify({
            'exists': True,
            'balita': {
                'nik_balita': data_lama.nik_balita, 'nama_balita': data_lama.nama_anak,
                'nama_ibu': ortu.nama_ibu if ortu else '', 'nama_ayah': ortu.nama_ayah if ortu else '',
                'tanggal_lahir': data_lama.tanggal_lahir.strftime('%Y-%m-%d') if data_lama.tanggal_lahir else None,
                'jk': data_lama.jk, 'bb_lahir': data_lama.bb_lahir, 'tb_lahir': data_lama.tb_lahir,
                'desa': ortu.desa if ortu else '', 'lat': ortu.latitude if ortu else None, 'lng': ortu.longitude if ortu else None
            }
        })
    return jsonify({'exists': False})

@api.route('/api/v1/export-excel', methods=['GET'])
@login_required
def export_excel():
    try:
        semua_catatan = db.session.query(PemantauanPerkembanganGiziAnak, Anak).join(Anak).order_by(PemantauanPerkembanganGiziAnak.tanggal_ukur.desc()).all()
        data_excel = []
        ada_alert_toleransi = False 
        no = 1
        for catatan, anak in semua_catatan:
            tgl_ukur = catatan.tanggal_ukur.date()
            tgl_lahir = anak.tanggal_lahir
            selisih = relativedelta(tgl_ukur, tgl_lahir)
            usia_format = f"{selisih.years} tahun {selisih.months} bulan {selisih.days} hari"
            if 60 < ((selisih.years * 12) + selisih.months) <= 70: ada_alert_toleransi = True
            
            ortu = anak.profil_orangtua
            list_imun = [l.jenis_layanan.replace("Imunisasi: ", "") for l in catatan.layanan_tambahan if "Imunisasi:" in l.jenis_layanan]
            list_vit = [l.jenis_layanan.replace("Vitamin A: ", "") for l in catatan.layanan_tambahan if "Vitamin A:" in l.jenis_layanan]
            
            data_excel.append({
                'No': no, 'NIK Balita': anak.nik_balita, 'Nama Balita': anak.nama_anak,
                'Jenis Kelamin': 'Laki-Laki' if anak.jk == 'L' else 'Perempuan',
                'Nama Ibu': ortu.nama_ibu if ortu else '-', 'Desa': ortu.desa if ortu else '-',
                'Tgl Lahir': tgl_lahir.strftime('%Y-%m-%d'), 'Tgl Pengukuran': tgl_ukur.strftime('%Y-%m-%d'), 
                'Usia Detail': usia_format, 'Usia (Bulan)': catatan.usia_bulan,
                'BB (kg)': catatan.bb, 'TB (cm)': catatan.tb, 'N/T/O/B': catatan.ntob or '-',
                'Imunisasi': ", ".join(list_imun) if list_imun else '-', 'Vitamin A': ", ".join(list_vit) if list_vit else '-',
                'Z BB/U': round(catatan.z_bbu, 2) if catatan.z_bbu is not None else '-', 'St. BB/U': catatan.status_bbu or '-',
                'Z TB/U': round(catatan.z_tbu, 2) if catatan.z_tbu is not None else '-', 'St. TB/U': catatan.status_tbu or '-',
                'Z BB/TB': round(catatan.z_bbtb, 2) if catatan.z_bbtb is not None else '-', 'Klasifikasi SVM': catatan.kesimpulan_svm or '-'
            })
            no += 1

        df = pd.DataFrame(data_excel)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Data Pengukuran Balita')
        output.seek(0)
        
        response = make_response(send_file(output, as_attachment=True, download_name=f"Data_Export_SVM_{date.today()}.xlsx", mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))
        if ada_alert_toleransi:
            response.headers['X-Alert-Usia-Toleransi'] = 'true'
            response.headers['Access-Control-Expose-Headers'] = 'X-Alert-Usia-Toleransi'
        return response
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500