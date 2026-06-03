import { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import EditPasswordModal from '../components/EditPasswordModal';

export default function AdminPanel() {
  const [users, setUsers] = useState<any[]>([]);
  const [logs, setLogs] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<any>(null);
  
  // Form States
  const [editingUserId, setEditingUserId] = useState<number | null>(null); // State Mode Edit
  const [username, setUsername] = useState('');
  const [nama, setNama] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('kader');
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Pagination States
  const [userPage, setUserPage] = useState(1);
  const [logPage, setLogPage] = useState(1);
  const USERS_PER_PAGE = 5;
  const LOGS_PER_PAGE = 10;

  const navigate = useNavigate();

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [resUsers, resLogs] = await Promise.all([
        fetch('/api/v1/admin/users', { credentials: 'include' }),
        fetch('/api/v1/admin/logs', { credentials: 'include' })
      ]);

      if (resUsers.status === 403 || resUsers.status === 401) {
        toast.error('Akses ditolak! Khusus Administrator.');
        navigate('/dashboard');
        return;
      }

      const dataUsers = await resUsers.json();
      const dataLogs = await resLogs.json();

      if (dataUsers.status === 'success') setUsers(dataUsers.data);
      if (dataLogs.status === 'success') setLogs(dataLogs.data);

    } catch (error) {
      console.error("Gagal mengambil data admin:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [navigate]);

  // FUNGSI GABUNGAN: TAMBAH & EDIT AKUN
  const handleSubmitUser = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Jika mode tambah, password wajib. Jika mode edit, password opsional.
    if (!username || !nama || (!editingUserId && !password)) {
      toast.error("Mohon lengkapi data yang wajib!");
      return;
    }

    setIsSubmitting(true);
    try {
      const url = editingUserId ? `/api/v1/admin/users/${editingUserId}` : '/api/v1/admin/users';
      const method = editingUserId ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ username, nama, password, role })
      });
      const result = await response.json();
      
      if (response.ok && result.status === 'success') {
        toast.success(result.message);
        handleCancelEdit(); // Kosongkan form kembali ke mode Tambah
        fetchData();
      } else {
        toast.error(`Gagal: ${result.message}`);
      }
    } catch (error) {
      toast.error("Terjadi kesalahan sistem saat menyimpan data.");
    } finally {
      setIsSubmitting(false);
    }
  };

  // TRIGGER MASUK KE MODE EDIT
  const handleEditClick = (u: any) => {
    setEditingUserId(u.id);
    setNama(u.nama);
    setUsername(u.username);
    setRole(u.role);
    setPassword(''); // Password dikosongkan agar tidak terubah jika tidak diisi
    window.scrollTo({ top: 0, behavior: 'smooth' }); // Scroll otomatis ke atas
  };

  // BATALKAN MODE EDIT
  const handleCancelEdit = () => {
    setEditingUserId(null);
    setNama('');
    setUsername('');
    setPassword('');
    setRole('kader');
  };

  const handleResetPassword = async (id: number, namaUser: string) => {
    if (window.confirm(`Yakin ingin mereset password akun ${namaUser} menjadi bawaan pabrik (puskesmas123)?`)) {
      try {
        const response = await fetch(`/api/v1/admin/users/reset/${id}`, {
          method: 'POST',
          credentials: 'include'
        });
        const result = await response.json();
        
        if (response.ok && result.status === 'success') {
          toast.success(result.message);
          fetchData();
        } else {
          toast.error(`Gagal reset password: ${result.message}`);
        }
      } catch (error) {
        toast.error("Terjadi kesalahan saat mereset password.");
      }
    }
  };

  const triggerEditPassword = (u: any) => {
    setSelectedUser(u);
    setIsModalOpen(true);
  };

  const handleEditPasswordConfirm = async (password: string) => {
    try {
      const response = await fetch(`/api/v1/admin/users/edit-password/${selectedUser.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ password })
      });
      
      const result = await response.json();
      
      if (response.ok && result.status === 'success') {
        toast.success(result.message);
        setIsModalOpen(false);
        fetchData();
      } else {
        toast.error(`Gagal: ${result.message}`);
      }
    } catch (error) {
      toast.error("Terjadi kesalahan sistem saat mengubah password.");
    }
  };

  const totalUserPages = Math.ceil(users.length / USERS_PER_PAGE) || 1;
  const totalLogPages = Math.ceil(logs.length / LOGS_PER_PAGE) || 1;

  const currentUsers = users.slice((userPage - 1) * USERS_PER_PAGE, userPage * USERS_PER_PAGE);
  const currentLogs = logs.slice((logPage - 1) * LOGS_PER_PAGE, logPage * LOGS_PER_PAGE);

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-800 animate-page">
      <Navbar />

      <main className="max-w-7xl mx-auto w-full p-6 lg:p-8 flex-1 space-y-8">
        <div>
          <h2 className="text-3xl font-black text-teal-800">Panel Administrator</h2>
          <p className="text-slate-500 mt-1">Manajemen akun petugas dan pemantauan log sistem.</p>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Kolom Kiri: Form MULTIFUNGSI (Tambah / Edit) */}
          <div className="lg:col-span-1">
            <div className={`bg-white rounded-3xl shadow-xl p-8 border h-full transition-colors ${editingUserId ? 'border-blue-300 ring-4 ring-blue-50' : 'border-slate-100'}`}>
              <div className="flex justify-between items-center mb-6 border-b pb-4">
                <h3 className={`text-xl font-bold ${editingUserId ? 'text-blue-700' : 'text-slate-800'}`}>
                  {editingUserId ? 'Edit Data Pengguna' : 'Tambah Pengguna Baru'}
                </h3>
                {editingUserId && (
                  <span className="bg-blue-100 text-blue-700 text-xs font-bold px-2 py-1 rounded">Mode Edit</span>
                )}
              </div>
              
              <form onSubmit={handleSubmitUser} className="space-y-4">
                <div>
                  <label className="text-sm font-bold text-slate-600 block mb-2">Nama Lengkap</label>
                  <input type="text" value={nama} onChange={(e) => setNama(e.target.value)} placeholder="Contoh: Bidan Siti" className="w-full rounded-xl border border-slate-200 bg-slate-50 p-3 outline-none focus:border-teal-500 focus:bg-white transition" />
                </div>
                <div>
                  <label className="text-sm font-bold text-slate-600 block mb-2">Username</label>
                  <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Untuk login aplikasi" className="w-full rounded-xl border border-slate-200 bg-slate-50 p-3 outline-none focus:border-teal-500 focus:bg-white transition" />
                </div>
                <div>
                  <label className="text-sm font-bold text-slate-600 block mb-2">
                    {editingUserId ? 'Ubah Sandi (Opsional)' : 'Password Awal'}
                  </label>
                  <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder={editingUserId ? "Kosongkan jika tidak diubah" : "Minimal 6 karakter"} className="w-full rounded-xl border border-slate-200 bg-slate-50 p-3 outline-none focus:border-teal-500 focus:bg-white transition" />
                </div>
                <div>
                  <label className="text-sm font-bold text-slate-600 block mb-2">Hak Akses (Role)</label>
                  <select value={role} onChange={(e) => setRole(e.target.value)} className="w-full rounded-xl border border-slate-200 bg-slate-50 p-3 outline-none focus:border-teal-500 focus:bg-white transition">
                    <option value="kader">Kader Posyandu</option>
                    <option value="admin">Administrator</option>
                  </select>
                </div>
                
                <div className="flex gap-2 pt-2">
                  <button type="submit" disabled={isSubmitting} className={`flex-1 text-white font-bold py-3 px-4 rounded-xl shadow-md transition disabled:opacity-70 ${editingUserId ? 'bg-blue-600 hover:bg-blue-700' : 'bg-teal-600 hover:bg-teal-700'}`}>
                    {isSubmitting ? 'Memproses...' : (editingUserId ? 'Simpan Perubahan' : 'Buat Akun')}
                  </button>
                  {editingUserId && (
                    <button type="button" onClick={handleCancelEdit} className="bg-slate-200 hover:bg-slate-300 text-slate-700 font-bold py-3 px-4 rounded-xl transition">
                      Batal
                    </button>
                  )}
                </div>
              </form>
            </div>
          </div>

          {/* Kolom Kanan: Tabel Users */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-3xl shadow-xl p-8 border border-slate-100 h-full flex flex-col">
              <h3 className="text-xl font-bold text-slate-800 mb-6 border-b pb-4">Daftar Akun Terdaftar</h3>
              <div className="overflow-x-auto flex-1">
                <table className="min-w-full text-left text-sm">
                  <thead className="bg-slate-100 text-slate-600 uppercase font-bold text-xs">
                    <tr>
                      <th className="py-3 px-4 rounded-l-xl">Nama Pengguna</th>
                      <th className="py-3 px-4">Username</th>
                      <th className="py-3 px-4">Role</th>
                      <th className="py-3 px-4 text-center rounded-r-xl">Aksi Khusus</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {isLoading ? (
                      <tr><td colSpan={4} className="py-8 text-center text-teal-600 animate-pulse font-semibold">Memuat data...</td></tr>
                    ) : currentUsers.length === 0 ? (
                      <tr><td colSpan={4} className="py-8 text-center text-slate-400">Belum ada akun.</td></tr>
                    ) : (
                      currentUsers.map((u) => (
                        <tr key={u.id} className={`transition ${editingUserId === u.id ? 'bg-blue-50' : 'hover:bg-slate-50'}`}>
                          <td className="py-4 px-4 font-bold text-slate-800">{u.nama}</td>
                          <td className="py-4 px-4 font-mono text-slate-600">{u.username}</td>
                          <td className="py-4 px-4">
                            <span className={`px-3 py-1 rounded-full text-xs font-bold border ${u.role === 'admin' ? 'bg-indigo-50 text-indigo-700 border-indigo-200' : 'bg-teal-50 text-teal-700 border-teal-200'}`}>
                              {u.role.toUpperCase()}
                            </span>
                          </td>
                          <td className="py-4 px-4 text-center space-x-1 sm:space-x-2">
                            <button onClick={() => triggerEditPassword(u)} className="bg-slate-50 hover:bg-slate-200 text-slate-700 text-xs font-bold py-2 px-3 rounded-lg transition border border-slate-200 mt-1">
                              Sandi
                            </button>
                            <button onClick={() => handleResetPassword(u.id, u.nama)} className="bg-orange-50 hover:bg-orange-100 text-orange-700 text-xs font-bold py-2 px-3 rounded-lg transition border border-orange-200 mt-1">
                              Reset
                            </button>
                            {/* TOMBOL EDIT PROFIL BARU */}
                            <button onClick={() => handleEditClick(u)} className="bg-blue-50 hover:bg-blue-100 text-blue-700 text-xs font-bold py-2 px-3 rounded-lg transition border border-blue-200 mt-1">
                              Edit
                            </button>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>

              {/* User Pagination Controls */}
              {!isLoading && totalUserPages > 1 && (
                <div className="flex justify-between items-center mt-6 pt-4 border-t border-slate-100">
                  <span className="text-sm font-medium text-slate-500">
                    Halaman <span className="text-slate-800 font-bold">{userPage}</span> dari {totalUserPages}
                  </span>
                  <div className="flex space-x-2">
                    <button 
                      onClick={() => setUserPage(prev => Math.max(1, prev - 1))}
                      disabled={userPage === 1}
                      className="px-4 py-2 rounded-lg border border-slate-200 text-sm font-bold text-slate-600 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
                    >
                      Sebelumnya
                    </button>
                    <button 
                      onClick={() => setUserPage(prev => Math.min(totalUserPages, prev + 1))}
                      disabled={userPage === totalUserPages}
                      className="px-4 py-2 rounded-lg border border-slate-200 text-sm font-bold text-slate-600 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
                    >
                      Selanjutnya
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Bagian Bawah: Log Sistem */}
        <div className="bg-white rounded-3xl shadow-xl p-8 border border-slate-100 flex flex-col">
          <h3 className="text-xl font-bold text-slate-800 mb-6 border-b pb-4">Riwayat Log Sistem (100 Terakhir)</h3>
          <div className="overflow-x-auto border border-slate-100 rounded-xl flex-1">
            <table className="min-w-full text-left text-sm relative">
              <thead className="bg-slate-100 text-slate-600 font-bold text-xs sticky top-0 z-10 shadow-sm">
                <tr>
                  <th className="py-3 px-4 w-40">Waktu</th>
                  <th className="py-3 px-4 w-64">Pengguna</th>
                  <th className="py-3 px-4">Aktivitas</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {isLoading ? (
                  <tr><td colSpan={3} className="py-8 text-center text-teal-600">Memuat log...</td></tr>
                ) : currentLogs.length === 0 ? (
                  <tr><td colSpan={3} className="py-8 text-center text-slate-400">Belum ada riwayat aktivitas.</td></tr>
                ) : (
                  currentLogs.map((log, index) => (
                    <tr key={index} className="hover:bg-slate-50 transition">
                      <td className="py-3 px-4 text-xs font-mono text-slate-500 whitespace-nowrap">{log.waktu}</td>
                      <td className="py-3 px-4 font-semibold text-slate-700">{log.pengguna}</td>
                      <td className="py-3 px-4 text-slate-600">{log.aksi}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Log Pagination Controls */}
          {!isLoading && totalLogPages > 1 && (
            <div className="flex justify-between items-center mt-6">
              <span className="text-sm font-medium text-slate-500">
                Halaman <span className="text-slate-800 font-bold">{logPage}</span> dari {totalLogPages}
              </span>
              <div className="flex space-x-2">
                <button 
                  onClick={() => setLogPage(prev => Math.max(1, prev - 1))}
                  disabled={logPage === 1}
                  className="px-4 py-2 rounded-lg border border-slate-200 text-sm font-bold text-slate-600 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
                >
                  Sebelumnya
                </button>
                <button 
                  onClick={() => setLogPage(prev => Math.min(totalLogPages, prev + 1))}
                  disabled={logPage === totalLogPages}
                  className="px-4 py-2 rounded-lg border border-slate-200 text-sm font-bold text-slate-600 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
                >
                  Selanjutnya
                </button>
              </div>
            </div>
          )}
        </div>

      </main>
      <EditPasswordModal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)}
        namaUser={selectedUser?.nama || "Pengguna"}
        onConfirm={handleEditPasswordConfirm}
      />
    </div>
  );
}