from flask import Blueprint, Flask, render_template, request, jsonify, redirect, url_for, flash, send_from_directory, make_response
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, Anak, PemantauanPerkembanganGiziAnak


web = Blueprint('web', __name__)
@web.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('web.home'))
    if request.method == 'POST':
        u = User.query.filter_by(username=request.form['username']).first()
        if u and check_password_hash(u.password, request.form['password']):
            login_user(u)
            return redirect(url_for('web.home'))
        flash('Username atau Password Salah!')
    return render_template('login.html')

@web.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('web.login'))

@web.route('/')
@login_required
def home():
    return render_template('dashboard.html', user=current_user)

@web.route('/input')
@login_required
def input_data():
    return render_template('index.html', user=current_user)

@web.route('/data-anak')
@login_required
def data_anak():
    return render_template('data_anak.html', user=current_user)

@web.route('/kia/<int:id_anak>')
@login_required
def buku_kia(id_anak):
    anak = Anak.query.get_or_404(id_anak)
    riwayat = PemantauanPerkembanganGiziAnak.query.filter_by(anak_id=id_anak).order_by(PemantauanPerkembanganGiziAnak.tanggal_ukur.asc()).all()
    return render_template('kia.html', user=current_user, anak=anak, riwayat=riwayat)