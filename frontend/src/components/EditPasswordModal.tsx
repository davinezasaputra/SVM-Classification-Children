import React, { useState } from 'react';
import { toast } from 'react-hot-toast';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (password: string) => void;
  namaUser: string;
}

export default function EditPasswordModal({ isOpen, onClose, onConfirm, namaUser }: Props) {
  const [password, setPassword] = useState('');

  if (!isOpen) return null;

  const handleSubmit = () => {
    if (password.length < 6) {
      toast.error("Password minimal 6 karakter!");
      return;
    }
    onConfirm(password);
    setPassword('');
  };

  return (
    <div className="fixed inset-0 bg-slate-900/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-3xl p-8 w-full max-w-sm shadow-2xl">
        <h3 className="text-xl font-bold text-slate-800 mb-2">Edit Password</h3>
        <p className="text-slate-500 mb-6 text-sm">Ganti password untuk: <strong>{namaUser}</strong></p>
        
        <input 
          type="password"
          className="w-full rounded-xl border border-slate-200 p-3 mb-6 outline-none focus:border-teal-500 transition"
          placeholder="Password baru (min 6 karakter)"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        
        <div className="flex gap-3">
          <button onClick={onClose} className="flex-1 py-3 rounded-xl font-bold text-slate-600 hover:bg-slate-100 transition">Batal</button>
          <button onClick={handleSubmit} className="flex-1 py-3 rounded-xl font-bold bg-teal-600 text-white hover:bg-teal-700 transition shadow-lg">Simpan</button>
        </div>
      </div>
    </div>
  );
}