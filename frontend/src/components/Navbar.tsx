import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useEffect, useState } from 'react';

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation(); // Untuk mendeteksi halaman saat ini
  const [namaPetugas, setNamaPetugas] = useState('');

  useEffect(() => {
    // Mengambil nama user yang disimpan saat login
    const userData = localStorage.getItem('user');
    if (userData) {
      const parsedUser = JSON.parse(userData);
      setNamaPetugas(parsedUser.nama || parsedUser.username || '');
    }
  }, []);

  const handleLogout = async () => {
    try {
      await fetch('/api/v1/auth/logout', { method: 'POST', credentials: 'include' });
      localStorage.removeItem('user'); // Bersihkan data lokal
      navigate('/login');
    } catch (error) {
      console.error("Gagal logout:", error);
    }
  };

  // Fungsi penentu gaya CSS jika link sedang aktif (garis bawah putih)
  const navLinkStyle = (path: string) => {
    return location.pathname === path
      ? "text-white relative after:absolute after:left-0 after:-bottom-2 after:w-full after:h-[2px] after:bg-white font-bold"
      : "text-teal-100 hover:text-white transition font-semibold";
  };

  return (
    <nav className="sticky top-0 z-50 bg-gradient-to-r from-teal-700 via-emerald-600 to-teal-700 shadow-2xl font-sans">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        
        {/* Bagian Kiri: Logo & Menu */}
        <div className="flex items-center gap-10">
          
          {/* Identitas Puskesmas */}
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-white shadow-lg flex items-center justify-center overflow-hidden">
              <img 
                src="/Kabupaten-Bangka-Barat.png" 
                alt="Logo Puskesmas"
                className="w-10 h-10 object-contain"
              />
            </div>
            <div>
              <h1 className="text-white font-black text-lg leading-none">Puskesmas Simpang Teritip</h1>
              <p className="text-teal-100 text-xs tracking-wide mt-1">Sistem Monitoring &amp; Klasifikasi Gizi Balita</p>
            </div>
          </div>

          {/* Menu Navigasi */}
          <div className="hidden md:flex items-center gap-8 text-sm">
            <Link to="/dashboard" className={navLinkStyle('/dashboard')}>
              Dashboard
            </Link>
            <Link to="/input" className={navLinkStyle('/input')}>
              Form Klasifikasi
            </Link>
            <Link to="/data-anak" className={navLinkStyle('/data-anak')}>
              Data Anak
            </Link>
          </div>
        </div>

        {/* Bagian Kanan: Profil & Logout */}
        <div className="text-white text-sm font-medium flex items-center">
          <span>Halo, Petugas {namaPetugas}</span>
          <button 
            onClick={handleLogout} 
            className="ml-4 text-red-100 hover:text-white underline transition cursor-pointer"
          >
            Keluar
          </button>
        </div>

      </div>
    </nav>
  );
}