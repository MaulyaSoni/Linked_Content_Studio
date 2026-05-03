'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';
import { api } from '@/lib/api';
import toast from 'react-hot-toast';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { Bot, ArrowLeft } from 'lucide-react';

export default function RegisterPage() {
  const router = useRouter();
  const setAuth = useAuthStore((state) => state.setAuth);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    linkedin_url: '',
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await api.post('/api/auth/register', formData);
      const user = response.data;
      
      const loginResponse = await api.post('/api/auth/login', {
        email: formData.email,
        password: formData.password,
      });
      
      setAuth(user, loginResponse.data.access_token);
      toast.success('Account created successfully!');
      router.push('/dashboard');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden flex items-center justify-center p-4">
      {/* Background Orbs */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-primary rounded-full mix-blend-multiply filter blur-[128px] opacity-30 animate-blob" />
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-secondary rounded-full mix-blend-multiply filter blur-[128px] opacity-30 animate-blob animation-delay-2000" />

      <Link href="/" className="absolute top-6 left-6 glass-card p-3 rounded-full hover:scale-105 transition-transform">
        <ArrowLeft className="text-foreground" size={24} />
      </Link>

      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="glass-card w-full max-w-md p-8 relative z-10"
      >
        <div className="flex justify-center mb-6">
          <div className="bg-gradient-to-br from-primary to-secondary p-3 rounded-2xl shadow-lg">
            <Bot className="text-white" size={32} />
          </div>
        </div>
        
        <h1 className="text-3xl font-extrabold text-center mb-2 text-foreground">Create Account</h1>
        <p className="text-center text-gray-500 dark:text-gray-400 mb-8 font-medium">Get started with AI-powered posts</p>

        <form onSubmit={handleRegister} className="space-y-5">
          <div>
            <label className="block text-sm font-bold mb-2 ml-2 text-foreground tracking-wide">FULL NAME</label>
            <input
              type="text"
              value={formData.full_name}
              onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
              className="glass-input"
              placeholder="John Doe"
            />
          </div>

          <div>
            <label className="block text-sm font-bold mb-2 ml-2 text-foreground tracking-wide">EMAIL</label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="glass-input"
              placeholder="name@company.com"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-bold mb-2 ml-2 text-foreground tracking-wide">PASSWORD</label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              className="glass-input"
              placeholder="••••••••"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-bold mb-2 ml-2 text-foreground tracking-wide">LINKEDIN URL (OPTIONAL)</label>
            <input
              type="url"
              value={formData.linkedin_url}
              onChange={(e) => setFormData({ ...formData, linkedin_url: e.target.value })}
              className="glass-input"
              placeholder="https://linkedin.com/in/yourprofile"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="glass-btn-primary w-full mt-6"
          >
            {isLoading ? 'Creating account...' : 'Sign Up'}
          </button>
        </form>

        <p className="text-center mt-8 text-sm font-medium text-gray-500 dark:text-gray-400">
          Already have an account?{' '}
          <Link href="/auth/login" className="text-primary hover:text-primary-light transition-colors font-bold">
            Sign in
          </Link>
        </p>
      </motion.div>
    </div>
  );
}
