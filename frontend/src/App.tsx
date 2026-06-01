import { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import LandingPage from './pages/LandingPages';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import InputData from './pages/InputData';
import DataAnak from './pages/DataAnak';
import BukuKIA from './pages/BukuKIA';
import AdminPanel from './pages/AdminPanels';

export default function App() {
  useEffect(() => {
    const originalFetch = window.fetch;
    window.fetch = async (...args) => {
      const response = await originalFetch(...args);
      if (response.status === 401 && window.location.pathname !== '/login') {
        localStorage.removeItem('user');
        alert('Sesi Anda telah berakhir dari Server. Silakan login kembali.');
        window.location.href = '/login';
      }
      return response;
    };
    const INACTIVITY_LIMIT = 1 * 60 * 1000; 
    let timeoutId: ReturnType<typeof setTimeout>;

    const resetTimer = () => {
      clearTimeout(timeoutId);
      const user = localStorage.getItem('user');
      if (user && window.location.pathname !== '/login') {
        timeoutId = setTimeout(() => {
          localStorage.removeItem('user');
          alert('Anda dikeluarkan karena tidak ada aktivitas.');
          window.location.href = '/login';
        }, INACTIVITY_LIMIT);
      }
    };
    const events = ['mousemove', 'mousedown', 'keypress', 'DOMMouseScroll', 'mousewheel', 'touchmove', 'MSPointerMove'];
    events.forEach((event) => document.addEventListener(event, resetTimer, true));
    resetTimer();
    return () => {
      events.forEach((event) => document.removeEventListener(event, resetTimer, true));
      clearTimeout(timeoutId);
    };
  }, []);
  return (
    <Router>
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            borderRadius: '16px',
            background: '#334155',
            color: '#fff',
          },
        }} 
      />

      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/input" element={<InputData />} />
        <Route path="/data-anak" element={<DataAnak />} />
        <Route path="/kia/:id" element={<BukuKIA />} />
        <Route path="/admin" element={<AdminPanel />} />
      </Routes>
    </Router>
  );
}