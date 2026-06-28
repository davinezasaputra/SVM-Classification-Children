import os
import joblib

base_direct = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
base_direct = os.path.join(base_direct,'models')

pipeline_bbu, label_bbu = None, None
pipeline_tbu, label_tbu = None, None
pipeline_bbtb, label_bbtb = None, None

try:
    print ("Memuat Semua Model SVM")
    
    paket_bbu = joblib.load(os.path.join(base_direct, 'mesin_svm_bbu.pkl'))
    pipeline_bbu = paket_bbu['model_pipeline']
    label_bbu = paket_bbu['labels_asli']
    
    paket_tbu = joblib.load(os.path.join(base_direct, 'mesin_svm_tbu.pkl'))
    pipeline_tbu = paket_tbu['model_pipeline'] 
    label_tbu = paket_tbu['labels_asli']
    
    paket_bbtb = joblib.load(os.path.join(base_direct, 'mesin_svm_bbtb.pkl'))
    pipeline_bbtb = paket_bbtb['model_pipeline'] 
    label_bbtb = paket_bbtb['labels_asli']
    
    print ("Semua Model SVM Berhasil dimuat")
except Exception as e:
    print (f"Error memuat model SVM: {e}")