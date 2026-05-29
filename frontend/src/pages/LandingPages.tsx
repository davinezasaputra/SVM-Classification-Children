import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

export default function LandingPage() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const user = localStorage.getItem('user');
    if (user) {
      setIsLoggedIn(true);
    }
  }, []);

  const tataNilai = [
    { huruf: 'T', judul: 'Transparansi', desc: 'Keterbukaan Pelayanan, dengan aturan kerja yang jelas, ringkas dan tuntas, sehingga bisa dipahami oleh sasaran Pelayanan.' },
    { huruf: 'E', judul: 'Efisien', desc: 'Bekerja memberikan Pelayanan secara Produktif dan Tepat.' },
    { huruf: 'R', judul: 'Ramah', desc: 'Memperlakukan pelanggan dengan menerapkan etik pelayanan 3 S (Senyum, Salam, Sapa).' },
    { huruf: 'I', judul: 'Integritas', desc: 'Konsisten dalam bekerja sesuai dengan Tupoksi dan kompetensi.' },
    { huruf: 'T', judul: 'Tanggung Jawab', desc: 'Tanggung Jawab dalam melakukan setiap pekerjaan yang diberikan.' },
    { huruf: 'I', judul: 'Informatif', desc: 'Memberikan informasi yang akurat dan jelas untuk setiap layanan yang diberikan.' },
    { huruf: 'P', judul: 'Patient Safety Goal', desc: 'Menciptakan suasana dan lingkungan kerja yang aman dan nyaman dengan mengutamakan keselamatan Pelanggan.' },
  ];
  const staffData = [
    { name: 'dr. Sahat L. Tobing', title: 'Dokter Umum (Medis)', icon: 'fa-user-doctor' },
    { name: 'Rindi Antika, S. Gz', title: 'Nutrisionis (Ahli Gizi)', icon: 'fa-wheat-awn' },
    { name: 'Sri Wahyuni, Amd. Keb', title: 'Bidan Desa', icon: 'fa-person-breastfeeding' },
    { name: 'Yeni, Amd. Keb', title: 'Bidan', icon: 'fa-person-breastfeeding' },
    { name: 'Eka Lestari, Amd. Keb', title: 'Bidan', icon: 'fa-person-breastfeeding' },
    { name: 'Ismaniar, Amd. Kep', title: 'Perawat', icon: 'fa-user-nurse' },
    { name: 'Iis Ismaid, Amd. Kep', title: 'Perawat Gigi', icon: 'fa-tooth' },
    { name: 'Elin Herawati', title: 'Administrasi', icon: 'fa-folder-open' },
  ];

  return (
    <div className="font-sans text-gray-800 antialiased bg-gray-50 scroll-smooth animate-page overflow-x-hidden">
      {/* NAVBAR */}
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

          <div className="hidden lg:flex items-center gap-7">
            <a href="#home" className="text-gray-600 text-sm font-bold hover:text-[#1e3c72] transition">Home</a>
            <a href="#tentang" className="text-gray-600 text-sm font-bold hover:text-[#1e3c72] transition">Tentang</a>
            <a href="#visi-misi" className="text-gray-600 text-sm font-bold hover:text-[#1e3c72] transition">Visi Misi</a>
            <a href="#tata-nilai" className="text-gray-600 text-sm font-bold hover:text-[#1e3c72] transition">Tata Nilai</a>
            <a href="#sdm" className="text-gray-600 text-sm font-bold hover:text-[#1e3c72] transition">Tim Kami</a>
            <a href="#wilayah" className="text-gray-600 text-sm font-bold hover:text-[#1e3c72] transition">Wilayah</a>
            {isLoggedIn ? (
              <Link to="/dashboard" className="bg-[#1e3c72] hover:bg-[#2a5298] text-white px-5 py-2 rounded-full font-bold text-sm shadow-lg transition-all duration-300 flex items-center gap-2 transform hover:-translate-y-0.5">
                <i className="fa-solid fa-gauge"></i> Dashboard
              </Link>
            ) : (
              <Link to="/login" className="bg-[#1e3c72] hover:bg-[#2a5298] text-white px-5 py-2 rounded-full font-bold text-sm shadow-lg transition-all duration-300 flex items-center gap-2 transform hover:-translate-y-0.5">
                <i className="fa-solid fa-right-to-bracket"></i> Login
              </Link>
            )}
          </div>
        </div>
        
        {/* MOBILE MENU */}
        <div className={`${isMobileMenuOpen ? 'flex' : 'hidden'} lg:hidden mt-4 pb-4 flex-col gap-4 text-center border-t pt-4`}>
          <a href="#home" onClick={() => setIsMobileMenuOpen(false)} className="text-gray-600 font-bold hover:text-[#1e3c72] block">Home</a>
          <a href="#tentang" onClick={() => setIsMobileMenuOpen(false)} className="text-gray-600 font-bold hover:text-[#1e3c72] block">Tentang</a>
          <a href="#visi-misi" onClick={() => setIsMobileMenuOpen(false)} className="text-gray-600 font-bold hover:text-[#1e3c72] block">Visi Misi</a>
          <a href="#tata-nilai" onClick={() => setIsMobileMenuOpen(false)} className="text-gray-600 font-bold hover:text-[#1e3c72] block">Tata Nilai</a>
          <a href="#sdm" onClick={() => setIsMobileMenuOpen(false)} className="text-gray-600 font-bold hover:text-[#1e3c72] block">Tim Kami</a>
          <a href="#wilayah" onClick={() => setIsMobileMenuOpen(false)} className="text-gray-600 font-bold hover:text-[#1e3c72] block">Wilayah Kerja</a>
          {isLoggedIn ? (
            <Link to="/dashboard" className="bg-[#1e3c72] text-white mx-auto px-8 py-2 rounded-full font-bold inline-block mt-2">Dashboard</Link>
          ) : (
            <Link to="/login" className="bg-[#1e3c72] text-white mx-auto px-8 py-2 rounded-full font-bold inline-block mt-2">Login Sistem</Link>
          )}
        </div>
      </nav>

      {/* HERO SECTION */}
      <section id="home" className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 bg-cover bg-center" style={{ backgroundImage: "url('https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=1200&q=80')" }}>
        <div className="absolute inset-0 bg-gradient-to-r from-[#1e3c72]/95 to-[#2a5298]/80"></div>
        <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-12 flex flex-col lg:flex-row items-center gap-12">
          <div className="lg:w-7/12 text-center lg:text-left text-white">
            <span className="inline-block bg-emerald-500 text-white text-xs font-extrabold px-4 py-1.5 rounded-full mb-6 uppercase tracking-widest shadow-sm">Transformasi Digital Kesehatan</span>
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-black mb-6 leading-tight drop-shadow-md">Sistem Klasifikasi Status Gizi Balita & Deteksi Stunting</h1>
            <p className="text-lg md:text-xl text-blue-50 mb-10 leading-relaxed max-w-2xl mx-auto lg:mx-0 font-medium">
              Implementasi Kecerdasan Buatan menggunakan Algoritma <strong className="text-white font-bold bg-white/20 px-2 py-0.5 rounded">Support Vector Machine (SVM)</strong> untuk memantau tumbuh kembang anak secara presisi di wilayah kerja Puskesmas Simpang Teritip.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              {isLoggedIn ? (
                <Link to="/dashboard" className="bg-white text-[#1e3c72] hover:bg-gray-100 px-8 py-3.5 rounded-full font-black text-lg shadow-xl transition-all duration-300 transform hover:-translate-y-1 flex justify-center items-center gap-2">
                  <i className="fa-solid fa-gauge"></i> Buka Dashboard
                </Link>
              ) : (
                <Link to="/login" className="bg-white text-[#1e3c72] hover:bg-gray-100 px-8 py-3.5 rounded-full font-black text-lg shadow-xl transition-all duration-300 transform hover:-translate-y-1 flex justify-center items-center gap-2">
                  <i className="fa-solid fa-right-to-bracket"></i> Masuk Aplikasi
                </Link>
              )}
              <a href="#tentang" className="bg-transparent border-2 border-white/50 text-white hover:bg-white/10 px-8 py-3.5 rounded-full font-bold text-lg transition-all duration-300 flex justify-center items-center backdrop-blur-sm">
                Pelajari Lebih Lanjut
              </a>
            </div>
          </div>
          <div className="hidden lg:block lg:w-5/12">
            <img 
              src="https://img.freepik.com/free-vector/doctor-character-background_1270-84.jpg" 
              alt="Ilustrasi Medis" 
              className="w-full max-w-md mx-auto rounded-3xl shadow-2xl animate-bounce" 
              style={{ animationDuration: '4s' }} 
            />
          </div>
        </div>
      </section>

      {/* TENTANG SECTION */}
      <section id="tentang" className="py-24 bg-white relative">
        <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-gray-200 to-transparent"></div>
        <div className="max-w-7xl mx-auto px-6 lg:px-12">
          <div className="text-center max-w-3xl mx-auto mb-20">
            <h2 className="text-3xl md:text-4xl font-black text-[#1e3c72] mb-4">Tentang Aplikasi & Inovasi AI</h2>
            <div className="w-20 h-1.5 bg-emerald-500 mx-auto rounded-full mb-6"></div>
            <p className="text-lg text-gray-600 font-medium">Sinergi antara pelayanan kesehatan masyarakat dengan teknologi kecerdasan buatan.</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white rounded-3xl p-8 border border-gray-100 shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-[0_8px_30px_rgb(0,0,0,0.12)] hover:-translate-y-2 transition-all duration-300 group">
              <div className="w-16 h-16 bg-[#1e3c72]/5 text-[#1e3c72] rounded-2xl flex items-center justify-center text-2xl mb-6 group-hover:bg-[#1e3c72] group-hover:text-white transition-colors duration-300">
                <i className="fa-solid fa-calculator"></i>
              </div>
              <h4 className="text-xl font-bold text-gray-900 mb-3">Standardisasi Otomatis</h4>
              <p className="text-gray-500 leading-relaxed text-sm">Sistem mendeteksi dan mengalibrasi otomatis kesalahan posisi ukur balita (berdiri vs telentang) secara komputasi waktu nyata berdasarkan standar antropometri WHO.</p>
            </div>
            <div className="bg-white rounded-3xl p-8 border border-gray-100 shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-[0_8px_30px_rgb(0,0,0,0.12)] hover:-translate-y-2 transition-all duration-300 group">
              <div className="w-16 h-16 bg-emerald-50 text-emerald-600 rounded-2xl flex items-center justify-center text-2xl mb-6 group-hover:bg-emerald-500 group-hover:text-white transition-colors duration-300">
                <i className="fa-solid fa-brain"></i>
              </div>
              <h4 className="text-xl font-bold text-gray-900 mb-3">Klasifikasi Multi-Indikator</h4>
              <p className="text-gray-500 leading-relaxed text-sm">Mengevaluasi status gizi anak melalui 3 indikator utama (BB/U, TB/U, BB/TB) sekaligus menggunakan model cerdas SVM RBF yang diperkuat SMOTE.</p>
            </div>
            <div className="bg-white rounded-3xl p-8 border border-gray-100 shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-[0_8px_30px_rgb(0,0,0,0.12)] hover:-translate-y-2 transition-all duration-300 group">
              <div className="w-16 h-16 bg-rose-50 text-rose-500 rounded-2xl flex items-center justify-center text-2xl mb-6 group-hover:bg-rose-500 group-hover:text-white transition-colors duration-300">
                <i className="fa-solid fa-shield-halved"></i>
              </div>
              <h4 className="text-xl font-bold text-gray-900 mb-3">Validasi & Deteksi Outlier</h4>
              <p className="text-gray-500 leading-relaxed text-sm">Melindungi validitas data klinis dari kesalahan input petugas melalui deteksi batas deviasi ekstrem dan analisis Confidence Rate probabilitas.</p>
            </div>
          </div>
        </div>
      </section>

      {/* VISI MISI SECTION */}
      <section id="visi-misi" className="py-24 bg-gray-50 border-t border-gray-100">
        <div className="max-w-7xl mx-auto px-6 lg:px-12">
          <div className="flex flex-col lg:flex-row items-start gap-16">
            <div className="lg:w-5/12 sticky top-32">
              <div className="relative">
                <img src="https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=600&q=80" alt="Pelayanan Kesehatan" className="rounded-3xl shadow-2xl relative z-10 w-full object-cover h-[500px]" />
                <div className="absolute -bottom-6 -right-6 w-full h-full border-4 border-[#1e3c72] rounded-3xl z-0 hidden md:block opacity-20"></div>
                
                {/* Float Badge */}
                <div className="absolute -left-6 top-10 bg-white p-4 rounded-2xl shadow-xl z-20 flex items-center gap-4 animate-bounce" style={{ animationDuration: '3s' }}>
                  <div className="w-12 h-12 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center text-xl"><i className="fa-solid fa-heart-pulse"></i></div>
                  <div>
                    <p className="text-xs text-gray-500 font-bold uppercase tracking-wider">Motto Kami</p>
                    <p className="font-bold text-[#1e3c72]">Melayani Sepenuh Hati</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="lg:w-7/12">
              <span className="text-emerald-500 font-extrabold tracking-widest uppercase text-xs mb-2 block">Komitmen Pelayanan</span>
              <h2 className="text-3xl md:text-4xl font-black text-gray-900 mb-10">Visi, Misi & Tujuan <br/><span className="text-[#1e3c72]">Puskesmas Simpang Teritip</span></h2>
              
              <div className="bg-white p-8 rounded-3xl border border-gray-100 shadow-[0_8px_30px_rgb(0,0,0,0.04)] mb-8 hover:shadow-lg transition-shadow">
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center text-xl"><i className="fa-solid fa-eye"></i></div>
                  <h5 className="text-2xl font-bold text-[#1e3c72]">Visi Utama</h5>
                </div>
                <p className="text-gray-600 text-lg font-medium leading-relaxed">"Mewujudkan Masyarakat Yang Sehat dan Mandiri di Wilayah Kerja Puskesmas Simpang Teritip."</p>
              </div>

              <div className="bg-white p-8 rounded-3xl border border-gray-100 shadow-[0_8px_30px_rgb(0,0,0,0.04)] mb-8">
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-12 h-12 bg-emerald-50 text-emerald-600 rounded-xl flex items-center justify-center text-xl"><i className="fa-solid fa-list-check"></i></div>
                  <h5 className="text-2xl font-bold text-[#1e3c72]">Misi Pelayanan</h5>
                </div>
                
                <div className="space-y-6 relative before:absolute before:inset-0 before:ml-[11px] before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-[#1e3c72] before:via-emerald-300 before:to-transparent ml-2">
                  {[
                    "Meningkatkan dan mengembangkan mutu sumber daya kesehatan dan pemberdayaan kesehatan masyarakat.",
                    "Meningkatkan capaian kinerja unit pelayanan / program.",
                    "Meningkatkan koordinasi dan kerjasama lintas program dan lintas sektor.",
                    "Meningkatkan kualitas pelayanan kesehatan yang cepat, tepat, bermutu, dan terjangkau.",
                    "Meningkatkan pengetahuan dan peran serta masyarakat agar dapat berperilaku hidup bersih dan sehat."
                  ].map((misi, idx) => (
                    <div key={idx} className="relative pl-8 group">
                      <div className="absolute left-0 top-1 w-6 h-6 bg-white border-4 border-[#1e3c72] rounded-full group-hover:bg-emerald-400 group-hover:border-emerald-400 transition-colors z-10 shadow-sm"></div>
                      <p className="font-bold text-gray-700 leading-relaxed text-sm group-hover:text-gray-900 transition-colors">{misi}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-[#1e3c72] text-white p-8 rounded-3xl shadow-lg hover:-translate-y-1 transition-transform">
                <div className="flex items-center gap-4 mb-2">
                  <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center"><i className="fa-solid fa-bullseye"></i></div>
                  <h5 className="text-xl font-bold">Tujuan</h5>
                </div>
                <p className="text-blue-100 font-medium">"Menjadikan masyarakat yang sehat dan mandiri di wilayah kerja Puskesmas Simpang Teritip."</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* TATA NILAI TERITIP SECTION */}
      <section id="tata-nilai" className="py-24 bg-white relative overflow-hidden border-b border-gray-100">
        {/* Dekorasi Background */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-50 rounded-full blur-3xl opacity-50 -translate-y-1/2 translate-x-1/2"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-emerald-50 rounded-full blur-3xl opacity-50 translate-y-1/2 -translate-x-1/2"></div>
        
        <div className="max-w-7xl mx-auto px-6 lg:px-12 relative z-10">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <span className="text-emerald-500 font-extrabold tracking-widest uppercase text-xs mb-2 block">Budaya Kerja</span>
            <h2 className="text-3xl md:text-5xl font-black text-[#1e3c72] mb-4">Tata Nilai "TERITIP"</h2>
            <div className="w-20 h-1.5 bg-emerald-500 mx-auto rounded-full mb-6"></div>
            <p className="text-lg text-gray-600 font-medium">Prinsip dan tata nilai dasar yang dipegang teguh dalam setiap aspek pelayanan kami.</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {tataNilai.map((item, index) => (
              <div key={index} className={`bg-white rounded-3xl p-8 border border-gray-100 shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-[0_8px_30px_rgb(0,0,0,0.12)] hover:-translate-y-2 transition-all duration-300 relative overflow-hidden group`}>
                <div className="absolute -right-6 -bottom-6 text-[180px] font-black text-gray-50 group-hover:text-blue-50 transition-colors duration-500 pointer-events-none leading-none select-none z-0">
                  {item.huruf}
                </div> 
                <div className="relative z-10">
                  <div className="w-14 h-14 bg-gradient-to-br from-[#1e3c72] to-[#2a5298] text-white rounded-2xl flex items-center justify-center text-2xl font-black mb-6 shadow-md shadow-blue-900/20 group-hover:scale-110 transition-transform duration-300">
                    {item.huruf}
                  </div>
                  <h4 className="text-xl font-extrabold text-gray-900 mb-3 tracking-tight">{item.judul}</h4>
                  <p className="text-sm text-gray-500 font-medium leading-relaxed">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      
      <section id="struktur" className="py-24 bg-white text-center border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-6 lg:px-12">
          <div className="max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-black text-[#1e3c72] mb-4">Struktur Organisasi Pelayanan</h2>
            <div className="w-20 h-1.5 bg-emerald-500 mx-auto rounded-full mb-6"></div>
            <p className="text-lg text-gray-600 font-medium">Pilar koordinasi pemantauan gizi dan operasional Posyandu.</p>
          </div>
          
          {/* Level 1 */}
          <div className="flex justify-center mb-8 relative z-10">
            <div className="bg-white p-8 rounded-[2rem] border-t-8 border-[#1e3c72] shadow-xl w-full max-w-sm hover:shadow-2xl transition-shadow cursor-pointer">
              <div className="w-24 h-24 bg-[#1e3c72] text-white rounded-full flex items-center justify-center text-4xl mx-auto mb-4 shadow-lg ring-4 ring-blue-50">
                <i className="fa-solid fa-user-tie"></i>
              </div>
              <h5 className="text-xl font-extrabold text-gray-900 mb-1">Kepala Puskesmas</h5>
              <p className="text-emerald-600 font-bold text-sm">Penanggung Jawab & Pengambil Kebijakan</p>
            </div>
          </div>
          
          {/* Connecting Lines */}
          <div className="hidden md:block w-1.5 h-10 bg-gray-200 mx-auto relative z-0"></div>
          <div className="hidden md:block w-2/3 h-1.5 bg-gray-200 mx-auto rounded-full relative z-0"></div>
          <div className="hidden md:flex justify-between w-2/3 mx-auto relative z-0">
            <div className="w-1.5 h-10 bg-gray-200 rounded-b-full"></div>
            <div className="w-1.5 h-10 bg-gray-200 rounded-b-full"></div>
            <div className="w-1.5 h-10 bg-gray-200 rounded-b-full"></div>
          </div>
          
          {/* Level 2 */}
          <div className="grid md:grid-cols-3 gap-6 md:gap-8 mt-8 md:mt-0 relative z-10">
            <div className="bg-white p-8 rounded-[2rem] shadow-lg border border-gray-100 hover:-translate-y-2 transition-transform">
              <div className="w-20 h-20 bg-gray-100 text-gray-600 rounded-2xl flex items-center justify-center text-3xl mx-auto mb-6">
                <i className="fa-solid fa-folder-open"></i>
              </div>
              <h6 className="text-lg font-extrabold text-gray-900 mb-2">Kasubag Tata Usaha</h6>
              <p className="text-gray-500 text-sm font-medium">Manajemen Berkas & Administrasi Sistem</p>
            </div>
            
            <div className="bg-white p-8 rounded-[2rem] shadow-lg border border-gray-100 hover:-translate-y-2 transition-transform">
              <div className="w-20 h-20 bg-emerald-100 text-emerald-600 rounded-2xl flex items-center justify-center text-3xl mx-auto mb-6">
                <i className="fa-solid fa-stethoscope"></i>
              </div>
              <h6 className="text-lg font-extrabold text-gray-900 mb-2">Nutrisionis / Ahli Gizi</h6>
              <p className="text-gray-500 text-sm font-medium">Validator Diagnosa AI & Intervensi Klinis</p>
            </div>
            
            <div className="bg-white p-8 rounded-[2rem] shadow-lg border border-gray-100 hover:-translate-y-2 transition-transform">
              <div className="w-20 h-20 bg-blue-100 text-blue-600 rounded-2xl flex items-center justify-center text-3xl mx-auto mb-6">
                <i className="fa-solid fa-users"></i>
              </div>
              <h6 className="text-lg font-extrabold text-gray-900 mb-2">Kader Posyandu</h6>
              <p className="text-gray-500 text-sm font-medium">Operator Input Data Lapangan</p>
            </div>
          </div>
        </div>
      </section>

      {/* SDM / STAF SECTION (BARU - BERDASARKAN GAMBAR) */}
      <section id="sdm" className="py-24 bg-gray-50 border-t border-gray-100 text-center relative overflow-hidden">
        {/* Dekorasi Background */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-50 rounded-full blur-3xl opacity-30 translate-x-1/2 -translate-y-1/2"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-rose-50 rounded-full blur-3xl opacity-30 translate-y-1/2 -translate-x-1/2"></div>

        <div className="max-w-7xl mx-auto px-6 lg:px-12 relative z-10">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <span className="text-emerald-500 font-extrabold tracking-widest uppercase text-xs mb-2 block">Kekuatan Kami</span>
            <h2 className="text-3xl md:text-4xl font-black text-[#1e3c72] mb-4">Sumber Daya Manusia (SDM)</h2>
            <div className="w-20 h-1.5 bg-emerald-500 mx-auto rounded-full mb-6"></div>
            <p className="text-lg text-gray-600 font-medium">Komposisi tenaga kesehatan dan profesional kami yang berdedikasi melayani masyarakat.</p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
            {staffData.map((item, index) => (
              <div key={index} className="bg-white p-6 rounded-3xl border border-gray-100 shadow-[0_8px_30px_rgb(0,0,0,0.03)] hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)] hover:-translate-y-1 transition-all duration-300 group">
                <div className="w-20 h-20 bg-[#1e3c72]/5 rounded-full flex items-center justify-center text-3xl mx-auto mb-4 shadow-inner border border-blue-50 group-hover:bg-[#1e3c72] transition-colors">
                    <i className={`fa-solid ${item.icon} text-[#1e3c72] group-hover:text-white transition-colors`}></i>
                </div>
                <h6 className="font-bold text-gray-900 text-sm mb-1 leading-tight tracking-tight">{item.name}</h6>
                <p className="text-xs text-emerald-600 font-bold bg-emerald-50 px-2 py-0.5 inline-block rounded-full">{item.title}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* WILAYAH KERJA SECTION */}
      <section id="wilayah" className="py-24 bg-white border-t border-gray-100 text-center">
        <div className="max-w-7xl mx-auto px-6 lg:px-12">
          <div className="max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-black text-[#1e3c72] mb-4">Wilayah Kerja Puskesmas</h2>
            <div className="w-20 h-1.5 bg-emerald-500 mx-auto rounded-full mb-6"></div>
            <p className="text-lg text-gray-600 font-medium">Pemantauan persebaran gizi buruk dilakukan secara intensif di 8 desa strategis wilayah Simpang Teritip.</p>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
            {['Pelangas', 'Kundi', 'Simpang Yul', 'Teritip', 'Berang', 'Mayang', 'Air Nyatoh', 'Rambat'].map((desa, idx) => (
              <div key={idx} className="bg-gray-50 py-8 px-4 rounded-3xl border border-gray-100 shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-lg hover:border-emerald-200 hover:-translate-y-1 transition-all cursor-pointer group">
                <div className="w-12 h-12 bg-rose-50 text-rose-500 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-rose-500 group-hover:text-white transition-colors">
                  <i className="fa-solid fa-location-dot text-xl"></i>
                </div>
                <h6 className="font-bold text-gray-800 text-lg">Desa {desa}</h6>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="bg-[#1e3c72] text-white pt-16 pb-8 border-t-[10px] border-emerald-500 relative overflow-hidden">
        {/* Dekorasi Footer */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full blur-2xl -translate-y-1/2 translate-x-1/2"></div>
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-emerald-500/10 rounded-full blur-2xl translate-y-1/2 -translate-x-1/2"></div>

        <div className="max-w-7xl mx-auto px-6 lg:px-12 relative z-10">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6 border-b border-white/10 pb-10 mb-8">
            <div className="text-center md:text-left">
              <div className="flex items-center justify-center md:justify-start gap-4 mb-4">
                <div className="bg-white p-2 rounded-xl">
                  <img 
                    src="/Kabupaten-Bangka-Barat.png" 
                    alt="Logo" 
                    className="h-12" 
                    onError={(e) => (e.currentTarget.src = 'https://placehold.co/48x48?text=Pusk')} 
                  />
                </div>
                <h3 className="text-2xl font-black tracking-tight leading-none">Puskesmas<br/><span className="text-emerald-400 font-bold text-lg">Simpang Teritip</span></h3>
              </div>
              <p className="text-blue-100/70 text-sm max-w-sm font-medium">Kecamatan Simpang Teritip, Kabupaten Bangka Barat, Kepulauan Bangka Belitung.</p>
            </div>
          </div>
          
          <div className="flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-blue-200/60 font-medium">
            <p>&copy; {new Date().getFullYear()} Proyek Skripsi. All Rights Reserved.</p>
            <p>Dikembangkan oleh <strong className="text-white">Davin</strong> - Teknik Informatika</p>
          </div>
        </div>
      </footer>
    </div>
  );
}