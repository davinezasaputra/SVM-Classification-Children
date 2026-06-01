import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { toast } from 'react-hot-toast';
import Swal from 'sweetalert2';

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const [namaPetugas, setNamaPetugas] = useState('');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      const parsedUser = JSON.parse(userData);
      setNamaPetugas(parsedUser.nama || parsedUser.username || '');
    }
  }, []);

  const handleLogout = async (e: React.MouseEvent) => {
    e.preventDefault();
    
    Swal.fire({
      title: 'Konfirmasi Logout',
      text: "Apakah Anda yakin ingin keluar dari sistem?",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#0f766e', // Warna teal-700 (menyesuaikan tema Dashboard Anda)
      cancelButtonColor: '#ef4444',  // Warna red-500
      confirmButtonText: 'Ya, Keluar',
      cancelButtonText: 'Batal',
      customClass: {
        popup: 'rounded-2xl',
        confirmButton: 'rounded-xl px-6 py-2',
        cancelButton: 'rounded-xl px-6 py-2'
      }
    }).then(async (result) => {
      if (result.isConfirmed) {
        try {
          // Lakukan proses pemutusan sesi dari server
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

  // Fungsi penentu gaya CSS jika link sedang aktif (garis bawah putih)
  const navLinkStyle = (path: string) => {
    return location.pathname === path
      ? "text-white relative after:absolute after:left-0 after:-bottom-2 after:w-full after:h-[2px] after:bg-white font-bold"
      : "text-teal-100 hover:text-white transition font-semibold";
  };

  // 🟢 Fungsi penentu gaya CSS khusus dropdown mobile
  const mobileLinkStyle = (path: string) => {
    return location.pathname === path
      ? "block px-4 py-3 bg-teal-800 text-white font-bold rounded-lg"
      : "block px-4 py-3 text-teal-100 hover:bg-teal-700 hover:text-white transition rounded-lg";
  };

  return (
    <nav className="sticky top-0 z-50 bg-gradient-to-r from-teal-700 via-emerald-600 to-teal-700 shadow-2xl font-sans">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        
        {/* Bagian Kiri: Logo & Menu */}
        <div className="flex items-center gap-10">
          
          {/* Identitas Puskesmas */}
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-white shadow-lg flex items-center justify-center overflow-hidden shrink-0">
              <img 
                src="/Kabupaten-Bangka-Barat.png" 
                alt="Logo Puskesmas"
                className="w-10 h-10 object-contain"
              />
            </div>
            <div>
              <h1 className="text-white font-black text-lg leading-none">Puskesmas Simpang Teritip</h1>
              <p className="text-teal-100 text-xs tracking-wide mt-1 hidden sm:block">Sistem Monitoring &amp; Klasifikasi Gizi Balita</p>
            </div>
          </div>

          {/* Menu Navigasi (DESKTOP) */}
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

        {/* Bagian Kanan: Profil & Logout (DESKTOP) */}
        <div className="hidden md:flex text-white text-sm font-medium items-center">
          <span>Halo, Petugas {namaPetugas}</span>
          <button 
            onClick={handleLogout} 
            className="ml-4 text-red-100 hover:text-white underline transition cursor-pointer"
          >
            Keluar
          </button>
        </div>

        {/* 🟢 TOMBOL HAMBURGER MOBILE (Hanya muncul di HP) */}
        <div className="flex items-center md:hidden">
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="text-white focus:outline-none"
          >
            <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              {isMobileMenuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>
      </div>

      {/* 🟢 DROPDOWN MENU MOBILE (Hanya muncul jika tombol hamburger diklik) */}
      {isMobileMenuOpen && (
        <div className="md:hidden bg-teal-900 border-t border-teal-800 shadow-xl absolute w-full left-0 z-50 animate-fade-in-down">
          <div className="px-4 py-4 space-y-2">
            <Link to="/dashboard" onClick={() => setIsMobileMenuOpen(false)} className={mobileLinkStyle('/dashboard')}>
              Dashboard
            </Link>
            <Link to="/input" onClick={() => setIsMobileMenuOpen(false)} className={mobileLinkStyle('/input')}>
              Form Klasifikasi
            </Link>
            <Link to="/data-anak" onClick={() => setIsMobileMenuOpen(false)} className={mobileLinkStyle('/data-anak')}>
              Data Anak
            </Link>
            
            <div className="border-t border-teal-800 my-2 pt-2"></div>
            
            <div className="px-4 py-2 text-sm text-teal-200">
              Login sebagai: <span className="font-bold text-white">{namaPetugas}</span>
            </div>
            
            <button
              onClick={(e) => {
                setIsMobileMenuOpen(false);
                handleLogout(e as unknown as React.MouseEvent);
              }}
              className="w-full text-left block px-4 py-3 rounded-lg text-base font-bold bg-red-600/20 text-red-100 hover:bg-red-500 hover:text-white transition-colors"
            >
              Keluar dari Sistem
            </button>
          </div>
        </div>
      )}
    </nav>
  );
}