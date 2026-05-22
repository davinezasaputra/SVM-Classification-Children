import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        // SANGAT PENTING: Agar session cookie dari Flask-Login tersimpan di browser
        credentials: 'include', 
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (response.ok && data.status === 'success') {
        // Simpan data user di localStorage (opsional, untuk nampilin nama di Navbar)
        localStorage.setItem('user', JSON.stringify(data.user));
        
        // Arahkan ke halaman Dashboard tanpa reload
        navigate('/dashboard');
      } else {
        // Tampilkan pesan error dari backend
        setErrorMsg(data.message || 'Gagal login. Silakan coba lagi.');
      }
    } catch (error) {
      console.error('Error during login:', error);
      setErrorMsg('Terjadi kesalahan koneksi ke server.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-gray-50 flex items-center justify-center min-h-screen p-4 font-sans text-gray-800 animate-page">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
        
        {/* Header Section */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-teal-50 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 11c0 3.517-1.009 6.799-2.753 9.571m-3.44-2.04l.054-.09A13.916 13.916 0 008 11a4 4 0 118 0c0 1.017-.071 2.019-.203 3m-2.118 6.844A21.88 21.88 0 0015.171 17m3.839 1.132c.645-2.266.99-4.659.99-7.132A8 8 0 008 4.07M3 15.364c.64-1.319 1-2.8 1-4.364 0-1.457.39-2.823 1.07-4"></path>
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900">Sistem Klasifikasi Gizi</h2>
          <p className="text-sm text-gray-500 mt-1">Puskesmas Simpang Teritip</p>
        </div>

        {/* Error Alert */}
        {errorMsg && (
          <div className="mb-4 p-4 rounded-lg bg-red-50 border border-red-200 text-red-600 text-sm font-medium text-center">
            {errorMsg}
          </div>
        )}

        {/* Form Section */}
        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1.5">Username Petugas</label>
            <input 
              type="text" 
              id="username" 
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required 
              className="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-teal-600 focus:border-teal-600 outline-none transition-all" 
              placeholder="Masukkan username"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1.5">Kata Sandi</label>
            <input 
              type="password" 
              id="password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required 
              className="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-teal-600 focus:border-teal-600 outline-none transition-all" 
              placeholder="••••••••"
            />
          </div>

          <button 
            type="submit" 
            disabled={isLoading}
            className={`w-full py-3 px-4 text-white font-semibold rounded-lg shadow-sm transition-colors duration-200 ${
              isLoading ? 'bg-teal-400 cursor-not-allowed' : 'bg-teal-600 hover:bg-teal-700'
            }`}
          >
            {isLoading ? 'Memproses...' : 'Masuk ke Dasbor'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-xs text-gray-400">&copy; 2026 Puskesmas Simpang Teritip</p>
        </div>
      </div>
    </div>
  );
}