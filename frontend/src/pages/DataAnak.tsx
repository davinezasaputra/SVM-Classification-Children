import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import { Link, useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';

export default function DataAnak() {
  const [dataAnak, setDataAnak] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isExporting, setIsExporting] = useState(false);
  const navigate = useNavigate();

  const fetchData = async (query = '') => {
    setIsLoading(true);
    try {
      const endpoint = query ? `/api/v1/search?q=${query}` : '/api/v1/anak';
      const response = await fetch(endpoint, { credentials: 'include' });
      
      if (response.status === 401) {
        navigate('/login');
        return;
      }
      
      const result = await response.json();
      if (result.status === 'success') {
        setDataAnak(result.data);
      }
    } catch (error) {
      toast.error('Error fetching data:');
      console.error('Error fetching data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchData(searchQuery);
  };

  const handleHapus = async (id: number, nama: string) => {
    if (window.confirm(`Yakin ingin menghapus semua data dan Buku KIA milik anak bernama ${nama}? Data tidak bisa dikembalikan.`)) {
      try {
        const response = await fetch(`/api/v1/anak/${id}`, {
          method: 'DELETE',
          credentials: 'include'
        });
        const result = await response.json();
        if (result.status === 'success') {
          toast.success('Data berhasil dihapus.');
          fetchData(); 
        } else {
          toast.error('Gagal menghapus data.');
        }
      } catch (error) {
        toast.error('Terjadi kesalahan sistem saat menghapus data.');
      }
    }
  };

  const handleExportExcel = async () => {
    setIsExporting(true);
    try {
      const response = await fetch('/api/v1/export-excel', { credentials: 'include' });
      if (!response.ok) throw new Error('Gagal mengunduh');

      if (response.headers.get('X-Alert-Usia-Toleransi') === 'true') {
        toast.error("Peringatan: Terdapat balita dengan usia mendekati batas toleransi (60-70 bulan) di dalam data ini.");
      }

      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = `Data_Gizi_Balita_SVM_${new Date().toISOString().split('T')[0]}.xlsx`;
      document.body.appendChild(a);
      a.click();
      
      a.remove();
      window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      console.error(error);
      toast.error('Terjadi kesalahan saat mencoba mengunduh file Excel.');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-800 animate-page">
      <Navbar />

      <main className="max-w-7xl mx-auto w-full p-6 lg:p-8 flex-1">
        <div className="bg-white p-8 rounded-3xl shadow-xl border border-gray-100">
          
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 border-b border-slate-100 pb-6 gap-4">
            <div>
              <h2 className="text-3xl font-black text-teal-800">Manajemen Data Anak</h2>
              <p className="text-slate-500 mt-1">Daftar riwayat pengukuran dan klasifikasi gizi balita.</p>
            </div>
            <button 
              onClick={handleExportExcel}
              disabled={isExporting}
              className="bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-3 px-6 rounded-xl shadow-lg transition disabled:opacity-70 flex items-center gap-2"
            >
              {isExporting ? 'Memproses Ekspor...' : '📥 Unduh Rekap Excel'}
            </button>
          </div>

          <div className="mb-8">
            <form onSubmit={handleSearch} className="flex flex-col md:flex-row gap-3">
              <input 
                type="text" 
                placeholder="Cari NIK Balita atau Nama Anak..." 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex-1 rounded-xl border border-slate-200 bg-slate-50 p-4 outline-none focus:border-teal-500 focus:bg-white transition"
              />
              <button type="submit" className="bg-teal-600 hover:bg-teal-700 text-white font-bold py-4 px-8 rounded-xl shadow-md transition">
                Cari Data
              </button>
              {searchQuery && (
                <button type="button" onClick={() => { setSearchQuery(''); fetchData(''); }} className="bg-slate-200 hover:bg-slate-300 text-slate-700 font-bold py-4 px-6 rounded-xl transition">
                  Reset
                </button>
              )}
            </form>
          </div>

          <div className="overflow-x-auto rounded-2xl border border-slate-200">
            <table className="min-w-full bg-white text-left text-sm">
              <thead className="bg-slate-100 text-slate-600 uppercase font-black text-xs tracking-wider">
                <tr>
                  <th className="py-4 px-6 border-b">NIK Balita</th>
                  <th className="py-4 px-6 border-b">Nama Anak</th>
                  <th className="py-4 px-6 border-b">Jenis Kelamin</th>
                  <th className="py-4 px-6 border-b">Status Gizi (Terakhir)</th>
                  <th className="py-4 px-6 border-b text-center">Aksi Manajemen</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {isLoading ? (
                  <tr>
                    <td colSpan={5} className="py-12 text-center text-teal-600 font-bold animate-pulse">
                      Memuat data dari server...
                    </td>
                  </tr>
                ) : dataAnak.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="py-12 text-center text-slate-400 font-medium">
                      Belum ada data anak yang terdaftar.
                    </td>
                  </tr>
                ) : (
                  dataAnak.map((anak) => (
                    <tr key={anak.id || anak.nik_balita} className="hover:bg-slate-50 transition">
                      <td className="py-4 px-6 font-semibold text-slate-800">{anak.nik_balita}</td>
                      <td className="py-4 px-6">
                        <span className="font-bold text-slate-800 block">{anak.nama_anak}</span>
                        <span className="text-xs text-slate-400">Ibu: {anak.nama_ibu}</span>
                      </td>
                      <td className="py-4 px-6">{anak.jk || '-'}</td>
                      <td className="py-4 px-6">
                        <span className={`inline-block px-3 py-1 rounded-full text-xs font-bold border ${
                          anak.status_terakhir.toLowerCase().includes('buruk') || anak.status_terakhir.toLowerCase().includes('kurang') || anak.status_terakhir.toLowerCase().includes('pendek')
                          ? 'bg-red-50 border-red-200 text-red-700' 
                          : anak.status_terakhir.toLowerCase().includes('baik') || anak.status_terakhir.toLowerCase().includes('normal')
                          ? 'bg-emerald-50 border-emerald-200 text-emerald-700'
                          : 'bg-slate-100 border-slate-200 text-slate-700'
                        }`}>
                          {anak.status_terakhir}
                        </span>
                      </td>
                      <td className="py-4 px-6 text-center space-x-2">
                        {anak.id ? (
                          <>
                            <Link to={`/kia/${anak.id}`} className="inline-block bg-teal-100 hover:bg-teal-200 text-teal-800 text-xs font-bold py-2 px-4 rounded-lg transition">
                              Buku KIA
                            </Link>
                            <button onClick={() => handleHapus(anak.id, anak.nama_anak)} className="bg-red-100 hover:bg-red-200 text-red-700 text-xs font-bold py-2 px-4 rounded-lg transition">
                              Hapus
                            </button>
                          </>
                        ) : (
                          <span className="text-xs text-slate-400">Hasil Pencarian</span>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

        </div>
      </main>
    </div>
  );
}