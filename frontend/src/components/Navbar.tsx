import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

export default function Navbar() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await fetch('/api/v1/auth/logout', { method: 'POST', credentials: 'include' });
      localStorage.removeItem('user');
      navigate('/login');
    } catch (error) {
      console.error("Gagal logout:", error);
    }
  };
  const navLinks = [
    { name: 'Dashboard', path: '/dashboard' },
    { name: 'Input Data', path: '/input-data' },
    { name: 'Data Anak', path: '/data-anak' },
    { name: 'Panel Admin', path: '/admin-panel' },
  ];

  return (
    <nav className="bg-white border-b border-slate-200 sticky top-0 z-50 transition-all duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <div className="flex-shrink-0 flex items-center">
            <Link to="/dashboard" className="text-2xl font-black text-teal-700 tracking-tight">
              Sistem<span className="text-emerald-500">Gizi</span>
            </Link>
          </div>
          <div className="hidden md:flex items-center space-x-1">
            {navLinks.map((link) => (
              <Link
                key={link.name}
                to={link.path}
                className={`px-4 py-2 rounded-xl text-sm font-bold transition-all duration-200 ${
                  location.pathname === link.path
                    ? 'bg-teal-50 text-teal-700 shadow-sm'
                    : 'text-slate-500 hover:bg-slate-50 hover:text-teal-600'
                }`}
              >
                {link.name}
              </Link>
            ))}
            <button
              onClick={handleLogout}
              className="ml-4 px-4 py-2 rounded-xl text-sm font-bold bg-red-50 text-red-600 hover:bg-red-100 transition-all"
            >
              Keluar
            </button>
          </div>
          <div className="flex items-center md:hidden">
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="p-2 rounded-xl text-slate-500 hover:bg-slate-100 hover:text-teal-600 focus:outline-none transition-colors"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                {isMobileMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
          
        </div>
      </div>
      {isMobileMenuOpen && (
        <div className="md:hidden bg-white border-b border-slate-200 shadow-2xl absolute w-full left-0 z-50 animate-fade-in-down">
          <div className="px-4 pt-2 pb-6 space-y-2">
            {navLinks.map((link) => (
              <Link
                key={link.name}
                to={link.path}
                onClick={() => setIsMobileMenuOpen(false)}
                className={`block px-4 py-3 rounded-xl text-base font-bold transition-all ${
                  location.pathname === link.path
                    ? 'bg-teal-50 text-teal-700'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-teal-600'
                }`}
              >
                {link.name}
              </Link>
            ))}
            <button
              onClick={() => {
                setIsMobileMenuOpen(false);
                handleLogout();
              }}
              className="w-full text-left block px-4 py-3 mt-4 rounded-xl text-base font-bold bg-red-50 text-red-600 hover:bg-red-100 transition-colors"
            >
              Keluar
            </button>
          </div>
        </div>
      )}
    </nav>
  );
}