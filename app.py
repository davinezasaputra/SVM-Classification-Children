from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import joblib
import numpy as np

app = Flask(__name__)

# ==========================================
# 1. KONFIGURASI DATABASE (MySQL LARAGON)
# ==========================================
# Format URI: mysql+pymysql://username:password@localhost/nama_database
# Username default Laragon adalah 'root' dan passwordnya kosong ''
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/db_puskesmas'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ==========================================
# 2. DESAIN TABEL DATABASE (Schema)
# ==========================================
class DataBalita(db.Model):
    # Nama tabel di MySQL akan otomatis menjadi 'data_balita'
    __tablename__ = 'data_balita'
    
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    usia_bulan = db.Column(db.Float, nullable=False)
    zs_bbu = db.Column(db.Float, nullable=False)
    zs_tbu = db.Column(db.Float, nullable=False)
    zs_bbtb = db.Column(db.Float, nullable=False)
    status_gizi = db.Column(db.String(50), nullable=False)
    tanggal_ukur = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'nama': self.nama,
            'usia_bulan': self.usia_bulan,
            'zscore_bbu': self.zs_bbu,
            'zscore_tbu': self.zs_tbu,
            'zscore_bbtb': self.zs_bbtb,
            'status_gizi': self.status_gizi,
            'tanggal_ukur': self.tanggal_ukur.strftime("%Y-%m-%d %H:%M:%S")
        }

# Otomatis membuat tabel 'data_balita' di MySQL jika belum ada
with app.app_context():
    db.create_all()

# ==========================================
# 3. LOAD MODEL AI SVM
# ==========================================
try:
    svm_model = joblib.load('svm_puskesmas.pkl')
    scaler = joblib.load('scaler_puskesmas.pkl')
    print("Model SVM & Scaler siap digunakan!")
except:
    print("Peringatan: File svm_puskesmas.pkl atau scaler_puskesmas.pkl tidak ditemukan!")
    svm_model = None
    scaler = None

# ==========================================
# 4. ROUTE WEB (Halaman HTML)
# ==========================================
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

# ==========================================
# 5. ROUTE API V1 (Standar Profesional)
# ==========================================

# Endpoint untuk menerima data dari Web/Android
@app.route('/api/v1/predict', methods=['POST'])
def api_predict_v1():
    if not svm_model or not scaler:
        return jsonify({'status': 'error', 'message': 'Model AI belum siap'}), 500

    try:
        data = request.get_json()
        
        nama = data.get('nama')
        usia = float(data.get('usia'))
        zs_bbu = float(data.get('zs_bbu'))
        zs_tbu = float(data.get('zs_tbu'))
        zs_bbtb = float(data.get('zs_bbtb'))

        # Prediksi SVM
        data_input = np.array([[usia, zs_bbu, zs_tbu, zs_bbtb]])
        data_scaled = scaler.transform(data_input)
        hasil = svm_model.predict(data_scaled)
        status_gizi = hasil[0]

        # Simpan ke MySQL Laragon
        balita_baru = DataBalita(
            nama=nama,
            usia_bulan=usia,
            zs_bbu=zs_bbu,
            zs_tbu=zs_tbu,
            zs_bbtb=zs_bbtb,
            status_gizi=status_gizi
        )
        db.session.add(balita_baru)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Data berhasil disimpan ke MySQL',
            'data': balita_baru.to_dict()
        }), 201

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

# Endpoint untuk melihat riwayat data (Laporan)
@app.route('/api/v1/history', methods=['GET'])
def api_history_v1():
    try:
        semua_data = DataBalita.query.order_by(DataBalita.tanggal_ukur.desc()).all()
        return jsonify({
            'status': 'success',
            'total_data': len(semua_data),
            'data': [balita.to_dict() for balita in semua_data]
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)