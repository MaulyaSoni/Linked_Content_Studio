'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';
import { motion } from 'framer-motion';
import { Sparkles, ArrowRight, Zap, Shield, BarChart3, Bot, LayoutTemplate } from 'lucide-react';
import Link from 'next/link';
import { ThemeToggle } from '@/components/ThemeToggle';

export default function HomePage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Decorative Blur Blobs */}
      <div className="absolute top-[-10%] left-[-10%] w-96 h-96 bg-primary rounded-full mix-blend-multiply filter blur-[128px] opacity-30 animate-blob" />
      <div className="absolute top-[20%] right-[-10%] w-96 h-96 bg-secondary rounded-full mix-blend-multiply filter blur-[128px] opacity-30 animate-blob animation-delay-2000" />
      <div className="absolute bottom-[-20%] left-[20%] w-96 h-96 bg-pink-400 rounded-full mix-blend-multiply filter blur-[128px] opacity-30 animate-blob animation-delay-4000" />

      {/* Header */}
      <header className="fixed top-0 w-full z-50">
        <div className="glass-card mx-4 mt-4 px-6 py-4 flex justify-between items-center rounded-full">
          <div className="flex items-center gap-2">
            <div className="bg-gradient-to-br from-primary to-secondary p-2 rounded-xl">
              <Bot className="text-white" size={24} />
            </div>
            <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-secondary">Lumina AI</h1>
          </div>
          <div className="flex gap-4 items-center">
            <ThemeToggle />
            <Link href="/auth/login" className="font-semibold text-gray-700 dark:text-gray-200 hover:text-primary transition-colors">
              Log in
            </Link>
            <Link href="/auth/register" className="glass-btn-primary py-2 px-5 text-sm">
              Get Started
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 pt-40 pb-20 relative z-10">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="text-center mb-24 max-w-4xl mx-auto"
        >
          <motion.div variants={itemVariants} className="inline-flex items-center gap-2 px-4 py-2 glass-card rounded-full mb-8">
            <Sparkles className="text-primary" size={18} />
            <span className="text-sm font-semibold tracking-wide text-foreground">Next-Gen Professional Content</span>
          </motion.div>
          
          <motion.h2 variants={itemVariants} className="text-6xl md:text-7xl font-extrabold text-foreground mb-8 leading-tight tracking-tight">
            Create LinkedIn Posts
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary via-secondary to-pink-500">
              That Stand Out
            </span>
          </motion.h2>
          
          <motion.p variants={itemVariants} className="text-xl text-gray-600 dark:text-gray-300 mb-10 max-w-2xl mx-auto leading-relaxed">
            Generate engaging, fact-checked LinkedIn posts in seconds with AI that learns your unique writing style. Deeply integrated with modern professional standards.
          </motion.p>
          
          <motion.div variants={itemVariants} className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/auth/register" className="glass-btn-primary flex items-center justify-center gap-2 text-lg">
              Start Creating Free <ArrowRight size={20} />
            </Link>
            <Link href="/auth/login" className="glass-btn-secondary flex items-center justify-center text-lg">
              View Demo
            </Link>
          </motion.div>
        </motion.div>

        {/* Features Grid */}
        <motion.div 
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          className="grid md:grid-cols-3 gap-8 mb-24"
        >
          <motion.div variants={itemVariants} className="glass-card p-8 group hover:-translate-y-2 transition-all duration-300">
            <div className="w-14 h-14 bg-gradient-to-br from-blue-400 to-blue-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg group-hover:scale-110 transition-transform">
              <Zap className="text-white" size={28} />
            </div>
            <h3 className="text-2xl font-bold mb-3 text-foreground">AI Workflow</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Advanced multi-agent system creates high-quality posts perfectly tailored to your tone of voice.
            </p>
          </motion.div>

          <motion.div variants={itemVariants} className="glass-card p-8 group hover:-translate-y-2 transition-all duration-300">
            <div className="w-14 h-14 bg-gradient-to-br from-green-400 to-green-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg group-hover:scale-110 transition-transform">
              <Shield className="text-white" size={28} />
            </div>
            <h3 className="text-2xl font-bold mb-3 text-foreground">Fact-Checked</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Multi-layer hallucination prevention ensures your posts are impeccably accurate and professional.
            </p>
          </motion.div>

          <motion.div variants={itemVariants} className="glass-card p-8 group hover:-translate-y-2 transition-all duration-300">
            <div className="w-14 h-14 bg-gradient-to-br from-purple-400 to-primary rounded-2xl flex items-center justify-center mb-6 shadow-lg group-hover:scale-110 transition-transform">
              <BarChart3 className="text-white" size={28} />
            </div>
            <h3 className="text-2xl font-bold mb-3 text-foreground">Quality Analytics</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Track post performance, algorithmic quality scores, and deep engagement metrics.
            </p>
          </motion.div>
        </motion.div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="glass-card p-12 text-center relative overflow-hidden"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-primary/20 to-secondary/20 backdrop-blur-3xl -z-10" />
          <h3 className="text-4xl font-extrabold mb-6 text-foreground">Ready to elevate your profile?</h3>
          <p className="text-xl mb-8 text-gray-700 dark:text-gray-200 max-w-2xl mx-auto">
            Join thousands of professionals creating better LinkedIn content with our neural architecture.
          </p>
          <Link href="/auth/register" className="glass-btn-primary inline-flex items-center gap-2 text-xl px-10 py-4">
            Create Free Account <Sparkles size={24} />
          </Link>
        </motion.div>
      </main>

      {/* Footer */}
      <footer className="glass-card m-4 px-6 py-6 text-center text-gray-500 dark:text-gray-400 font-medium">
        <p>© 2026 Lumina AI. Engineered for professionals.</p>
      </footer>
    </div>
  );
}
