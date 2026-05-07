from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(255))
    nama = db.Column(db.String(100))
    role = db.Column(db.String(20), default='kader')

class LogAktivitas(db.Model):
    __tablename__ = 'log_aktivitas'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    aksi = db.Column(db.String(255))
    waktu = db.Column(db.DateTime, default=datetime.now)
    
    user = db.relationship('User', backref=db.backref('logs', lazy=True))

class Anak(db.Model):
    __tablename__ = 'anak'
    id = db.Column(db.Integer, primary_key=True)
    nik_ibu = db.Column(db.String(16), nullable=False)
    nama_ibu = db.Column(db.String(100), nullable=False)
    nama_anak = db.Column(db.String(100), nullable=False)
    jk = db.Column(db.String(10), nullable=False)
    tanggal_daftar = db.Column(db.DateTime, default=datetime.now)
    tanggal_lahir = db.Column(db.Date, nullable=False)
    desa = db.Column(db.String(100), default="Teritip")
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    catatan_kia = db.relationship('PemantauanPerkembanganGiziAnak', backref='profil_anak', cascade='all, delete-orphan')

class PemantauanPerkembanganGiziAnak(db.Model):
    __tablename__ = 'pemantauan_gizi'
    id = db.Column(db.Integer, primary_key=True)
    anak_id = db.Column(db.Integer, db.ForeignKey('anak.id'), nullable=False)
    tanggal_ukur = db.Column(db.DateTime, default=datetime.now)
    usia_bulan = db.Column(db.Float)
    bb = db.Column(db.Float)
    tb = db.Column(db.Float)
    posisi_ukur = db.Column(db.String(20))
    z_bbu = db.Column(db.Float)
    status_bbu = db.Column(db.String(50)) 
    z_tbu = db.Column(db.Float)
    status_tbu = db.Column(db.String(50)) 
    z_bbtb = db.Column(db.Float)
    kesimpulan_svm = db.Column(db.String(50)) 