import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import ReactApexChart from 'react-apexcharts';
import Navbar from '../components/Navbar';

export default function BukuKIA() {
  const { id } = useParams(); // Mengambil ID dari URL
  const navigate = useNavigate();
  
  const [anak, setAnak] = useState<any>(null);
  const [riwayat, setRiwayat] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchKIA = async () => {
      try {
        const response = await fetch(`/api/v1/kia/${id}`, { credentials: 'include' });
        
        if (response.status === 401) {
          navigate('/login');
          return;
        }

        const data = await response.json();
        if (data.status === 'success') {
          setAnak(data.anak);
          setRiwayat(data.riwayat);
        }
      } catch (error) {
        console.error("Gagal memuat data KIA:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchKIA();
  }, [id, navigate]);

  // --- LOGIKA INSIGHT BERAT BADAN ---
  const renderInsight = () => {
    if (riwayat.length < 2) return null;
    
    const bbTerbaru = riwayat[riwayat.length - 1].bb;
    const bbSebelumnya = riwayat[riwayat.length - 2].bb;
    const selisih = Number((bbTerbaru - bbSebelumnya).toFixed(2));

    if (selisih > 0) {
      return (
        <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 p-4 rounded-xl mb-6 shadow-sm">
          📈 <strong>Bagus!</strong> Berat badan naik <strong>{selisih} kg</strong> dari bulan sebelumnya.
        </div>
      );
    } else if (selisih < 0) {
      return (
        <div className="bg-red-50 border border-red-200 text-red-800 p-4 rounded-xl mb-6 shadow-sm">
          ⚠️ <strong>Perhatian:</strong> Berat badan turun <strong>{Math.abs(selisih)} kg</strong>. Pantau asupan gizi anak!
        </div>
      );
    } else {
      return (
        <div className="bg-orange-50 border border-orange-200 text-orange-800 p-4 rounded-xl mb-6 shadow-sm">
          ➖ Berat badan <strong>tetap/stagnan</strong>. Pastikan kalori harian tercukupi.
        </div>
      );
    }
  };

  // --- KONFIGURASI GRAFIK APEXCHARTS ---
  const chartOptions: any = {
    chart: { type: 'line', height: 350, toolbar: { show: false }, fontFamily: 'Inter, sans-serif' },
    colors: ['#0d9488'],
    stroke: { curve: 'smooth', width: 4 },
    markers: { size: 6, colors: ['#fff'], strokeColors: '#0d9488', strokeWidth: 3 },
    xaxis: { 
      categories: riwayat.map(r => `Usia ${r.usia_bulan} Bln`),
      title: { text: 'Perkembangan Usia' }
    },
    yaxis: { title: { text: 'Berat Badan (kg)' } },
    dataLabels: { enabled: true, offsetY: -10, style: { fontSize: '12px', colors: ['#0f766e'] }, background: { enabled: false } },
    tooltip: { theme: 'light' }
  };

  const chartSeries = [{
    name: 'Berat Badan',
    data: riwayat.map(r => r.bb)
  }];

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-800 animate-page">
      <Navbar />

      <main className="max-w-7xl mx-auto w-full p-6 lg:p-8 flex-1">
        {/* Navigasi Kembali */}
        <Link to="/data-anak" className="inline-flex items-center text-teal-600 hover:text-teal-800 font-semibold mb-6 transition">
          <span className="mr-2">←</span> Kembali ke Data Anak
        </Link>

        {isLoading ? (
          <div className="flex justify-center items-center h-64">
            <div className="w-12 h-12 border-4 border-teal-200 border-t-teal-600 rounded-full animate-spin"></div>
          </div>
        ) : !anak ? (
          <div className="text-center py-20 bg-white rounded-3xl shadow-md">Data anak tidak ditemukan.</div>
        ) : (
          <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
            
            {/* KOLOM KIRI: Profil & Insight */}
            <div className="xl:col-span-1 space-y-6">
              <div className="bg-white rounded-3xl p-8 shadow-xl border border-slate-100 relative overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-teal-500 to-emerald-500"></div>
                <h3 className="text-xs font-black tracking-widest text-slate-400 uppercase mb-4">Profil Balita</h3>
                <h1 className="text-3xl font-black text-slate-800 leading-tight mb-2">{anak.nama_anak}</h1>
                <div className="space-y-4 mt-6">
                  <div>
                    <p className="text-xs text-slate-500 font-bold uppercase">Nama Ibu</p>
                    <p className="font-semibold text-slate-700">{anak.nama_ibu}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 font-bold uppercase">NIK Anak</p>
                    <p className="font-mono bg-slate-100 px-2 py-1 rounded inline-block text-sm">{anak.nik_balita}</p>
                  </div>
                  <div className="flex justify-between border-t pt-4 mt-2">
                    <div>
                      <p className="text-xs text-slate-500 font-bold uppercase">Lahir</p>
                      <p className="font-medium">{anak.tanggal_lahir}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-slate-500 font-bold uppercase">Jenis Kelamin</p>
                      <p className="font-medium">{anak.jk === 'L' ? 'Laki-Laki 👦' : 'Perempuan 👧'}</p>
                    </div>
                  </div>
                </div>
              </div>

              {renderInsight()}
            </div>

            {/* KOLOM KANAN: Grafik & Tabel Riwayat */}
            <div className="xl:col-span-2 space-y-8">
              {/* Grafik Pertumbuhan */}
              <div className="bg-white rounded-3xl p-8 shadow-xl border border-slate-100">
                <h3 className="text-lg font-bold text-slate-800 mb-6">Grafik Pertumbuhan Berat Badan</h3>
                {riwayat.length > 0 ? (
                  <div className="h-80">
                    <ReactApexChart options={chartOptions} series={chartSeries} type="line" height={320} />
                  </div>
                ) : (
                  <div className="h-40 flex items-center justify-center text-slate-400 bg-slate-50 rounded-xl border-dashed border-2">
                    Belum ada riwayat pengukuran
                  </div>
                )}
              </div>

              {/* Tabel Riwayat */}
              <div className="bg-white rounded-3xl p-8 shadow-xl border border-slate-100">
                <h3 className="text-lg font-bold text-slate-800 mb-6">Riwayat Pengukuran</h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full text-left text-sm">
                    <thead className="bg-slate-100 text-slate-600">
                      <tr>
                        <th className="py-3 px-4 font-bold rounded-l-xl">Tanggal</th>
                        <th className="py-3 px-4 font-bold">Usia</th>
                        <th className="py-3 px-4 font-bold">Berat (kg)</th>
                        <th className="py-3 px-4 font-bold">Tinggi (cm)</th>
                        <th className="py-3 px-4 font-bold">Z-Score BB/U</th>
                        <th className="py-3 px-4 font-bold">Z-Score TB/U</th>
                        <th className="py-3 px-4 font-bold">Z-Score BB/TB</th>
                        <th className="py-3 px-4 font-bold rounded-r-xl">Status Gizi Klasifikasi</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-50">
                      {riwayat.length === 0 ? (
                        <tr><td colSpan={5} className="py-8 text-center text-slate-400">Belum ada data</td></tr>
                      ) : (
                        riwayat.map((r, idx) => (
                          <tr key={r.id || idx} className="hover:bg-slate-50">
                            <td className="py-4 px-4 font-medium text-slate-700">{r.tanggal_ukur}</td>
                            <td className="py-4 px-4">{r.usia_bulan} bln</td>
                            <td className="py-4 px-4 font-bold text-teal-700">{r.bb}</td>
                            <td className="py-4 px-4 font-bold text-teal-700">{r.tb}</td>
                            <td className="py-4 px-4">
                                <span className="block text-xs font-mono text-slate-400">Z: {r.z_bbu !== null ? r.z_bbu : '-'}</span>
                                <span className="font-medium text-slate-700">{r.status_bbu || '-'}</span>
                            </td>
                            <td className="py-4 px-4">
                                <span className="block text-xs font-mono text-slate-400">Z: {r.z_tbu !== null ? r.z_tbu : '-'}</span>
                                <span className="font-medium text-slate-700">{r.status_tbu || '-'}</span>
                            </td>
                            <td className="py-4 px-4">{r.z_bbtb !== null ? r.z_bbtb.toFixed(2) : '-'}</td>
                            <td className="py-4 px-4">
                              <span className={`inline-block px-3 py-1 rounded-full text-xs font-bold border ${r.kesimpulan_svm.toLowerCase().includes('buruk') || r.kesimpulan_svm.toLowerCase().includes('pendek')? 'bg-red-50 border-red-200 text-red-700' : 'bg-emerald-50 border-emerald-200 text-emerald-700'
                              }`}>
                                {r.kesimpulan_svm}
                              </span>
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

          </div>
        )}
      </main>
    </div>
  );
}