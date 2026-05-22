from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.models import db, User, LogAktivitas
from functools import wraps

admin = Blueprint('admin', __name__, url_prefix='/api/v1/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            return jsonify({'status': 'error', 'message': 'Akses ditolak! Khusus Administrator.'}), 403
        return f(*args, **kwargs)
    return decorated_function

def catat_log(aksi):
    log = LogAktivitas(user_id=current_user.id, aksi=aksi)
    db.session.add(log)
    db.session.commit()

@admin.route('/logs', methods=['GET'])
@login_required
@admin_required
def sistem_log():
    logs = LogAktivitas.query.order_by(LogAktivitas.waktu.desc()).limit(100).all()
    data_logs = [{
        'waktu': l.waktu.strftime('%d-%m-%Y %H:%M'),
        'pengguna': f"{l.user.nama} ({l.user.role})",
        'aksi': l.aksi
    } for l in logs]
    return jsonify({'status': 'success', 'data': data_logs}), 200

@admin.route('/users', methods=['GET'])
@login_required
@admin_required
def manajemen_akun():
    users = User.query.all()
    data_users = [{
        'id': u.id,
        'nama': u.nama,
        'username': u.username,
        'role': u.role
    } for u in users]
    return jsonify({'status': 'success', 'data': data_users}), 200

@admin.route('/users', methods=['POST'])
@login_required
@admin_required
def tambah_akun():
    data = request.get_json()
    nama = data.get('nama')
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'kader')

    if not nama or not username or not password:
        return jsonify({'status': 'error', 'message': 'Data tidak lengkap'}), 400

    cek_user = User.query.filter_by(username=username).first()
    if cek_user:
        return jsonify({'status': 'error', 'message': f'Username "{username}" sudah digunakan!'}), 409

    hashed_pw = generate_password_hash(password)
    user_baru = User(nama=nama, username=username, password=hashed_pw, role=role)
    db.session.add(user_baru)
    
    catat_log(f"Membuat akun baru: {username} (Role: {role})")
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': f'Akun {nama} berhasil dibuat!'}), 201

@admin.route('/users/reset/<int:id_user>', methods=['POST'])
@login_required
@admin_required
def reset_password(id_user):
    target_user = User.query.get_or_404(id_user)
    password_baru = "puskesmas123"
    target_user.password = generate_password_hash(password_baru)
    
    catat_log(f"Mereset password untuk akun: {target_user.username}")
    db.session.commit()
    
    return jsonify({
        'status': 'success', 
        'message': f'Password {target_user.nama} direset menjadi: {password_baru}'
    }), 200