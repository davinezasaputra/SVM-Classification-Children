import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

export default function LandingPage() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // Cek apakah petugas sudah login saat halaman dimuat
  useEffect(() => {
    const user = localStorage.getItem('user');
    if (user) {
      setIsLoggedIn(true);
    }
  }, []);

  return (
    <div className="font-sans text-gray-800 antialiased bg-gray-50 scroll-smooth animate-page">
      {/* --- NAVBAR --- */}
      <nav className="fixed w-full z-50 bg-white/95 backdrop-blur-sm shadow-md transition-all duration-300 py-3 px-6 lg:px-12">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <a href="#home" className="flex items-center gap-3">
            <img 
              src="/Kabupaten-Bangka-Barat.png" 
              alt="Logo" 
              className="h-10 w-auto" 
              onError={(e) => (e.currentTarget.src = 'https://placehold.co/40x40?text=Pusk')} 
            />
            <div>
              <span className="block font-bold text-[#1e3c72] text-base leading-tight">Puskesmas</span>
              <span className="block text-gray-500 text-xs">Simpang Teritip</span>
            </div>
          </a>
          
          <button 
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} 
            className="lg:hidden text-gray-600 hover:text-[#1e3c72] focus:outline-none"
          >
            <i className="fa-solid fa-bars text-2xl"></i>
          </button>

          <div className="hidden lg:flex items-center gap-8">
            <a href="#home" className="text-gray-600 font-medium hover:text-[#1e3c72] transition">Home</a>
            <a href="#tentang" className="text-gray-600 font-medium hover:text-[#1e3c72] transition">Tentang</a>
            <a href="#visi-misi" className="text-gray-600 font-medium hover:text-[#1e3c72] transition">Visi Misi</a>
            <a href="#wilayah" className="text-gray-600 font-medium hover:text-[#1e3c72] transition">Wilayah Kerja</a>
            <a href="#struktur" className="text-gray-600 font-medium hover:text-[#1e3c72] transition">Struktur</a>
            
            {/* Tombol Navbar Dinamis Berdasarkan Status Login */}
            {isLoggedIn ? (
              <Link to="/dashboard" className="bg-[#1e3c72] hover:bg-[#2a5298] text-white px-6 py-2 rounded-full font-semibold shadow-lg transition-all duration-300 flex items-center gap-2 transform hover:-translate-y-0.5">
                <i className="fa-solid fa-gauge"></i> Ke Dashboard
              </Link>
            ) : (
              <Link to="/login" className="bg-[#1e3c72] hover:bg-[#2a5298] text-white px-6 py-2 rounded-full font-semibold shadow-lg transition-all duration-300 flex items-center gap-2 transform hover:-translate-y-0.5">
                <i className="fa-solid fa-right-to-bracket"></i> Login Sistem
              </Link>
            )}
          </div>
        </div>
        
        {/* Mobile Menu */}
        <div className={`${isMobileMenuOpen ? 'flex' : 'hidden'} lg:hidden mt-4 pb-4 flex-col gap-4 text-center`}>
          <a href="#home" onClick={() => setIsMobileMenuOpen(false)} className="text-gray-600 font-medium hover:text-[#1e3c72] block">Home</a>
          <a href="#tentang" onClick={() => setIsMobileMenuOpen(false)} className="text-gray-600 font-medium hover:text-[#1e3c72] block">Tentang</a>
          <a href="#visi-misi" onClick={() => setIsMobileMenuOpen(false)} className="text-gray-600 font-medium hover:text-[#1e3c72] block">Visi Misi</a>
          <a href="#wilayah" onClick={() => setIsMobileMenuOpen(false)} className="text-gray-600 font-medium hover:text-[#1e3c72] block">Wilayah Kerja</a>
          <a href="#struktur" onClick={() => setIsMobileMenuOpen(false)} className="text-gray-600 font-medium hover:text-[#1e3c72] block">Struktur</a>
          
          {/* Tombol Mobile Dinamis */}
          {isLoggedIn ? (
            <Link to="/dashboard" className="bg-[#1e3c72] text-white mx-auto px-6 py-2 rounded-full font-semibold inline-block">Ke Dashboard</Link>
          ) : (
            <Link to="/login" className="bg-[#1e3c72] text-white mx-auto px-6 py-2 rounded-full font-semibold inline-block">Login Sistem</Link>
          )}
        </div>
      </nav>

      {/* --- HERO SECTION --- */}
      <section id="home" className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 bg-cover bg-center" style={{ backgroundImage: "url('https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=1200&q=80')" }}>
        <div className="absolute inset-0 bg-gradient-to-r from-[#1e3c72]/95 to-[#2a5298]/80"></div>
        
        <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-12 flex flex-col lg:flex-row items-center gap-12">
          <div className="lg:w-7/12 text-center lg:text-left text-white">
            <span className="inline-block bg-green-500 text-white text-xs font-bold px-3 py-1 rounded-full mb-6 uppercase tracking-wider shadow-sm">Transformasi Digital Kesehatan</span>
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6 leading-tight">Sistem Klasifikasi Status Gizi Balita & Deteksi Stunting</h1>
            <p className="text-lg md:text-xl text-blue-100 mb-10 leading-relaxed max-w-2xl mx-auto lg:mx-0">
              Implementasi Kecerdasan Buatan menggunakan Algoritma <strong className="text-white">Support Vector Machine (SVM)</strong> untuk memantau tumbuh kembang anak secara presisi di wilayah kerja Puskesmas Simpang Teritip.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              
              {/* Tombol Hero Dinamis */}
              {isLoggedIn ? (
                <Link to="/dashboard" className="bg-white text-[#1e3c72] hover:bg-gray-100 px-8 py-3 rounded-full font-bold text-lg shadow-xl transition-all duration-300 transform hover:-translate-y-1 flex justify-center items-center gap-2">
                  <i className="fa-solid fa-gauge"></i> Ke Dashboard
                </Link>
              ) : (
                <Link to="/login" className="bg-white text-[#1e3c72] hover:bg-gray-100 px-8 py-3 rounded-full font-bold text-lg shadow-xl transition-all duration-300 transform hover:-translate-y-1 flex justify-center items-center gap-2">
                  <i className="fa-solid fa-right-to-bracket"></i> Masuk Aplikasi
                </Link>
              )}
              
              <a href="#tentang" className="bg-transparent border-2 border-white text-white hover:bg-white/10 px-8 py-3 rounded-full font-bold text-lg transition-all duration-300 flex justify-center items-center">
                Pelajari Lebih Lanjut
              </a>
            </div>
          </div>
          <div className="hidden lg:block lg:w-5/12">
            <img 
              src="https://img.freepik.com/free-vector/doctor-character-background_1270-84.jpg" 
              alt="Ilustrasi Medis" 
              className="w-full max-w-md mx-auto rounded-2xl shadow-2xl animate-bounce" 
              style={{ animationDuration: '3s' }} 
            />
          </div>
        </div>
      </section>

      {/* --- TENTANG SECTION --- */}
      <section id="tentang" className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-6 lg:px-12">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">Tentang Aplikasi & Inovasi AI</h2>
            <p className="text-lg text-gray-600">Sinergi antara pelayanan kesehatan masyarakat dengan teknologi kecerdasan buatan.</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-gray-50 rounded-2xl p-8 border border-gray-100 shadow-sm hover:shadow-xl hover:-translate-y-2 transition-all duration-300 group">
              <div className="w-16 h-16 bg-blue-100 text-[#1e3c72] rounded-xl flex items-center justify-center text-2xl mb-6 group-hover:bg-[#1e3c72] group-hover:text-white transition-colors duration-300">
                <i className="fa-solid fa-calculator"></i>
              </div>
              <h4 className="text-xl font-bold text-gray-900 mb-3">Standardisasi Otomatis</h4>
              <p className="text-gray-600 leading-relaxed">Sistem mendeteksi dan mengalibrasi otomatis kesalahan posisi ukur balita (berdiri vs telentang) secara komputasi waktu nyata berdasarkan standar antropometri WHO.</p>
            </div>
            <div className="bg-gray-50 rounded-2xl p-8 border border-gray-100 shadow-sm hover:shadow-xl hover:-translate-y-2 transition-all duration-300 group">
              <div className="w-16 h-16 bg-blue-100 text-[#1e3c72] rounded-xl flex items-center justify-center text-2xl mb-6 group-hover:bg-[#1e3c72] group-hover:text-white transition-colors duration-300">
                <i className="fa-solid fa-brain"></i>
              </div>
              <h4 className="text-xl font-bold text-gray-900 mb-3">Klasifikasi Multi-Indikator</h4>
              <p className="text-gray-600 leading-relaxed">Mengevaluasi status gizi anak melalui 3 indikator utama (BB/U, TB/U, BB/TB) sekaligus menggunakan model cerdas SVM RBF yang diperkuat SMOTE.</p>
            </div>
            <div className="bg-gray-50 rounded-2xl p-8 border border-gray-100 shadow-sm hover:shadow-xl hover:-translate-y-2 transition-all duration-300 group">
              <div className="w-16 h-16 bg-blue-100 text-[#1e3c72] rounded-xl flex items-center justify-center text-2xl mb-6 group-hover:bg-[#1e3c72] group-hover:text-white transition-colors duration-300">
                <i className="fa-solid fa-shield-halved"></i>
              </div>
              <h4 className="text-xl font-bold text-gray-900 mb-3">Validasi & Deteksi Outlier</h4>
              <p className="text-gray-600 leading-relaxed">Melindungi validitas data klinis dari kesalahan input petugas melalui deteksi batas deviasi ekstrem dan analisis Confidence Rate probabilitas.</p>
            </div>
          </div>
        </div>
      </section>

      {/* --- VISI MISI SECTION --- */}
      <section id="visi-misi" className="py-24 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6 lg:px-12">
          <div className="flex flex-col lg:flex-row items-center gap-16">
            <div className="lg:w-1/2">
              <div className="relative">
                <img src="https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=600&q=80" alt="Pelayanan Kesehatan" className="rounded-3xl shadow-2xl relative z-10 w-full object-cover h-[500px]" />
                <div className="absolute -bottom-6 -right-6 w-full h-full border-4 border-[#1e3c72] rounded-3xl z-0 hidden md:block"></div>
              </div>
            </div>
            <div className="lg:w-1/2">
              <span className="text-[#1e3c72] font-bold tracking-widest uppercase text-sm mb-2 block">Komitmen Pelayanan</span>
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-8">Visi & Misi Puskesmas Simpang Teritip</h2>
              
              <div className="bg-white p-6 rounded-2xl border-l-4 border-[#1e3c72] shadow-sm mb-8">
                <h5 className="flex items-center gap-2 text-xl font-bold text-[#1e3c72] mb-3">
                  <i className="fa-solid fa-eye"></i> Visi
                </h5>
                <p className="text-gray-700 italic text-lg">"Terwujudnya Masyarakat Kecamatan Simpang Teritip yang Sehat, Mandiri, dan Berkeadilan Menuju Bangka Barat Hebat."</p>
              </div>
              
              <h5 className="flex items-center gap-2 text-xl font-bold text-[#1e3c72] mb-6">
                <i className="fa-solid fa-list-check"></i> Misi Utama
              </h5>
              <div className="space-y-6 relative before:absolute before:inset-0 before:ml-2 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-300 before:to-transparent ml-4">
                <div className="relative pl-8">
                  <div className="absolute left-0 top-1.5 w-4 h-4 bg-[#1e3c72] rounded-full border-4 border-white shadow"></div>
                  <h6 className="font-bold text-gray-900 mb-1">Meningkatkan Mutu Pelayanan Kesehataan</h6>
                  <p className="text-gray-600 text-sm">Menyelenggarakan pelayanan kesehatan tingkat pertama yang bermutu, merata, dan terjangkau.</p>
                </div>
                <div className="relative pl-8">
                  <div className="absolute left-0 top-1.5 w-4 h-4 bg-[#1e3c72] rounded-full border-4 border-white shadow"></div>
                  <h6 className="font-bold text-gray-900 mb-1">Pemberdayaan Masyarakat Sehat</h6>
                  <p className="text-gray-600 text-sm">Mendorong kemandirian hidup sehat bagi keluarga dan masyarakat beserta penyehatan lingkungan kerja.</p>
                </div>
                <div className="relative pl-8">
                  <div className="absolute left-0 top-1.5 w-4 h-4 bg-[#1e3c72] rounded-full border-4 border-white shadow"></div>
                  <h6 className="font-bold text-gray-900 mb-1">Pencegahan Stunting & Gizi Buruk</h6>
                  <p className="text-gray-600 text-sm">Menurunkan prevalensi gizi kurang dan stunting secara masif dengan optimalisasi pendataan posyandu berbasis IT.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* --- WILAYAH KERJA SECTION --- */}
      <section id="wilayah" className="py-24 bg-white text-center">
        <div className="max-w-7xl mx-auto px-6 lg:px-12">
          <div className="max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">Wilayah Kerja Puskesmas</h2>
            <p className="text-lg text-gray-600">Pemantauan persebaran gizi buruk dilakukan secara intensif di desa-desa strategis wilayah Simpang Teritip.</p>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
            {['Pelangas', 'Kundi', 'Simpang Yul', 'Teritip', 'Berang', 'Mayang', 'Air Nyatoh', 'Rambat'].map((desa, idx) => (
              <div key={idx} className="bg-gray-50 py-6 px-4 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md hover:bg-blue-50 transition-all cursor-pointer">
                <i className="fa-solid fa-location-dot text-red-500 text-2xl mb-3"></i>
                <h6 className="font-bold text-gray-800">Desa {desa}</h6>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* --- STRUKTUR SECTION --- */}
      <section id="struktur" className="py-24 bg-gray-50 text-center">
        <div className="max-w-7xl mx-auto px-6 lg:px-12">
          <div className="max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">Struktur Organisasi Pelayanan</h2>
            <p className="text-lg text-gray-600">Pilar koordinasi pemantauan gizi dan operasional Posyandu.</p>
          </div>
          
          <div className="flex justify-center mb-8">
            <div className="bg-white p-8 rounded-3xl border-t-4 border-[#1e3c72] shadow-lg w-full max-w-sm">
              <div className="w-20 h-20 bg-[#1e3c72] text-white rounded-full flex items-center justify-center text-3xl mx-auto mb-4 shadow-md">
                <i className="fa-solid fa-user-tie"></i>
              </div>
              <h5 className="text-xl font-bold text-gray-900 mb-1">Kepala Puskesmas</h5>
              <p className="text-gray-500 text-sm">Penanggung Jawab & Pengambil Kebijakan</p>
            </div>
          </div>
          
          <div className="hidden md:block w-px h-8 bg-gray-300 mx-auto"></div>
          <div className="hidden md:block w-2/3 h-px bg-gray-300 mx-auto"></div>
          <div className="hidden md:flex justify-between w-2/3 mx-auto">
            <div className="w-px h-8 bg-gray-300"></div>
            <div className="w-px h-8 bg-gray-300"></div>
            <div className="w-px h-8 bg-gray-300"></div>
          </div>
          
          <div className="grid md:grid-cols-3 gap-6 md:gap-8 mt-8 md:mt-0">
            <div className="bg-white p-6 rounded-3xl shadow border border-gray-100 hover:shadow-lg transition-all">
              <div className="w-16 h-16 bg-gray-600 text-white rounded-full flex items-center justify-center text-xl mx-auto mb-4">
                <i className="fa-solid fa-folder-open"></i>
              </div>
              <h6 className="text-lg font-bold text-gray-900 mb-1">Kasubag Tata Usaha</h6>
              <p className="text-gray-500 text-sm">Manajemen Berkas & Administrasi Sistem</p>
            </div>
            
            <div className="bg-white p-6 rounded-3xl shadow border border-gray-100 hover:shadow-lg transition-all">
              <div className="w-16 h-16 bg-green-600 text-white rounded-full flex items-center justify-center text-xl mx-auto mb-4">
                <i className="fa-solid fa-stethoscope"></i>
              </div>
              <h6 className="text-lg font-bold text-gray-900 mb-1">Nutrisionis / Ahli Gizi</h6>
              <p className="text-gray-500 text-sm">Validator Diagnosa AI & Intervensi Klinis</p>
            </div>
            
            <div className="bg-white p-6 rounded-3xl shadow border border-gray-100 hover:shadow-lg transition-all">
              <div className="w-16 h-16 bg-blue-500 text-white rounded-full flex items-center justify-center text-xl mx-auto mb-4">
                <i className="fa-solid fa-users"></i>
              </div>
              <h6 className="text-lg font-bold text-gray-900 mb-1">Kader Posyandu</h6>
              <p className="text-gray-500 text-sm">Operator Input Data Lapangan</p>
            </div>
          </div>
        </div>
      </section>

      {/* --- FOOTER --- */}
      <footer className="bg-[#1e3c72] text-white pt-16 pb-8 border-t-[10px] border-[#2a5298]">
        <div className="max-w-7xl mx-auto px-6 lg:px-12">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6 border-b border-white/20 pb-8 mb-8">
            <div className="text-center md:text-left">
              <div className="flex items-center justify-center md:justify-start gap-3 mb-4">
                <img 
                  src="/Kabupaten-Bangka-Barat.png" 
                  alt="Logo" 
                  className="h-12 brightness-0 invert opacity-90" 
                  onError={(e) => (e.currentTarget.src = 'https://placehold.co/48x48?text=Pusk')} 
                />
                <h3 className="text-2xl font-bold tracking-tight">Puskesmas<br/><span className="text-lg font-normal text-blue-200">Simpang Teritip</span></h3>
              </div>
              <p className="text-blue-200 text-sm max-w-sm">Kecamatan Simpang Teritip, Kabupaten Bangka Barat, Kepulauan Bangka Belitung.</p>
            </div>
          </div>
          
          <div className="flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-blue-200">
            <p>&copy; {new Date().getFullYear()} Proyek Skripsi Universitas. All Rights Reserved.</p>
            <p>Dikembangkan oleh <strong className="text-white">Davin</strong> - Teknik Informatika</p>
          </div>
        </div>
      </footer>
    </div>
  );
}