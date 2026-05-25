import { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import Navbar from '../components/Navbar';

export default function InputData() {
  const [nikBalita, setNikBalita] = useState('');
  const [namaBalita, setNamaBalita] = useState('');
  const [tglLahir, setTglLahir] = useState('');
  const [jk, setJk] = useState('L');
  const [namaIbu, setNamaIbu] = useState('');
  const [namaAyah, setNamaAyah] = useState('');
  const [desa, setDesa] = useState('');
  const [latitude, setLatitude] = useState('');
  const [longitude, setLongitude] = useState('');
  const [bbLahir, setBbLahir] = useState('');
  const [tbLahir, setTbLahir] = useState('');
  const [beratBadan, setBeratBadan] = useState('');
  const [tinggiBadan, setTinggiBadan] = useState('');
  const [posisi, setPosisi] = useState('berdiri');
  const [ntob, setNtob] = useState('B');
  const [imunisasi, setImunisasi] = useState('Tidak');
  const [vitA, setVitA] = useState('Tidak');
  const [isDataBaru, setIsDataBaru] = useState(false);
  const [infoUmur, setInfoUmur] = useState('');
  const [kunciPosisi, setKunciPosisi] = useState(false);
  const [loading, setLoading] = useState(false);
  const [hasilSVM, setHasilSVM] = useState<any>(null);
  const [antrianOffline, setAntrianOffline] = useState<any[]>([]);
  const cekDataDatabase = async (tipePencarian: 'nik' | 'nama', nilai: string) => {
    if (!nilai) return;
    
    try {
      const response = await fetch(`/api/v1/cek-balita?${tipePencarian}=${encodeURIComponent(nilai)}`, { credentials: 'include' });
      const data = await response.json();
      
      if (data.exists) {
        setIsDataBaru(false);
        if (tipePencarian === 'nama') setNikBalita(data.balita.nik_balita || '');
        if (tipePencarian === 'nik') setNamaBalita(data.balita.nama_balita || '');
        
        setNamaIbu(data.balita.nama_ibu || '');
        setNamaAyah(data.balita.nama_ayah || '');
        setBbLahir(data.balita.bb_lahir || '');
        setTbLahir(data.balita.tb_lahir || '');
        setDesa(data.balita.desa || '');
        setLatitude(data.balita.lat || '');
        setLongitude(data.balita.lng || '');
        
        if (data.balita.tanggal_lahir) {
           handleTanggalLahir(data.balita.tanggal_lahir);
        }
        if (data.balita.jk) setJk(data.balita.jk);
        
      } else {
        if (tipePencarian === 'nik' && nilai.length >= 16) {
          setIsDataBaru(true);
          setNamaIbu('');
          setNamaAyah('');
          setBbLahir('');
          setTbLahir('');
        }
      }
    } catch (err) {
      console.error("Gagal cek data:", err);
    }
  };
  const handleCekNIK = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setNikBalita(val);
    if (val.length >= 16) {
      cekDataDatabase('nik', val);
    } else {
      setIsDataBaru(false);
    }
  };

  const handleCekNamaBlur = () => {
    if (namaBalita.length > 2 && nikBalita.length < 16) {
      cekDataDatabase('nama', namaBalita);
    }
  };


  const handleTanggalLahir = (val: string) => {
    setTglLahir(val);
    if (!val) {
      setInfoUmur('');
      setKunciPosisi(false);
      return;
    }
    const tgl = new Date(val);
    const sekarang = new Date();
    const diffTime = sekarang.getTime() - tgl.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    const umurDesimal = diffDays / 30.4375;
    const umurBulanBulat = Math.floor(umurDesimal);

    setInfoUmur(`Terhitung: ${umurBulanBulat} Bulan (${diffDays} Hari)`);

    if (umurDesimal < 24) {
      setKunciPosisi(true);
      setPosisi('telentang');
    } else {
      setKunciPosisi(false);
      setPosisi('berdiri');
    }
  };
  const submitKlasifikasi = async () => {
    if (!nikBalita || !namaBalita || !tglLahir || !beratBadan || !tinggiBadan) {
      toast.error("Mohon lengkapi data NIK, Nama, Tanggal Lahir, serta Pengukuran BB & TB!");
      return;
    }

    const payload = {
      nik_balita: nikBalita,
      nama_anak: namaBalita,
      tanggal_lahir: tglLahir,
      jk: jk,
      nama_ibu: namaIbu,
      nama_ayah: namaAyah,
      desa: desa,
      latitude: latitude,
      longitude: longitude,
      bb_lahir: bbLahir,
      tb_lahir: tbLahir,
      berat_badan: beratBadan,
      tinggi_badan: tinggiBadan,
      posisi_pengukuran: posisi,
      ntob: ntob,
      imunisasi: imunisasi,
      vit_a: vitA,
      timestamp_lokal: new Date().toISOString()
    };

    if (!navigator.onLine) {
      const antrianBaru = [...antrianOffline, payload];
      setAntrianOffline(antrianBaru);
      localStorage.setItem('antrianKIA', JSON.stringify(antrianBaru));
      toast.error("Sinyal terputus! Data disimpan secara OFFLINE.");
      resetPengukuran();
      return;
    }

    setLoading(true);
    setHasilSVM(null);

    try {
      const response = await fetch('/api/v1/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(payload)
      });
      const result = await response.json();
      
      if (response.ok && result.status === 'success') {
        setHasilSVM(result);
        resetPengukuran();
        if (result.is_outlier) {
          toast.error("Data terdeteksi sebagai OUTLIER. Hasil SVM mungkin tidak akurat.");
        } else {
          toast.success("Klasifikasi berhasil! Lihat hasil SVM di sebelah kanan.");
        }
      } else {
        toast.error(`Pesan Server: ${result.message}`);
      }
    } catch (error) {
      toast.error("Terjadi kesalahan koneksi ke server AI.");
    } finally {
      setLoading(false);
    }
  };

  const resetPengukuran = () => {
    setBeratBadan('');
    setTinggiBadan('');
    setNtob('B');
    setImunisasi('Tidak');
    setVitA('Tidak');
  };

  useEffect(() => {
    const saved = JSON.parse(localStorage.getItem('antrianKIA') || '[]');
    setAntrianOffline(saved);
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-800 animate-page">
      <Navbar />

      <main className="max-w-7xl mx-auto w-full p-6 lg:p-8 flex-1">
        
        {antrianOffline.length > 0 && (
          <div className="bg-orange-100 border border-orange-200 rounded-3xl shadow-md p-6 mb-8 flex justify-between items-center animate-pulse">
            <div>
              <h2 className="text-xl font-black text-orange-700">Terdapat Data Offline</h2>
              <p className="text-orange-600 mt-1">Ada <span className="font-black">{antrianOffline.length}</span> data yang belum sinkron.</p>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          
          <div className="xl:col-span-2 bg-white rounded-[30px] shadow-xl p-8 border border-white">
            <div className="flex items-center justify-between mb-8 border-b pb-4">
              <div>
                <h2 className="text-3xl font-black text-slate-800">Form Data Anak</h2>
                <p className="text-slate-500 mt-2">Pencatatan KIA Posyandu & Klasifikasi Gizi SVM.</p>
              </div>
              <div className="hidden md:flex w-16 h-16 rounded-2xl bg-gradient-to-br from-teal-500 to-emerald-500 text-white items-center justify-center text-3xl shadow-xl"></div>
            </div>

            <div className="space-y-8">
              
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 bg-slate-50 p-6 rounded-2xl border border-slate-100">
                <h3 className="md:col-span-2 text-lg font-bold text-teal-800 flex items-center gap-2">
                  <span className="bg-teal-200 text-teal-800 w-6 h-6 rounded-full flex items-center justify-center text-xs">1</span> 
                  Identitas Balita
                </h3>
                <div className="md:col-span-2">
                  <label className="text-sm font-bold text-slate-600 block mb-2">Nama Balita</label>
                  <input 
                    type="text" 
                    value={namaBalita} 
                    onChange={(e) => setNamaBalita(e.target.value)} 
                    onBlur={handleCekNamaBlur} 
                    placeholder="Ketik Nama Balita lalu klik di luar kotak..." 
                    className="w-full rounded-xl border p-3 outline-none focus:border-teal-500 bg-white" 
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="text-sm font-bold text-slate-600 block mb-2">NIK Balita (16 Digit)</label>
                  <input 
                    type="text" 
                    value={nikBalita} 
                    onChange={handleCekNIK} 
                    placeholder="Otomatis terisi jika nama ada, atau ketik 16 digit..." 
                    className="w-full rounded-xl border p-4 outline-none focus:border-teal-500 shadow-sm bg-white" 
                  />
                </div>
                <div>
                  <label className="text-sm font-bold text-slate-600 block mb-2">Jenis Kelamin</label>
                  <select value={jk} onChange={(e) => setJk(e.target.value)} className="w-full rounded-xl border p-3 outline-none focus:border-teal-500 bg-white">
                    <option value="L">Laki-Laki</option>
                    <option value="P">Perempuan</option>
                  </select>
                </div>
                <div>
                  <label className="text-sm font-bold text-slate-600 block mb-2">Tanggal Lahir</label>
                  <input type="date" value={tglLahir} onChange={(e) => handleTanggalLahir(e.target.value)} className="w-full rounded-xl border p-3 outline-none focus:border-teal-500 bg-white" />
                  {infoUmur && <p className="mt-2 text-xs font-semibold text-teal-700">{infoUmur}</p>}
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 bg-slate-50 p-6 rounded-2xl border border-slate-100">
                <h3 className="md:col-span-2 text-lg font-bold text-teal-800 flex items-center gap-2">
                  <span className="bg-teal-200 text-teal-800 w-6 h-6 rounded-full flex items-center justify-center text-xs">2</span> 
                  Riwayat Orang Tua & Kelahiran
                </h3>
                {isDataBaru && (
                  <div className="md:col-span-2 bg-blue-50 border border-blue-200 rounded-xl p-4 mb-2">
                    <p className="text-blue-700 font-semibold text-sm">Data Baru Terdeteksi. Silakan lengkapi domisili.</p>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-3">
                      <input type="text" placeholder="Nama Desa" value={desa} onChange={(e) => setDesa(e.target.value)} className="w-full rounded-lg border p-2 outline-none focus:border-teal-500 bg-white text-sm" />
                      <input type="text" placeholder="Latitude" value={latitude} onChange={(e) => setLatitude(e.target.value)} className="w-full rounded-lg border p-2 outline-none focus:border-teal-500 bg-white text-sm" />
                      <input type="text" placeholder="Longitude" value={longitude} onChange={(e) => setLongitude(e.target.value)} className="w-full rounded-lg border p-2 outline-none focus:border-teal-500 bg-white text-sm" />
                    </div>
                  </div>
                )}

                <div>
                  <label className="text-sm font-bold text-slate-600 block mb-2">Nama Ibu</label>
                  <input type="text" value={namaIbu} onChange={(e) => setNamaIbu(e.target.value)} placeholder="Nama Ibu" className="w-full rounded-xl border p-3 outline-none focus:border-teal-500 bg-white" />
                </div>
                <div>
                  <label className="text-sm font-bold text-slate-600 block mb-2">Nama Ayah</label>
                  <input type="text" value={namaAyah} onChange={(e) => setNamaAyah(e.target.value)} placeholder="Nama Ayah" className="w-full rounded-xl border p-3 outline-none focus:border-teal-500 bg-white" />
                </div>
                <div>
                  <label className="text-sm font-bold text-slate-600 block mb-2">Berat Badan Lahir (kg)</label>
                  <input type="number" step="0.01" value={bbLahir} onChange={(e) => setBbLahir(e.target.value)} placeholder="Misal: 3.2" className="w-full rounded-xl border p-3 outline-none focus:border-teal-500 bg-white" />
                </div>
                <div>
                  <label className="text-sm font-bold text-slate-600 block mb-2">Tinggi Badan Lahir (cm)</label>
                  <input type="number" step="0.01" value={tbLahir} onChange={(e) => setTbLahir(e.target.value)} placeholder="Misal: 50" className="w-full rounded-xl border p-3 outline-none focus:border-teal-500 bg-white" />
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 bg-emerald-50 p-6 rounded-2xl border border-emerald-100">
                <h3 className="md:col-span-3 text-lg font-bold text-emerald-800 flex items-center gap-2">
                  <span className="bg-emerald-200 text-emerald-900 w-6 h-6 rounded-full flex items-center justify-center text-xs">3</span> 
                  Pengukuran Posyandu Saat Ini
                </h3>
                
                <div>
                  <label className="text-sm font-bold text-slate-700 block mb-2">Berat (kg)</label>
                  <input type="number" step="0.01" value={beratBadan} onChange={(e) => setBeratBadan(e.target.value)} placeholder="12.5" className="w-full rounded-xl border p-3 outline-none focus:border-emerald-500 bg-white border-emerald-300" />
                </div>
                <div>
                  <label className="text-sm font-bold text-slate-700 block mb-2">Tinggi (cm)</label>
                  <input type="number" step="0.01" value={tinggiBadan} onChange={(e) => setTinggiBadan(e.target.value)} placeholder="90.5" className="w-full rounded-xl border p-3 outline-none focus:border-emerald-500 bg-white border-emerald-300" />
                </div>
                <div>
                  <label className="text-sm font-bold text-slate-700 block mb-2">Tren N/T/O/B</label>
                  <select value={ntob} onChange={(e) => setNtob(e.target.value)} className="w-full rounded-xl border p-3 outline-none focus:border-emerald-500 bg-white font-bold text-slate-700 border-emerald-300">
                    <option value="B">B (Baru)</option>
                    <option value="N">N (Naik)</option>
                    <option value="T">T (Turun)</option>
                    <option value="O">O (Tetap)</option>
                  </select>
                </div>

                <div className="md:col-span-3">
                  <label className="text-sm font-bold text-slate-700 block mb-2">Posisi Pengukuran</label>
                  <div className="flex gap-4">
                    <label className={`flex items-center gap-3 bg-white px-5 py-3 rounded-xl border transition ${kunciPosisi ? 'opacity-40 cursor-not-allowed' : 'border-emerald-200 hover:border-emerald-500 cursor-pointer'}`}>
                      <input type="radio" value="berdiri" checked={posisi === 'berdiri'} onChange={() => setPosisi('berdiri')} disabled={kunciPosisi} /> Berdiri
                    </label>
                    <label className="flex items-center gap-3 bg-white hover:border-emerald-500 border-emerald-200 px-5 py-3 rounded-xl border cursor-pointer transition">
                      <input type="radio" value="telentang" checked={posisi === 'telentang'} onChange={() => setPosisi('telentang')} /> Telentang
                    </label>
                  </div>
                  {kunciPosisi && <p className="mt-2 text-xs font-semibold text-red-500">Balita {'< 24'} bulan wajib diukur telentang.</p>}
                </div>
                <div>
                  <label className="text-sm font-bold text-slate-700 block mb-2">Imunisasi</label>
                  <input 
                    type="text" 
                    value={imunisasi} 
                    onChange={(e) => setImunisasi(e.target.value)} 
                    placeholder="Contoh: Campak, DPT 1 (Isi 'Tidak' jika kosong)" 
                    className="w-full rounded-xl border p-3 outline-none focus:border-emerald-500 border-emerald-300 bg-white" 
                  />
                </div>
                <div>
                  <label className="text-sm font-bold text-slate-700 block mb-2">Vitamin A</label>
                  <input 
                    type="text" 
                    value={vitA} 
                    onChange={(e) => setVitA(e.target.value)} 
                    placeholder="Contoh: Kapsul Merah (Isi 'Tidak' jika kosong)" 
                    className="w-full rounded-xl border p-3 outline-none focus:border-emerald-500 border-emerald-300 bg-white" 
                  />
                </div>
              </div>

            </div>

            <button onClick={submitKlasifikasi} disabled={loading} className="mt-10 w-full bg-gradient-to-r from-teal-600 to-emerald-600 hover:scale-[1.01] transition-all duration-300 text-white font-black py-5 rounded-2xl shadow-xl text-lg disabled:opacity-50">
              {loading ? 'MEMPROSES...' : 'SIMPAN & KLASIFIKASI'}
            </button>
          </div>
          <div className="bg-white rounded-[30px] shadow-xl p-8 border border-white h-fit sticky top-28">
            <p className="text-xs font-black tracking-[0.2em] text-slate-400 uppercase">Hasil AI</p>
            <h2 className="text-2xl font-black text-slate-800 mt-1 mb-6">Kesimpulan Gizi</h2>

            {!hasilSVM && !loading && (
              <div className="flex flex-col items-center justify-center py-20 text-center">
                <div className="w-16 h-16 mb-4 rounded-full bg-slate-100 mx-auto"></div>
                <h3 className="font-bold text-slate-700 text-lg">Belum Ada Data</h3>
                <p className="text-slate-400 mt-2 text-sm">Hasil klasifikasi Z-Score akan muncul di sini.</p>
              </div>
            )}

            {loading && (
              <div className="flex flex-col items-center justify-center py-20">
                <div className="w-16 h-16 border-4 border-teal-200 border-t-teal-600 rounded-full animate-spin mb-5"></div>
                <p className="font-bold text-teal-700">Menganalisis SVM...</p>
              </div>
            )}

            {hasilSVM && (
              <div className="animate-page">
                <div className="bg-gradient-to-br from-teal-500 to-emerald-500 rounded-3xl p-6 text-white text-center shadow-md">
                  <p className="uppercase text-xs tracking-[0.2em] opacity-80">Status Gizi</p>
                  <h1 className="text-3xl font-black mt-2">{hasilSVM.kesimpulan_svm}</h1>
                </div>

                <div className="mt-6 space-y-3">
                  <div className="bg-slate-50 border border-slate-200 rounded-2xl p-4">
                    <div className="flex justify-between items-center mb-1">
                      <span className="font-bold text-slate-700 text-sm">BB/U (Berat/Umur)</span>
                      <span className="text-xs font-black bg-white border px-2 py-1 rounded-md">Z: {hasilSVM.hasil_indikator.bbu.z}</span>
                    </div>
                    <p className="text-xs text-slate-500">{hasilSVM.hasil_indikator.bbu.status}</p>
                  </div>

                  <div className="bg-slate-50 border border-slate-200 rounded-2xl p-4">
                    <div className="flex justify-between items-center mb-1">
                      <span className="font-bold text-slate-700 text-sm">TB/U (Tinggi/Umur)</span>
                      <span className="text-xs font-black bg-white border px-2 py-1 rounded-md">Z: {hasilSVM.hasil_indikator.tbu.z}</span>
                    </div>
                    <p className="text-xs text-slate-500">{hasilSVM.hasil_indikator.tbu.status}</p>
                  </div>
                  
                  <div className="bg-slate-50 border border-slate-200 rounded-2xl p-4">
                    <div className="flex justify-between items-center mb-1">
                      <span className="font-bold text-slate-700 text-sm">BB/TB (Berat/Tinggi)</span>
                      <span className="text-xs font-black bg-white border px-2 py-1 rounded-md">Z: {hasilSVM.hasil_indikator.bbtb?.z || '-'}</span>
                    </div>
                    <p className="text-xs text-slate-500">{hasilSVM.hasil_indikator.bbtb?.status || '-'}</p>
                  </div>
                </div>

                <div className="mt-6">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-xs font-bold text-slate-600">Tingkat Kepercayaan AI</span>
                    <span className="text-xs font-black text-teal-700">{hasilSVM.confidence}</span>
                  </div>
                  <div className="w-full h-2 bg-slate-200 rounded-full overflow-hidden">
                    <div className="h-2 rounded-full bg-gradient-to-r from-teal-500 to-emerald-500" style={{ width: hasilSVM.confidence }}></div>
                  </div>
                </div>
              </div>
            )}
          </div>

        </div>
      </main>
    </div>
  );
}