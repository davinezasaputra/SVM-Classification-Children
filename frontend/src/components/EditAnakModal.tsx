import { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (id: number, dataBaru: any) => void;
  anakData: any;
}

export default function EditAnakModal({ isOpen, onClose, onConfirm, anakData }: Props) {
  const [formData, setFormData] = useState({
    nama_anak: '',
    nama_ibu: '',
    nama_ayah: '',
    desa: '',
    jk: 'L',
    tanggal_lahir: '',
    berat_badan: '',
    tinggi_badan: '',
    posisi_pengukuran: 'berdiri'
  });

  useEffect(() => {
    if (isOpen && anakData) {
      setFormData({
        nama_anak: anakData.nama_anak || '',
        nama_ibu: anakData.nama_ibu || '',
        nama_ayah: anakData.nama_ayah || '',
        desa: anakData.desa || '',
        jk: anakData.jk === 'Perempuan' || anakData.jk === 'P' ? 'P' : 'L',
        tanggal_lahir: anakData.tanggal_lahir || '',
        berat_badan: anakData.bb || '',
        tinggi_badan: anakData.tb || '',
        posisi_pengukuran: anakData.posisi_ukur || 'berdiri'
      });
    }
  }, [isOpen, anakData]);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.nama_anak || !formData.berat_badan || !formData.tinggi_badan) {
      toast.error("Nama Balita, Berat, dan Tinggi Badan wajib diisi!");
      return;
    }
    onConfirm(anakData.id, formData);
  };

  return (
    <div className="fixed inset-0 bg-slate-900/50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-white rounded-3xl p-8 w-full max-w-md shadow-2xl my-auto">
        <h3 className="text-xl font-bold text-slate-800 mb-1">Edit Profil & Pengukuran</h3>
        <p className="text-slate-500 mb-6 text-sm">NIK: <strong>{anakData?.nik_balita}</strong></p>
        
        <form onSubmit={handleSubmit} className="space-y-4 max-h-[70vh] overflow-y-auto pr-2">
          <div>
            <label className="text-xs font-bold text-slate-600 block mb-1">Nama Anak</label>
            <input type="text" value={formData.nama_anak} onChange={(e) => setFormData({...formData, nama_anak: e.target.value})} className="w-full rounded-xl border border-slate-200 p-3 outline-none focus:border-teal-500 text-sm" />
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-bold text-slate-600 block mb-1">Nama Ibu</label>
              <input type="text" value={formData.nama_ibu} onChange={(e) => setFormData({...formData, nama_ibu: e.target.value})} className="w-full rounded-xl border border-slate-200 p-3 outline-none focus:border-teal-500 text-sm" />
            </div>
            <div>
              <label className="text-xs font-bold text-slate-600 block mb-1">Nama Ayah</label>
              <input type="text" value={formData.nama_ayah} onChange={(e) => setFormData({...formData, nama_ayah: e.target.value})} className="w-full rounded-xl border border-slate-200 p-3 outline-none focus:border-teal-500 text-sm" />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-bold text-slate-600 block mb-1">Jenis Kelamin</label>
              <select value={formData.jk} onChange={(e) => setFormData({...formData, jk: e.target.value})} className="w-full rounded-xl border border-slate-200 p-3 outline-none focus:border-teal-500 text-sm bg-white">
                <option value="L">Laki-laki</option>
                <option value="P">Perempuan</option>
              </select>
            </div>
            <div>
              <label className="text-xs font-bold text-slate-600 block mb-1">Tanggal Lahir</label>
              <input type="date" value={formData.tanggal_lahir} onChange={(e) => setFormData({...formData, tanggal_lahir: e.target.value})} className="w-full rounded-xl border border-slate-200 p-3 outline-none focus:border-teal-500 text-sm" />
            </div>
          </div>

          <div>
            <label className="text-xs font-bold text-slate-600 block mb-1">Desa / Domisili</label>
            <input type="text" value={formData.desa} onChange={(e) => setFormData({...formData, desa: e.target.value})} className="w-full rounded-xl border border-slate-200 p-3 outline-none focus:border-teal-500 text-sm" />
          </div>

          <div className="bg-emerald-50 p-4 rounded-2xl border border-emerald-100 space-y-3">
            <h4 className="text-xs font-bold text-emerald-800 uppercase tracking-wider">Koreksi Parameter Pengukuran</h4>
            
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-[11px] font-bold text-slate-600 block mb-1">Berat Badan (kg)</label>
                <input type="number" step="0.01" value={formData.berat_badan} onChange={(e) => setFormData({...formData, berat_badan: e.target.value})} className="w-full rounded-lg border p-2 outline-none focus:border-emerald-500 text-sm bg-white" />
              </div>
              <div>
                <label className="text-[11px] font-bold text-slate-600 block mb-1">Tinggi Badan (cm)</label>
                <input type="number" step="0.01" value={formData.tinggi_badan} onChange={(e) => setFormData({...formData, tinggi_badan: e.target.value})} className="w-full rounded-lg border p-2 outline-none focus:border-emerald-500 text-sm bg-white" />
              </div>
            </div>

            <div>
              <label className="text-[11px] font-bold text-slate-600 block mb-1">Posisi Ukur</label>
              <select value={formData.posisi_pengukuran} onChange={(e) => setFormData({...formData, posisi_pengukuran: e.target.value})} className="w-full rounded-lg border p-2 outline-none focus:border-emerald-500 text-sm bg-white text-slate-700">
                <option value="berdiri">Berdiri</option>
                <option value="telentang">Telentang</option>
              </select>
            </div>
          </div>
          
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose} className="flex-1 py-3 rounded-xl font-bold text-slate-600 bg-slate-100 hover:bg-slate-200 transition text-sm">Batal</button>
            <button type="submit" className="flex-1 py-3 rounded-xl font-bold bg-teal-600 text-white hover:bg-teal-700 transition shadow-lg text-sm">Simpan</button>
          </div>
        </form>
      </div>
    </div>
  );
}