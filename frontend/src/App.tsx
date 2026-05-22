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