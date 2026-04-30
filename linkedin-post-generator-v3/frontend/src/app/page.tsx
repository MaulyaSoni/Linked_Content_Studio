'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';
import { motion } from 'framer-motion';
import { Sparkles, ArrowRight, Zap, Shield, BarChart3 } from 'lucide-react';
import Link from 'next/link';

export default function HomePage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-primary-100">
      {/* Header */}
      <header className="border-b bg-white/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">LinkedIn Post Generator</h1>
          <div className="flex gap-3">
            <Link href="/auth/login" className="btn-secondary">
              Login
            </Link>
            <Link href="/auth/register" className="btn-primary">
              Get Started
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 py-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary-100 rounded-full mb-6">
            <Sparkles className="text-primary-600" size={18} />
            <span className="text-sm font-medium text-primary-700">Powered by AI</span>
          </div>
          
          <h2 className="text-5xl font-bold text-gray-900 mb-6">
            Create LinkedIn Posts
            <br />
            <span className="text-primary-600">That Stand Out</span>
          </h2>
          
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Generate engaging, fact-checked LinkedIn posts in seconds with AI that learns your unique writing style.
          </p>
          
          <div className="flex gap-4 justify-center">
            <Link href="/auth/register" className="btn-primary flex items-center gap-2 text-lg px-8 py-3">
              Start Free <ArrowRight size={20} />
            </Link>
            <Link href="/auth/login" className="btn-secondary text-lg px-8 py-3">
              Login
            </Link>
          </div>
        </motion.div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="card"
          >
            <div className="p-3 bg-blue-100 rounded-lg inline-block mb-4">
              <Zap className="text-blue-600" size={24} />
            </div>
            <h3 className="text-xl font-bold mb-2">AI-Powered Generation</h3>
            <p className="text-gray-600">
              Advanced LangGraph workflows with multi-agent system create high-quality posts tailored to your style.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="card"
          >
            <div className="p-3 bg-green-100 rounded-lg inline-block mb-4">
              <Shield className="text-green-600" size={24} />
            </div>
            <h3 className="text-xl font-bold mb-2">Fact-Checked Content</h3>
            <p className="text-gray-600">
              Multi-layer hallucination prevention ensures your posts are accurate and professional.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="card"
          >
            <div className="p-3 bg-purple-100 rounded-lg inline-block mb-4">
              <BarChart3 className="text-purple-600" size={24} />
            </div>
            <h3 className="text-xl font-bold mb-2">Quality Analytics</h3>
            <p className="text-gray-600">
              Track post performance, quality scores, and engagement metrics to optimize your content strategy.
            </p>
          </motion.div>
        </div>

        {/* How It Works */}
        <div className="text-center mb-16">
          <h3 className="text-3xl font-bold mb-8">How It Works</h3>
          <div className="grid md:grid-cols-4 gap-6">
            {[
              { step: '1', title: 'Sign Up', desc: 'Create your free account' },
              { step: '2', title: 'Enter Topic', desc: 'Tell us what to write about' },
              { step: '3', title: 'AI Generates', desc: 'Our AI creates your post' },
              { step: '4', title: 'Post & Share', desc: 'Copy and share on LinkedIn' },
            ].map((item, index) => (
              <motion.div
                key={item.step}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * index }}
                className="card"
              >
                <div className="w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-4">
                  {item.step}
                </div>
                <h4 className="font-bold mb-2">{item.title}</h4>
                <p className="text-sm text-gray-600">{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="card bg-gradient-to-r from-primary-600 to-primary-700 text-white text-center py-12"
        >
          <h3 className="text-3xl font-bold mb-4">Ready to Get Started?</h3>
          <p className="text-lg mb-6 text-primary-100">
            Join thousands of professionals creating better LinkedIn content with AI
          </p>
          <Link href="/auth/register" className="bg-white text-primary-600 px-8 py-3 rounded-lg font-bold hover:bg-primary-50 transition-colors inline-block">
            Create Free Account
          </Link>
        </motion.div>
      </main>

      {/* Footer */}
      <footer className="border-t bg-white py-8 mt-16">
        <div className="max-w-7xl mx-auto px-4 text-center text-gray-600">
          <p>© 2026 LinkedIn Post Generator v3.0. Built with AI.</p>
        </div>
      </footer>
    </div>
  );
}
