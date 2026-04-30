'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';
import { usePostStore } from '@/stores/postStore';
import { api } from '@/lib/api';
import { motion } from 'framer-motion';
import { BarChart3, FileText, TrendingUp, Plus, LogOut } from 'lucide-react';
import Link from 'next/link';

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

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">LinkedIn Post Generator</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">Welcome, {user?.full_name || user?.email}</span>
            <button onClick={handleLogout} className="btn-secondary flex items-center gap-2">
              <LogOut size={16} />
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card"
          >
            <div className="flex items-center gap-4">
              <div className="p-3 bg-primary-100 rounded-lg">
                <FileText className="text-primary-600" size={24} />
              </div>
              <div>
                <p className="text-sm text-gray-600">Total Posts</p>
                <p className="text-2xl font-bold">{posts.length}</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="card"
          >
            <div className="flex items-center gap-4">
              <div className="p-3 bg-green-100 rounded-lg">
                <TrendingUp className="text-green-600" size={24} />
              </div>
              <div>
                <p className="text-sm text-gray-600">Avg Quality</p>
                <p className="text-2xl font-bold">
                  {posts.length > 0
                    ? Math.round(posts.reduce((sum, p) => sum + (p.quality_score || 0), 0) / posts.length)
                    : 0}%
                </p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="card"
          >
            <div className="flex items-center gap-4">
              <div className="p-3 bg-purple-100 rounded-lg">
                <BarChart3 className="text-purple-600" size={24} />
              </div>
              <div>
                <p className="text-sm text-gray-600">This Month</p>
                <p className="text-2xl font-bold">
                  {posts.filter(p => {
                    const postDate = new Date(p.created_at);
                    const now = new Date();
                    return postDate.getMonth() === now.getMonth();
                  }).length}
                </p>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Actions */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold">Recent Posts</h2>
          <Link href="/dashboard/generate" className="btn-primary flex items-center gap-2">
            <Plus size={16} />
            Generate New Post
          </Link>
        </div>

        {/* Posts List */}
        {isLoading ? (
          <div className="text-center py-12">Loading posts...</div>
        ) : posts.length === 0 ? (
          <div className="card text-center py-12">
            <p className="text-gray-600 mb-4">No posts generated yet</p>
            <Link href="/dashboard/generate" className="btn-primary">
              Create Your First Post
            </Link>
          </div>
        ) : (
          <div className="grid gap-4">
            {posts.slice(0, 10).map((post) => (
              <motion.div
                key={post.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="card"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg mb-2">{post.topic}</h3>
                    <p className="text-gray-600 text-sm line-clamp-3 mb-3">
                      {post.content}
                    </p>
                    <div className="flex gap-4 text-sm text-gray-500">
                      <span>Quality: {post.quality_score?.toFixed(0) || 0}%</span>
                      <span>Fact Check: {post.fact_check_score?.toFixed(0) || 0}%</span>
                      <span>{new Date(post.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <Link href={`/dashboard/posts/${post.id}`} className="btn-secondary text-sm">
                    View
                  </Link>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
