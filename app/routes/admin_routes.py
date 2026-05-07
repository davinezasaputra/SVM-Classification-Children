from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.models import db, User, LogAktivitas
from functools import wraps
from datetime import datetime

admin = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Akses ditolak! Halaman ini khusus Administrator.', 'error')
            return redirect(url_for('web.home'))
        return f(*args, **kwargs)
    return decorated_function

def catat_log(aksi):
    log = LogAktivitas(user_id=current_user.id, aksi=aksi)
    db.session.add(log)
    db.session.commit()

@admin.route('/logs')
@login_required
@admin_required
def sistem_log():
    logs = LogAktivitas.query.order_by(LogAktivitas.waktu.desc()).limit(100).all()
    return render_template('admin_logs.html', user=current_user, logs=logs)

@admin.route('/users')
@login_required
@admin_required
def manajemen_akun():
    users = User.query.all()
    return render_template('admin_Musers.html', user=current_user, users=users)

@admin.route('/users/add', methods=['POST'])
@login_required
@admin_required
def tambah_akun():
    nama = request.form.get('nama')
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role', 'kader')
    cek_user = User.query.filter_by(username=username).first()
    if cek_user:
        flash(f'Username "{username}" sudah digunakan!', 'error')
        return redirect(url_for('admin.manajemen_akun'))
    hashed_pw = generate_password_hash(password)
    user_baru = User(nama=nama, username=username, password=hashed_pw, role=role)
    db.session.add(user_baru)
    
    catat_log(f"Membuat akun baru: {username} (Role: {role})")
    db.session.commit()
    
    flash(f'Akun {nama} berhasil dibuat!', 'success')
    return redirect(url_for('admin.manajemen_akun'))

@admin.route('/users/reset/<int:id_user>', methods=['POST'])
@login_required
@admin_required
def reset_password(id_user):
    target_user = User.query.get_or_404(id_user)
    password_baru = "puskesmas123"
    target_user.password = generate_password_hash(password_baru)
    
    catat_log(f"Mereset password untuk akun: {target_user.username}")
    db.session.commit()
    
    flash(f'Password {target_user.nama} direset menjadi: {password_baru}', 'success')
    return redirect(url_for('admin.manajemen_akun'))