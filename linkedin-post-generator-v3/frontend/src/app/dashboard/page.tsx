'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';
import { usePostStore } from '@/stores/postStore';
import { api } from '@/lib/api';
import { motion } from 'framer-motion';
import { BarChart3, FileText, TrendingUp, Plus, LogOut, ArrowRight, Bot } from 'lucide-react';
import Link from 'next/link';
import { ThemeToggle } from '@/components/ThemeToggle';

export default function DashboardPage() {
  const router = useRouter();
  const { user, logout } = useAuthStore();
  const { posts, setPosts, isLoading, setLoading } = usePostStore();

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/posts/history');
      setPosts(response.data.posts || []);
    } catch (error) {
      console.error('Failed to fetch posts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    router.push('/auth/login');
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <div className="min-h-screen relative overflow-hidden bg-background">
      {/* Background Blobs */}
      <div className="absolute top-[-10%] left-[-10%] w-96 h-96 bg-primary rounded-full mix-blend-multiply filter blur-[128px] opacity-20 animate-blob" />
      <div className="absolute bottom-[-10%] right-[-10%] w-96 h-96 bg-secondary rounded-full mix-blend-multiply filter blur-[128px] opacity-20 animate-blob animation-delay-2000" />

      {/* Header */}
      <header className="sticky top-0 w-full z-50 p-4">
        <div className="glass-card max-w-7xl mx-auto px-6 py-3 flex justify-between items-center rounded-full">
          <Link href="/" className="flex items-center gap-2">
            <div className="bg-gradient-to-br from-primary to-secondary p-1.5 rounded-xl">
              <Bot className="text-white" size={20} />
            </div>
            <span className="text-lg font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-secondary">Lumina AI</span>
          </Link>
          
          <div className="flex items-center gap-6">
            <span className="hidden sm:inline text-sm font-medium text-gray-600 dark:text-gray-300">
              Welcome back, <span className="text-foreground font-bold">{user?.full_name?.split(' ')[0] || 'User'}</span>
            </span>
            <div className="flex items-center gap-3">
              <ThemeToggle />
              <button 
                onClick={handleLogout} 
                className="glass-btn-secondary py-2 px-4 text-sm flex items-center gap-2 group"
              >
                <LogOut size={16} className="group-hover:text-red-500 transition-colors" />
                <span className="hidden sm:inline">Logout</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8 relative z-10">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            <motion.div variants={itemVariants} className="glass-card p-6 group hover:-translate-y-1 transition-all">
              <div className="flex items-center gap-5">
                <div className="p-4 bg-gradient-to-br from-primary/20 to-primary/5 rounded-2xl">
                  <FileText className="text-primary" size={28} />
                </div>
                <div>
                  <p className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Total Posts</p>
                  <p className="text-3xl font-extrabold text-foreground">{posts.length}</p>
                </div>
              </div>
            </motion.div>

            <motion.div variants={itemVariants} className="glass-card p-6 group hover:-translate-y-1 transition-all">
              <div className="flex items-center gap-5">
                <div className="p-4 bg-gradient-to-br from-green-500/20 to-green-500/5 rounded-2xl">
                  <TrendingUp className="text-green-500" size={28} />
                </div>
                <div>
                  <p className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Avg Quality</p>
                  <p className="text-3xl font-extrabold text-foreground">
                    {posts.length > 0
                      ? Math.round(posts.reduce((sum, p) => sum + (p.quality_score || 0), 0) / posts.length)
                      : 0}%
                  </p>
                </div>
              </div>
            </motion.div>

            <motion.div variants={itemVariants} className="glass-card p-6 group hover:-translate-y-1 transition-all">
              <div className="flex items-center gap-5">
                <div className="p-4 bg-gradient-to-br from-purple-500/20 to-purple-500/5 rounded-2xl">
                  <BarChart3 className="text-purple-500" size={28} />
                </div>
                <div>
                  <p className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">This Month</p>
                  <p className="text-3xl font-extrabold text-foreground">
                    {posts.filter(p => {
                      const postDate = new Date(p.created_at);
                      const now = new Date();
                      return postDate.getMonth() === now.getMonth() && postDate.getFullYear() === now.getFullYear();
                    }).length}
                  </p>
                </div>
              </div>
            </motion.div>
          </div>

          {/* Action Header */}
          <div className="flex flex-col sm:flex-row justify-between items-center gap-6 mb-8">
            <h2 className="text-3xl font-extrabold text-foreground tracking-tight">Recent Activity</h2>
            <Link href="/dashboard/generate" className="glass-btn-primary flex items-center gap-2 px-8 py-3 text-lg">
              <Plus size={20} />
              Generate New Post
            </Link>
          </div>

          {/* Posts List */}
          {isLoading ? (
            <div className="grid gap-4">
              {[1, 2, 3].map(i => (
                <div key={i} className="glass-card p-8 animate-pulse h-32" />
              ))}
            </div>
          ) : posts.length === 0 ? (
            <motion.div variants={itemVariants} className="glass-card text-center py-20 px-4">
              <div className="max-w-md mx-auto">
                <div className="w-20 h-20 bg-surface-muted rounded-full flex items-center justify-center mx-auto mb-6">
                  <Bot className="text-gray-400" size={40} />
                </div>
                <h3 className="text-2xl font-bold mb-3">No posts yet</h3>
                <p className="text-gray-500 dark:text-gray-400 mb-8">
                  Start your journey by generating your first AI-powered LinkedIn post.
                </p>
                <Link href="/dashboard/generate" className="glass-btn-primary inline-flex items-center gap-2">
                  Create First Post <ArrowRight size={18} />
                </Link>
              </div>
            </motion.div>
          ) : (
            <div className="grid gap-6">
              {posts.slice(0, 10).map((post, idx) => (
                <motion.div
                  key={post.id}
                  variants={itemVariants}
                  whileHover={{ x: 10 }}
                  className="glass-card p-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-6 group transition-all"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-bold text-xl text-foreground line-clamp-1">{post.topic}</h3>
                      <span className="px-3 py-1 bg-primary/10 text-primary text-xs font-bold rounded-full uppercase tracking-widest">
                        {post.mode_used || 'standard'}
                      </span>
                    </div>
                    <p className="text-gray-600 dark:text-gray-300 line-clamp-2 mb-4 text-sm leading-relaxed">
                      {post.content}
                    </p>
                    <div className="flex flex-wrap gap-5 text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-widest">
                      <div className="flex items-center gap-1.5">
                        <div className="w-2 h-2 rounded-full bg-green-500" />
                        Quality: {post.quality_score?.toFixed(0) || 0}%
                      </div>
                      <div className="flex items-center gap-1.5">
                        <div className="w-2 h-2 rounded-full bg-blue-500" />
                        Fact: {post.fact_check_score?.toFixed(0) || 0}%
                      </div>
                      <div className="flex items-center gap-1.5">
                        <div className="w-2 h-2 rounded-full bg-purple-500" />
                        {new Date(post.created_at).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                  <Link 
                    href={`/dashboard/posts/${post.id}`} 
                    className="glass-btn-secondary self-stretch md:self-center flex items-center justify-center gap-2 group-hover:bg-primary group-hover:text-white group-hover:border-transparent transition-all"
                  >
                    View Details <ArrowRight size={16} />
                  </Link>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>
      </main>
    </div>
  );
}
