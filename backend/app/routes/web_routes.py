from flask import Blueprint, request, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from app.models import User, Anak, PemantauanPerkembanganGiziAnak

web = Blueprint('web', __name__)
@web.route('/api/v1/auth/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return jsonify({
            'status': 'success', 
            'message': 'Berhasil Login', 
            'user': {'nama': current_user.nama, 'role': current_user.role}
        }), 200

    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'status': 'error', 'message': 'Data tidak lengkap'}), 400

    u = User.query.filter_by(username=data['username']).first()
    if u and check_password_hash(u.password, data['password']):
        login_user(u)
        return jsonify({
            'status': 'success',
            'message': 'Login berhasil',
            'user': {'nama': u.nama, 'role': u.role}
        }), 200
        
    return jsonify({'status': 'error', 'message': 'Username atau Password Salah!'}), 401

@web.route('/api/v1/auth/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'status': 'success', 'message': 'Logout berhasil'}), 200

@web.route('/api/v1/auth/me', methods=['GET'])
@login_required
def get_current_user():
    return jsonify({
        'status': 'success',
        'user': {'nama': current_user.nama, 'role': current_user.role}
    }), 200

@web.route('/api/v1/kia/<int:id_anak>', methods=['GET'])
@login_required
def get_buku_kia(id_anak):
    anak = Anak.query.get_or_404(id_anak)
    riwayat = PemantauanPerkembanganGiziAnak.query.filter_by(anak_id=id_anak).order_by(PemantauanPerkembanganGiziAnak.tanggal_ukur.asc()).all()
    data_anak = {
        'id': anak.id,
        'nik_balita': anak.nik_balita,
        'nama_anak': anak.nama_anak,
        'nama_ibu': anak.nama_ibu,
        'jk': anak.jk,
        'tanggal_lahir': anak.tanggal_lahir.strftime('%Y-%m-%d'),
        'tanggal_daftar': anak.tanggal_daftar.strftime('%Y-%m-%d')
    }
    
    data_riwayat = [{
        'id': r.id,
        'tanggal_ukur': r.tanggal_ukur.strftime('%Y-%m-%d'),
        'usia_bulan': r.usia_bulan,
        'bb': r.bb,
        'tb': r.tb,
        'z_bbu': round(r.z_bbu, 2) if r.z_bbu else None,
        'status_bbu': r.status_bbu,
        'z_tbu': round(r.z_tbu, 2) if r.z_tbu else None,
        'status_tbu': r.status_tbu,
        'z_bbtb': round(r.z_bbtb, 2) if r.z_bbtb else None,
        'kesimpulan_svm': r.kesimpulan_svm
    } for r in riwayat]

    return jsonify({'status': 'success', 'anak': data_anak, 'riwayat': data_riwayat}), 200