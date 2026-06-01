import { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from 'chart.js';
import { Doughnut, Bar } from 'react-chartjs-2';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import Swal from 'sweetalert2';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

export default function Dashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState({ total: '-', buruk: '-', stunting: '-', baik: '-' });
  const [giziData, setGiziData] = useState<any>(null);
  const [desaData, setDesaData] = useState<any>(null);
  const [mapData, setMapData] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [userRole, setUserRole] = useState('petugas');
  const [namaPetugas, setNamaPetugas] = useState('');

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      const parsed = JSON.parse(userData);
      setUserRole(parsed.role?.toLowerCase() || 'petugas');
      setNamaPetugas(parsed.nama || parsed.username || '');
    }

    const fetchStats = async () => {
      try {
        const response = await fetch('/api/v1/stats', {
          method: 'GET',
          credentials: 'include', 
        });

        if (response.status === 401) {
          navigate('/login');
          return;
        }

        const data = await response.json();
        
        if (data.status === 'success') {
          setStats(data.summary);
          
          setGiziData({
            labels: Object.keys(data.gizi),
            datasets: [{ data: Object.values(data.gizi), backgroundColor: ['#0d9488', '#f59e0b', '#ef4444', '#3b82f6'] }]
          });

          setDesaData({
            labels: Object.keys(data.desa),
            datasets: [{ label: 'Jumlah Anak', data: Object.values(data.desa), backgroundColor: '#0d9488', borderRadius: 4 }]
          });

          setMapData(data.map || []);
        }
      } catch (error) {
        console.error("Gagal mengambil statistik:", error);
        toast.error("Gagal mengambil statistik");
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
  }, [navigate]);

  const handleLogout = async (e: React.MouseEvent) => {
    e.preventDefault();
    
    Swal.fire({
      title: 'Konfirmasi Logout',
      text: "Apakah Anda yakin ingin keluar dari sistem?",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#0f766e',
      cancelButtonColor: '#ef4444',
      confirmButtonText: 'Ya, Keluar',
      cancelButtonText: 'Batal',
      customClass: {
        popup: 'rounded-2xl',
        confirmButton: 'rounded-xl px-6 py-2',
        cancelButton: 'rounded-xl px-6 py-2'
      }
    }).then(async (result: any) => {
      if (result.isConfirmed) {
        try {
          await fetch('/api/v1/auth/logout', { method: 'POST', credentials: 'include' });
          localStorage.removeItem('user');
          navigate('/login');
        } catch (error) {
          console.error("Gagal logout:", error);
          toast.error("Terjadi kesalahan saat logout");
        }
      }
    });
  };

  const toggleSidebar = () => setIsSidebarOpen(!isSidebarOpen);
  const closeSidebar = () => setIsSidebarOpen(false);

  return (
    <div className="bg-slate-50 overflow-hidden font-sans text-slate-800 animate-page">
      <div className="flex h-screen overflow-hidden w-full relative">
        <aside className={`w-64 bg-teal-900 text-white fixed inset-y-0 left-0 z-50 flex flex-col transform ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0 transition-transform duration-300 ease-in-out`}>
          <button onClick={closeSidebar} className="absolute top-4 right-4 md:hidden text-teal-300 hover:text-white p-2">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
          
          <div className="p-6">
            <img src="/Kabupaten-Bangka-Barat.png" alt="Logo Puskesmas" className="w-12 h-12 mb-4" />
            <h1 className="text-xl font-black tracking-tighter uppercase">Puskesmas Simpang Teritip</h1>
            <p className="text-xs text-teal-300">Sistem Informasi Gizi SVM</p>
          </div>
  
          <nav className="flex-1 px-4 space-y-2 mt-4 overflow-y-auto">
            <Link to="/dashboard" onClick={closeSidebar} className="block py-3 px-4 bg-teal-800 rounded-lg transition font-medium border-l-4 border-teal-400">Dashboard Utama</Link>
            <Link to="/data-anak" onClick={closeSidebar} className="block py-3 px-4 rounded-lg hover:bg-teal-800 transition font-medium">Pencarian / Data Anak</Link>
            <Link to="/input" onClick={closeSidebar} className="block py-3 px-4 rounded-lg hover:bg-teal-800 transition font-medium">Input Data Baru</Link>
            {userRole === 'admin' && (
              <>
                <Link to="/admin" onClick={closeSidebar} className="block py-3 px-4 rounded-lg hover:bg-teal-800 transition font-medium">Manajemen Akun</Link>
                <Link to="/admin" onClick={closeSidebar} className="block py-3 px-4 rounded-lg hover:bg-teal-800 transition font-medium">Sistem Log</Link>
              </>
            )}
          </nav>
  
          <div className="p-4 border-t border-teal-800">
            <button onClick={handleLogout} className="text-sm text-teal-400 hover:text-white w-full text-left font-semibold">Keluar Sistem</button>
          </div>
        </aside>
        <div className={`fixed inset-0 bg-black/40 z-40 md:hidden ${isSidebarOpen ? 'block' : 'hidden'}`} onClick={closeSidebar}></div>
        <main className="relative z-10 flex-1 flex flex-col h-screen overflow-y-auto transition-all duration-300 md:ml-64">
          <header className="bg-white shadow-sm p-4 flex justify-between items-center w-full sticky top-0 z-40">
            <div className="flex items-center gap-3">
              <button onClick={toggleSidebar} className="md:hidden p-2 text-slate-600 hover:bg-slate-100 rounded-lg transition">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
              </button>
              <h2 className="text-base sm:text-lg font-bold text-slate-800">Ringkasan Statistik Gizi</h2>
            </div>
            <div className="flex items-center gap-2 sm:gap-4">
              <span className="text-sm text-slate-500 hidden sm:inline-block capitalize">Halo, {namaPetugas}</span>
              <div className="w-8 h-8 bg-teal-600 rounded-full flex items-center justify-center text-white font-bold text-xs shrink-0">PT</div>
            </div>
          </header>

          <div className="p-4 md:p-8 space-y-8">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                <p className="text-slate-500 text-xs font-bold uppercase mb-1">Total Balita</p>
                <h3 className="text-3xl font-black text-slate-800">{stats.total}</h3>
                <p className="text-xs text-teal-600 font-medium mt-2">↑ Data terdaftar</p>
              </div>
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                <p className="text-slate-500 text-xs font-bold uppercase mb-1 text-red-500">Gizi Buruk</p>
                <h3 className="text-3xl font-black text-slate-800">{stats.buruk}</h3>
                <p className="text-xs text-slate-400 mt-2">Status per hari ini</p>
              </div>
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                <p className="text-slate-500 text-xs font-bold uppercase mb-1 text-orange-500">Stunting / Pendek</p>
                <h3 className="text-3xl font-black text-slate-800">{stats.stunting}</h3>
                <p className="text-xs text-slate-400 mt-2">Perlu intervensi khusus</p>
              </div>
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                <p className="text-slate-500 text-xs font-bold uppercase mb-1 text-teal-500">Gizi Baik</p>
                <h3 className="text-3xl font-black text-slate-800">{stats.baik}</h3>
                <p className="text-xs text-teal-600 font-medium mt-2">Kondisi Normal</p>
              </div>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 lg:col-span-1">
                <h4 className="font-bold text-slate-800 mb-4 text-center">Distribusi Gizi SVM</h4>
                <div className="relative h-64 w-full">
                  {!isLoading && giziData ? <Doughnut data={giziData} options={{ maintainAspectRatio: false }} /> : <div className="h-full flex items-center justify-center animate-pulse text-teal-500">Memuat grafik...</div>}
                </div>
              </div>
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 lg:col-span-1">
                <h4 className="font-bold text-slate-800 mb-4 text-center">Sebaran per Desa</h4>
                <div className="relative h-64 w-full">
                  {!isLoading && desaData ? <Bar data={desaData} options={{ maintainAspectRatio: false }} /> : <div className="h-full flex items-center justify-center animate-pulse text-teal-500">Memuat grafik...</div>}
                </div>
              </div>
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 lg:col-span-1 flex flex-col">
                <h4 className="font-bold text-slate-800 mb-4">Aksi Cepat Petugas</h4>
                <div className="space-y-3 overflow-y-auto pr-2" style={{ maxHeight: '256px' }}>
                  
                  <Link to="/input" className="flex items-center justify-between p-3 bg-teal-50 rounded-xl border border-teal-100 hover:bg-teal-100 transition">
                    <span className="text-teal-900 font-semibold text-sm">Input Pengukuran Baru</span>
                    <span className="text-teal-600 font-bold">→</span>
                  </Link>
                  
                  <Link to="/data-anak" className="flex items-center justify-between p-3 bg-slate-50 rounded-xl border border-slate-100 hover:bg-slate-100 transition text-left">
                    <span className="text-slate-700 font-semibold text-sm">Cari Riwayat Medis Anak</span>
                    <span className="text-slate-400 font-bold">→</span>
                  </Link>
                  
                  <Link to="/data-anak" className="flex items-center justify-between p-3 bg-slate-50 rounded-xl border border-slate-100 hover:bg-slate-100 transition text-left">
                    <span className="text-slate-700 font-semibold text-sm">Lihat Seluruh Tabel Data</span>
                    <span className="text-slate-400 font-bold">→</span>
                  </Link>

                  {userRole === 'admin' && (
                    <div className="border-t border-slate-200 pt-3 mt-3">
                      <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Menu Administrator</p>
                      <div className="space-y-3">
                        <Link to="/admin" className="flex items-center justify-between p-3 bg-indigo-50 rounded-xl border border-indigo-100 hover:bg-indigo-100 transition text-left">
                          <span className="text-indigo-900 font-semibold text-sm">Logs Aktivitas User</span>
                          <span className="text-indigo-600 font-bold">→</span>
                        </Link>
                        <Link to="/admin" className="flex items-center justify-between p-3 bg-indigo-50 rounded-xl border border-indigo-100 hover:bg-indigo-100 transition text-left">
                          <span className="text-indigo-900 font-semibold text-sm">Manage Akun User</span>
                          <span className="text-indigo-600 font-bold">→</span>
                        </Link>
                      </div>
                    </div>
                  )}

                </div>
              </div>

            </div>
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
              <h4 className="font-bold mb-4 text-slate-800">Peta Sebaran Lokasi Balita</h4>
              <div className="h-96 rounded-xl border-2 border-slate-200 z-0 relative overflow-hidden">
                {!isLoading && mapData ? (
                  <MapContainer center={[-1.815, 105.445]} zoom={11} className="h-full w-full">
                    <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                    {mapData.map((marker, index) => (
                      <CircleMarker 
                        key={index}
                        center={[marker.lat, marker.lng]} 
                        pathOptions={{ color: marker.status.toLowerCase().includes('buruk') || marker.status.toLowerCase().includes('kurang') ? 'red' : 'green' }} 
                        radius={8}
                      >
                        <Popup>
                          <strong>{marker.nama}</strong><br/>
                          Status: {marker.status}
                        </Popup>
                      </CircleMarker>
                    ))}
                  </MapContainer>
                ) : (
                  <div className="h-full flex items-center justify-center animate-pulse text-teal-500">Memuat peta...</div>
                )}
              </div>
            </div>

          </div>
        </main>
      </div>
    </div>
  );
}