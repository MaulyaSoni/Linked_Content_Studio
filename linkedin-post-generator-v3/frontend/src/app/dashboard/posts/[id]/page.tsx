'use client';

import { useEffect, useState } from 'react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Send, CheckCircle, AlertTriangle, Calendar, Award, Bot, Linkedin, Edit3, Save, X } from 'lucide-react';
import Link from 'next/link';
import { ThemeToggle } from '@/components/ThemeToggle';
import { formatError } from '@/lib/utils';
import toast from 'react-hot-toast';

export default function PostViewPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [post, setPost] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [publishing, setPublishing] = useState(false);
  const [publishSuccess, setPublishSuccess] = useState(false);
  const [error, setError] = useState('');
  
  // Edit state
  const [isEditing, setIsEditing] = useState(false);
  const [editedContent, setEditedContent] = useState('');
  const [editedHashtags, setEditedHashtags] = useState<string[]>([]);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchPost();
  }, [params.id]);

  const fetchPost = async () => {
    try {
      const response = await api.get(`/api/posts/${params.id}`);
      setPost(response.data);
      setEditedContent(response.data.content);
      setEditedHashtags(response.data.hashtags || []);
    } catch (err: any) {
      console.error('Failed to fetch post:', err);
      setError('Failed to load the post. It may have been deleted or does not exist.');
    } finally {
      setLoading(false);
    }
  };

  const { data: session } = useSession();

  const handleSave = async () => {
    setSaving(true);
    setError('');
    
    try {
      const response = await api.put(`/api/posts/${params.id}`, {
        content: editedContent,
        hashtags: editedHashtags
      });
      
      setPost(response.data);
      setIsEditing(false);
      toast.success('Post updated successfully!');
    } catch (err: any) {
      setError(formatError(err));
      toast.error('Failed to update post');
    } finally {
      setSaving(false);
    }
  };

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
        toast.success('Published to LinkedIn!');
      } else {
        setError(formatError(response.data.error || 'Failed to publish post'));
      }
      
    } catch (err: any) {
      setError(formatError(err));
    } finally {
      setPublishing(false);
    }
  };

  const qualityScore = (() => {
    if (!post?.quality_score) return 0;
    if (typeof post.quality_score === 'number') return Math.round(post.quality_score);
    const values = Object.values(post.quality_score).filter((value) => typeof value === 'number');
    return values.length ? Math.round(values.reduce((sum: number, value: any) => sum + value, 0) / values.length) : 0;
  })();

  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5 } }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-primary/30 border-t-primary rounded-full animate-spin" />
          <p className="text-gray-500 font-bold tracking-widest uppercase text-xs">Retrieving Content...</p>
        </div>
      </div>
    );
  }

  if (error || !post) {
    return (
      <div className="min-h-screen relative overflow-hidden bg-background p-8 flex items-center justify-center">
        <div className="absolute inset-0 bg-red-500/5 backdrop-blur-3xl" />
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="max-w-md w-full glass-card p-12 text-center relative z-10"
        >
          <div className="w-20 h-20 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-6 text-red-500">
            <AlertTriangle size={40} />
          </div>
          <h2 className="text-2xl font-black text-foreground mb-4 uppercase tracking-tight">Post Not Found</h2>
          <p className="text-gray-500 dark:text-gray-400 mb-10 leading-relaxed">{formatError(error) || "We couldn't find the requested content."}</p>
          <Link href="/dashboard" className="glass-btn-primary w-full inline-block">
            Back to Hub
          </Link>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen relative overflow-hidden bg-background pb-20">
      {/* Background Blobs */}
      <div className="absolute top-[-10%] left-[-10%] w-96 h-96 bg-primary rounded-full mix-blend-multiply filter blur-[128px] opacity-20 animate-blob" />
      <div className="absolute bottom-[-10%] right-[-10%] w-96 h-96 bg-secondary rounded-full mix-blend-multiply filter blur-[128px] opacity-20 animate-blob animation-delay-2000" />

      {/* Header */}
      <header className="sticky top-0 w-full z-50 p-4">
        <div className="glass-card max-w-4xl mx-auto px-6 py-3 flex justify-between items-center rounded-full">
          <Link href="/dashboard" className="glass-btn-secondary py-2 px-4 text-sm flex items-center gap-2 group">
            <ArrowLeft size={16} className="group-hover:-translate-x-1 transition-transform" />
            Hub
          </Link>
          <div className="flex items-center gap-2">
            <Bot className="text-primary" size={24} />
            <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-secondary">Content View</h1>
          </div>
          <ThemeToggle />
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-12 relative z-10">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="space-y-8"
        >
          {/* Metadata Card */}
          <div className="glass-card p-8 bg-gradient-to-br from-primary/5 via-transparent to-transparent">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
              <div className="space-y-4">
                <div className="flex flex-wrap gap-2">
                  <span className="px-3 py-1 bg-primary/20 text-primary text-[10px] font-black uppercase tracking-[0.2em] rounded-full">
                    {post.mode_used || 'standard'} AI
                  </span>
                  <span className={`px-3 py-1 text-[10px] font-black uppercase tracking-[0.2em] rounded-full ${post.status === 'published' ? 'bg-green-500/20 text-green-500' : 'bg-secondary/20 text-secondary'}`}>
                    {post.status}
                  </span>
                </div>
                <h1 className="text-4xl font-black text-foreground tracking-tight leading-none uppercase">{post.topic}</h1>
                <div className="flex items-center gap-6 text-sm font-bold text-gray-500 dark:text-gray-400">
                  <div className="flex items-center gap-2">
                    <Calendar size={16} className="text-primary" />
                    {new Date(post.created_at).toLocaleDateString(undefined, { month: 'long', day: 'numeric', year: 'numeric' })}
                  </div>
                  <div className="flex items-center gap-2">
                    <Award size={16} className="text-primary" />
                    Quality: {qualityScore}%
                  </div>
                </div>
              </div>
              
              <div className="flex flex-wrap gap-4">
                {isEditing ? (
                  <>
                    <button 
                      onClick={() => setIsEditing(false)}
                      disabled={saving}
                      className="flex items-center gap-2 py-4 px-6 rounded-2xl font-black uppercase tracking-widest text-sm transition-all glass-btn-secondary border-red-500/30 text-red-500"
                    >
                      <X size={20} />
                      Cancel
                    </button>
                    <button 
                      onClick={handleSave}
                      disabled={saving}
                      className="flex items-center gap-2 py-4 px-8 rounded-2xl font-black uppercase tracking-widest text-sm transition-all glass-btn-primary"
                    >
                      {saving ? (
                        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      ) : (
                        <>
                          <Save size={20} />
                          Save Changes
                        </>
                      )}
                    </button>
                  </>
                ) : (
                  <>
                    <button 
                      onClick={() => setIsEditing(true)}
                      disabled={post.status === 'published'}
                      className="flex items-center gap-2 py-4 px-6 rounded-2xl font-black uppercase tracking-widest text-sm transition-all glass-btn-secondary"
                    >
                      <Edit3 size={20} />
                      Edit Post
                    </button>
                    <button 
                      onClick={handlePublish}
                      disabled={publishing || publishSuccess || post.status === 'published'}
                      className={`flex items-center gap-3 py-4 px-8 rounded-2xl font-black uppercase tracking-widest text-sm transition-all shadow-xl active:scale-95 ${
                        publishSuccess || post.status === 'published' 
                          ? 'bg-green-500/20 text-green-500 border border-green-500/30' 
                          : 'glass-btn-primary bg-[#0077b5] border-none'
                      }`}
                    >
                      {publishing ? (
                        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      ) : publishSuccess || post.status === 'published' ? (
                        <>
                          <CheckCircle size={20} />
                          Published
                        </>
                      ) : (
                        <>
                          <Linkedin size={20} />
                          Post to LinkedIn
                        </>
                      )}
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Content Card */}
          <div className="glass-card overflow-hidden">
            <div className="bg-surface/30 backdrop-blur-md p-10 md:p-16 border-b border-border/50">
              <div className="max-w-none prose dark:prose-invert">
                {isEditing ? (
                  <textarea
                    value={editedContent}
                    onChange={(e) => setEditedContent(e.target.value)}
                    className="w-full h-[400px] bg-transparent text-xl text-foreground leading-[1.8] font-medium focus:outline-none resize-none border-none p-0"
                    placeholder="Write your post content here..."
                  />
                ) : (
                  <div className="whitespace-pre-wrap text-xl text-foreground leading-[1.8] font-medium selection:bg-primary selection:text-white">
                    {post.content}
                  </div>
                )}
              </div>
            </div>
            
            {(post.hashtags && post.hashtags.length > 0 || isEditing) && (
              <div className="p-8 bg-surface-muted/30">
                <h3 className="text-[10px] font-black text-gray-500 uppercase tracking-[0.3em] mb-4 ml-1">Optimized Hashtags</h3>
                {isEditing ? (
                  <input
                    type="text"
                    value={editedHashtags.join(' ')}
                    onChange={(e) => setEditedHashtags(e.target.value.split(' ').filter(tag => tag.trim() !== ''))}
                    className="w-full bg-primary/5 border border-primary/20 rounded-xl px-4 py-3 text-primary font-bold text-sm focus:outline-none focus:border-primary/50"
                    placeholder="Enter hashtags separated by spaces (e.g., #ai #tech)"
                  />
                ) : (
                  <div className="flex flex-wrap gap-3">
                    {post.hashtags.map((tag: string, i: number) => (
                      <span key={i} className="px-4 py-2 bg-primary/10 text-primary hover:bg-primary/20 transition-colors cursor-default rounded-xl font-bold text-sm">
                        #{tag.replace('#', '')}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Error Message if any */}
          <AnimatePresence>
            {error && (
              <motion.div 
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="bg-red-500/10 border border-red-500/30 text-red-500 p-4 rounded-2xl flex items-center gap-3 font-bold"
              >
                <AlertTriangle size={20} />
                {error}
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </main>
    </div>
  );
}
