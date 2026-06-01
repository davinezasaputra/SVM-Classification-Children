import { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast/headless';
import { useNavigate } from 'react-router-dom';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  
  useEffect(() => {
    const logoutReason = localStorage.getItem('logout_reason');
    if (logoutReason) {
      toast.error(logoutReason);
      localStorage.removeItem('logout_reason');
    }
  }, []);
  
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
        credentials: 'include', 
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (response.ok && data.status === 'success') {
        localStorage.setItem('user', JSON.stringify(data.user));
        navigate('/dashboard');
      } else {
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
        <div className="text-center mb-8">
          <div className="w-17 h-17 mx-auto mb-4 rounded-2xl bg-white shadow-lg flex items-center justify-center overflow-hidden shrink-0">
              <img 
                src="/Kabupaten-Bangka-Barat.png" 
                alt="Logo Puskesmas"
                className="w-15 h-15 object-contain"
              />
            </div>
          <h2 className="text-2xl font-bold text-gray-900">Sistem Klasifikasi Gizi</h2>
          <p className="text-sm text-gray-500 mt-1">Puskesmas Simpang Teritip</p>
        </div>
        {errorMsg && (
          <div className="mb-4 p-4 rounded-lg bg-red-50 border border-red-200 text-red-600 text-sm font-medium text-center">
            {errorMsg}
          </div>
        )}
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