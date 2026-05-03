'use client';

import { useEffect, useState } from 'react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { motion } from 'framer-motion';
import { ArrowLeft, Send, CheckCircle, AlertTriangle } from 'lucide-react';
import Link from 'next/link';

export default function PostViewPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [post, setPost] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [publishing, setPublishing] = useState(false);
  const [publishSuccess, setPublishSuccess] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchPost();
  }, [params.id]);

  const fetchPost = async () => {
    try {
      const response = await api.get(`/api/posts/${params.id}`);
      setPost(response.data);
    } catch (err: any) {
      console.error('Failed to fetch post:', err);
      setError('Failed to load the post. It may have been deleted or does not exist.');
    } finally {
      setLoading(false);
    }
  };

  const { data: session } = useSession();

  const handlePublish = async () => {
    setPublishing(true);
    setError('');
    
    try {
      const payload = { 
        post_id: parseInt(params.id), 
        access_token: session?.accessToken || null, 
        user_id: session?.userId || null 
      };
      
      const response = await api.post('/api/posts/publish', payload);
      
      if (response.data.success) {
        setPublishSuccess(true);
        setPost({ ...post, status: 'published' });
      } else {
        setError(response.data.error || 'Failed to publish post');
      }
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to publish post to LinkedIn');
    } finally {
      setPublishing(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-lg text-gray-600">Loading post details...</div>
      </div>
    );
  }

  if (error || !post) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-3xl mx-auto card text-center py-12">
          <AlertTriangle className="mx-auto text-red-500 mb-4" size={48} />
          <h2 className="text-xl font-bold text-gray-900 mb-2">Error Loading Post</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <Link href="/dashboard" className="btn-primary">
            Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-3xl mx-auto">
        <Link href="/dashboard" className="inline-flex items-center text-gray-600 hover:text-primary-600 mb-6 transition-colors">
          <ArrowLeft size={20} className="mr-2" />
          Back to Dashboard
        </Link>
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card overflow-hidden"
        >
          <div className="border-b border-gray-100 pb-4 mb-6 flex justify-between items-start">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">{post.topic}</h1>
              <div className="flex gap-4 text-sm text-gray-500">
                <span>Created: {new Date(post.created_at).toLocaleDateString()}</span>
                <span className="capitalize">Status: {post.status}</span>
              </div>
            </div>
            <div className="flex gap-3">
              <div className="bg-primary-50 text-primary-700 px-3 py-1 rounded-full text-sm font-medium">
                Quality: {post.quality_score?.toFixed(0) || 0}%
              </div>
            </div>
          </div>

          <div className="prose max-w-none mb-8">
            <div className="whitespace-pre-wrap text-gray-800 text-lg leading-relaxed bg-gray-50 p-6 rounded-lg border border-gray-100">
              {post.content}
            </div>
          </div>
          
          {post.hashtags && post.hashtags.length > 0 && (
            <div className="mb-8">
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Hashtags</h3>
              <div className="flex flex-wrap gap-2">
                {post.hashtags.map((tag: string, i: number) => (
                  <span key={i} className="bg-blue-50 text-blue-600 px-3 py-1 rounded-full text-sm font-medium">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div className="border-t border-gray-100 pt-6 mt-6 flex justify-end gap-4">
            <Link href="/dashboard" className="btn-secondary">
              Close
            </Link>
            <button 
              onClick={handlePublish}
              disabled={publishing || publishSuccess || post.status === 'published'}
              className={`flex items-center gap-2 ${publishSuccess || post.status === 'published' ? 'bg-green-600 text-white cursor-not-allowed px-4 py-2 rounded-lg font-medium' : 'btn-primary'}`}
            >
              {publishing ? (
                'Publishing...'
              ) : publishSuccess || post.status === 'published' ? (
                <>
                  <CheckCircle size={18} />
                  Published
                </>
              ) : (
                <>
                  <Send size={18} />
                  Publish to LinkedIn
                </>
              )}
            </button>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
