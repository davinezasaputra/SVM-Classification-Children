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

class OrangTua(db.Model):
    __tablename__ = 'orangtua'
    id = db.Column(db.Integer, primary_key=True)
    nama_ibu = db.Column(db.String(100), nullable=True)
    nama_ayah = db.Column(db.String(100), nullable=True)
    desa = db.Column(db.String(100), default="Teritip")
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    tanggal_daftar = db.Column(db.DateTime, default=datetime.now)
    
    # 1 Keluarga bisa punya banyak anak
    anak = db.relationship('Anak', backref='profil_orangtua', cascade='all, delete-orphan')

class Anak(db.Model):
    __tablename__ = 'anak'
    id = db.Column(db.Integer, primary_key=True)
    orangtua_id = db.Column(db.Integer, db.ForeignKey('orangtua.id'), nullable=False) # Relasi ke Orang Tua
    nik_balita = db.Column(db.String(16), unique=True, nullable=False)
    nama_anak = db.Column(db.String(100), nullable=False)
    jk = db.Column(db.String(10), nullable=False)
    tanggal_lahir = db.Column(db.Date, nullable=False)
    bb_lahir = db.Column(db.Float, nullable=True)
    tb_lahir = db.Column(db.Float, nullable=True)
    tanggal_daftar = db.Column(db.DateTime, default=datetime.now)
    
    catatan_kia = db.relationship('PemantauanPerkembanganGiziAnak', backref='profil_anak', cascade='all, delete-orphan')

class PemantauanPerkembanganGiziAnak(db.Model):
    __tablename__ = 'pemantauan_gizi'
    id = db.Column(db.Integer, primary_key=True)
    anak_id = db.Column(db.Integer, db.ForeignKey('anak.id'), nullable=False)
    kader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Mencatat siapa petugasnya
    
    tanggal_ukur = db.Column(db.DateTime, default=datetime.now)
    usia_bulan = db.Column(db.Float)
    bb = db.Column(db.Float)
    tb = db.Column(db.Float)
    posisi_ukur = db.Column(db.String(20))
    ntob = db.Column(db.String(5))
    
    z_bbu = db.Column(db.Float)
    status_bbu = db.Column(db.String(50)) 
    z_tbu = db.Column(db.Float)
    status_tbu = db.Column(db.String(50)) 
    z_bbtb = db.Column(db.Float)
    kesimpulan_svm = db.Column(db.String(50))

    layanan_tambahan = db.relationship('LayananMedis', backref='pemantauan', cascade='all, delete-orphan')

class LayananMedis(db.Model):
    __tablename__ = 'layanan_medis'
    id = db.Column(db.Integer, primary_key=True)
    pemantauan_id = db.Column(db.Integer, db.ForeignKey('pemantauan_gizi.id'), nullable=False)
    jenis_layanan = db.Column(db.String(100), nullable=False)
    keterangan = db.Column(db.String(255), nullable=True)