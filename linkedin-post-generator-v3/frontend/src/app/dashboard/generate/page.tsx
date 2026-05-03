'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useSession, signIn } from 'next-auth/react';
import { api } from '@/lib/api';
import toast from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Sparkles, Copy, Linkedin, ExternalLink, Bot, Zap, Globe, Target } from 'lucide-react';
import Link from 'next/link';
import { AUDIENCES, CONTENT_TYPES, POST_TYPES, TONES } from '@/features/post-generator/config';
import { ThemeToggle } from '@/components/ThemeToggle';

type GeneratedResponse = {
  success: boolean;
  post: string;
  post_id: number;
  hashtags?: string;
  mode_used: string;
  quality_score?: Record<string, number> | number;
};

export default function GeneratePostPage() {
  const router = useRouter();
  const { data: session } = useSession();
  const [formData, setFormData] = useState({
    post_type: 'simple_topic',
    mode: 'simple',
    content_type: 'educational',
    topic: '',
    github_url: '',
    text_input: '',
    user_key_message: '',
    tone: 'professional',
    audience: 'professionals',
    context: '',
    include_hashtags: true,
    include_caption: false,
    max_length: 2000,
    hackathon_name: '',
    project_name: '',
    problem_statement: '',
    solution_description: '',
    tech_stack_text: '',
    key_features_text: '',
    personal_journey: '',
    achievement: 'participant',
    completion_time_hours: 24,
    hackathon_type: 'general',
  });
  const [isGenerating, setIsGenerating] = useState(false);
  const [isPublishing, setIsPublishing] = useState(false);
  const [generatedPost, setGeneratedPost] = useState<GeneratedResponse | null>(null);
  const [isPublished, setIsPublished] = useState(false);

  const isHackathon = formData.post_type === 'hackathon_project';
  const isAdvanced = formData.post_type === 'advanced_github';

  const handlePublish = async () => {
    if (!session?.accessToken || !session?.userId) {
      toast.error('Please connect your LinkedIn account first');
      signIn('linkedin');
      return;
    }

    if (!generatedPost?.post_id) {
      toast.error('Post ID missing');
      return;
    }

    setIsPublishing(true);
    try {
      const response = await api.post('/api/posts/publish', {
        post_id: generatedPost.post_id,
        access_token: session.accessToken,
        user_id: session.userId,
      });

      if (response.data.success) {
        toast.success('Published to LinkedIn!');
        setIsPublished(true);
      } else {
        toast.error(response.data.error || 'Publishing failed');
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Publishing failed');
    } finally {
      setIsPublishing(false);
    }
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsGenerating(true);

    try {
      const payload =
        formData.post_type === 'hackathon_project'
          ? {
              ...formData,
              topic: formData.project_name || formData.topic,
              tech_stack: formData.tech_stack_text.split(',').map((item) => item.trim()).filter(Boolean),
              key_features: formData.key_features_text.split('\n').map((item) => item.trim()).filter(Boolean),
            }
          : formData;

      const response = await api.post('/api/posts/generate', payload);
      setGeneratedPost(response.data);
      toast.success('Post generated successfully!');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Generation failed');
    } finally {
      setIsGenerating(false);
    }
  };

  const copyToClipboard = () => {
    if (!generatedPost?.post) return;
    const value = [generatedPost.post, generatedPost.hashtags].filter(Boolean).join('\n\n');
    navigator.clipboard.writeText(value);
    toast.success('Copied to clipboard!');
  };

  const qualityScore = (() => {
    if (!generatedPost?.quality_score) return 0;
    if (typeof generatedPost.quality_score === 'number') return Math.round(generatedPost.quality_score);
    const values = Object.values(generatedPost.quality_score).filter((value) => typeof value === 'number');
    return values.length ? Math.round(values.reduce((sum, value) => sum + value, 0) / values.length) : 0;
  })();

  return (
    <div className="min-h-screen relative overflow-hidden bg-background">
      {/* Background Blobs */}
      <div className="absolute top-[-10%] right-[-10%] w-96 h-96 bg-primary rounded-full mix-blend-multiply filter blur-[128px] opacity-20 animate-blob" />
      <div className="absolute bottom-[-10%] left-[-10%] w-96 h-96 bg-secondary rounded-full mix-blend-multiply filter blur-[128px] opacity-20 animate-blob animation-delay-4000" />

      {/* Header */}
      <header className="sticky top-0 w-full z-50 p-4">
        <div className="glass-card max-w-5xl mx-auto px-6 py-3 flex justify-between items-center rounded-full">
          <Link href="/dashboard" className="glass-btn-secondary py-2 px-4 text-sm flex items-center gap-2 group">
            <ArrowLeft size={16} className="group-hover:-translate-x-1 transition-transform" />
            Back
          </Link>
          <div className="flex items-center gap-2">
            <Bot className="text-primary" size={24} />
            <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-secondary">Lumina Creator</h1>
          </div>
          <ThemeToggle />
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-12 relative z-10">
        <AnimatePresence mode="wait">
          {!generatedPost ? (
            <motion.div
              key="generator-form"
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.98 }}
              className="glass-card p-8 md:p-12"
            >
              <div className="mb-10 text-center">
                <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 rounded-full mb-4">
                  <Sparkles className="text-primary" size={16} />
                  <span className="text-xs font-bold uppercase tracking-wider text-primary">AI Content Engine</span>
                </div>
                <h2 className="text-4xl font-extrabold text-foreground mb-4">What's the topic?</h2>
                <p className="text-gray-500 dark:text-gray-400">Tell us what you want to talk about, and Lumina will do the rest.</p>
              </div>

              <form onSubmit={handleGenerate} className="space-y-8">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div className="space-y-2">
                    <label className="flex items-center gap-2 text-sm font-bold text-foreground ml-1">
                      <Zap size={14} className="text-primary" /> POST TYPE
                    </label>
                    <select
                      value={formData.post_type}
                      onChange={(e) =>
                        setFormData((prev) => ({
                          ...prev,
                          post_type: e.target.value,
                          mode: e.target.value === 'advanced_github' ? 'advanced' : 'simple',
                        }))
                      }
                      className="glass-input appearance-none"
                    >
                      {POST_TYPES.map((postType) => (
                        <option key={postType.value} value={postType.value}>
                          {postType.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  {!isHackathon && (
                    <div className="space-y-2">
                      <label className="flex items-center gap-2 text-sm font-bold text-foreground ml-1">
                        <Globe size={14} className="text-primary" /> CONTENT STRATEGY
                      </label>
                      <select
                        value={formData.content_type}
                        onChange={(e) => setFormData({ ...formData, content_type: e.target.value })}
                        className="glass-input appearance-none"
                      >
                        {CONTENT_TYPES.map((contentType) => (
                          <option key={contentType} value={contentType}>
                            {contentType}
                          </option>
                        ))}
                      </select>
                    </div>
                  )}
                </div>

                {!isHackathon && (
                  <div className="space-y-2">
                    <label className="block text-sm font-bold text-foreground ml-1 uppercase">Main Topic *</label>
                    <input
                      type="text"
                      value={formData.topic}
                      onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
                      className="glass-input"
                      placeholder="e.g. The future of AI Agents in software engineering"
                      required
                    />
                  </div>
                )}

                {isAdvanced && (
                  <div className="grid grid-cols-1 gap-8">
                    <div className="space-y-2">
                      <label className="block text-sm font-bold text-foreground ml-1 uppercase">GitHub Repository URL</label>
                      <input
                        type="text"
                        value={formData.github_url}
                        onChange={(e) => setFormData({ ...formData, github_url: e.target.value })}
                        className="glass-input"
                        placeholder="https://github.com/user/repo"
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="block text-sm font-bold text-foreground ml-1 uppercase">Detailed Input / Code Snippets</label>
                      <textarea
                        value={formData.text_input}
                        onChange={(e) => setFormData({ ...formData, text_input: e.target.value })}
                        className="glass-input min-h-[120px]"
                        placeholder="Paste any specific text or code you want to analyze..."
                      />
                    </div>
                  </div>
                )}

                {isHackathon && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="space-y-2">
                      <label className="block text-sm font-bold text-foreground ml-1 uppercase">Hackathon Name</label>
                      <input
                        type="text"
                        value={formData.hackathon_name}
                        onChange={(e) => setFormData({ ...formData, hackathon_name: e.target.value })}
                        className="glass-input"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="block text-sm font-bold text-foreground ml-1 uppercase">Project Name</label>
                      <input
                        type="text"
                        value={formData.project_name}
                        onChange={(e) => setFormData({ ...formData, project_name: e.target.value })}
                        className="glass-input"
                        required
                      />
                    </div>
                    <div className="md:col-span-2 space-y-2">
                      <label className="block text-sm font-bold text-foreground ml-1 uppercase">Problem Statement</label>
                      <textarea
                        value={formData.problem_statement}
                        onChange={(e) => setFormData({ ...formData, problem_statement: e.target.value })}
                        className="glass-input min-h-[100px]"
                        required
                      />
                    </div>
                  </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div className="space-y-2">
                    <label className="flex items-center gap-2 text-sm font-bold text-foreground ml-1">
                      <Bot size={14} className="text-primary" /> WRITING TONE
                    </label>
                    <select
                      value={formData.tone}
                      onChange={(e) => setFormData({ ...formData, tone: e.target.value })}
                      className="glass-input appearance-none"
                    >
                      {TONES.map((tone) => (
                        <option key={tone} value={tone}>
                          {tone}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="space-y-2">
                    <label className="flex items-center gap-2 text-sm font-bold text-foreground ml-1">
                      <Target size={14} className="text-primary" /> AUDIANCE
                    </label>
                    <select
                      value={formData.audience}
                      onChange={(e) => setFormData({ ...formData, audience: e.target.value })}
                      className="glass-input appearance-none"
                    >
                      {AUDIENCES.map((audience) => (
                        <option key={audience} value={audience}>
                          {audience}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="block text-sm font-bold text-foreground ml-1 uppercase">Additional Context</label>
                  <textarea
                    value={formData.context}
                    onChange={(e) => setFormData({ ...formData, context: e.target.value })}
                    className="glass-input min-h-[100px]"
                    placeholder="Anything else we should know? Specific keywords to include?"
                  />
                </div>

                <button
                  type="submit"
                  disabled={isGenerating}
                  className="glass-btn-primary w-full py-5 text-xl flex items-center justify-center gap-3 shadow-2xl hover:scale-[1.02] active:scale-[0.98]"
                >
                  {isGenerating ? (
                    <>
                      <div className="w-6 h-6 border-4 border-white/30 border-t-white rounded-full animate-spin" />
                      Crafting your post...
                    </>
                  ) : (
                    <>
                      <Sparkles size={24} />
                      Generate Masterpiece
                    </>
                  )}
                </button>
              </form>
            </motion.div>
          ) : (
            <motion.div
              key="generator-result"
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-8"
            >
              <div className="glass-card p-1">
                <div className="bg-surface/50 rounded-[22px] p-8 md:p-12">
                  <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-10">
                    <div>
                      <div className="inline-flex items-center gap-2 px-3 py-1 bg-green-500/10 text-green-500 rounded-full mb-3">
                        <Zap size={14} />
                        <span className="text-xs font-bold uppercase tracking-wider">Ready to Post</span>
                      </div>
                      <h2 className="text-4xl font-extrabold text-foreground">Draft Created</h2>
                    </div>
                    <div className="flex gap-3">
                      <button 
                        onClick={copyToClipboard} 
                        className="glass-btn-secondary flex items-center gap-2 px-6"
                      >
                        <Copy size={18} />
                        Copy
                      </button>
                      <button 
                        onClick={() => setGeneratedPost(null)} 
                        className="glass-btn-secondary"
                      >
                        Start Over
                      </button>
                    </div>
                  </div>

                  <div className="glass-card bg-surface-muted/50 p-8 md:p-10 mb-8 relative group">
                    <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                      <div className="bg-primary/20 text-primary px-3 py-1 rounded-full text-xs font-bold">PREVIEW</div>
                    </div>
                    <div className="whitespace-pre-wrap text-lg text-foreground leading-relaxed font-medium">
                      {generatedPost.post}
                    </div>
                    {generatedPost.hashtags && (
                      <div className="mt-8 pt-8 border-t border-border/50 flex flex-wrap gap-2">
                        {generatedPost.hashtags.split(' ').map((tag, i) => (
                          <span key={i} className="text-primary font-bold hover:underline cursor-default">{tag}</span>
                        ))}
                      </div>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="glass-card p-6 flex justify-between items-center bg-gradient-to-br from-primary/5 to-transparent">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-primary/20 rounded-2xl flex items-center justify-center text-primary">
                          <Target size={24} />
                        </div>
                        <span className="font-bold text-gray-500 dark:text-gray-400">QUALITY SCORE</span>
                      </div>
                      <span className="text-3xl font-black text-primary">{qualityScore}%</span>
                    </div>
                    <div className="glass-card p-6 flex justify-between items-center">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-secondary/20 rounded-2xl flex items-center justify-center text-secondary">
                          <Bot size={24} />
                        </div>
                        <span className="font-bold text-gray-500 dark:text-gray-400">AI MODE</span>
                      </div>
                      <span className="text-xl font-bold text-foreground uppercase tracking-widest">{generatedPost.mode_used}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex flex-col md:flex-row gap-6">
                {!isPublished ? (
                  <button
                    onClick={handlePublish}
                    disabled={isPublishing}
                    className="glass-btn-primary flex-1 flex items-center justify-center gap-3 py-6 text-xl bg-[#0077b5] border-none hover:bg-[#005c8e] shadow-xl"
                  >
                    <Linkedin size={24} />
                    {isPublishing ? 'Publishing...' : 'Publish directly to LinkedIn'}
                  </button>
                ) : (
                  <div className="flex-1 flex items-center justify-center gap-3 py-6 text-xl bg-green-500/20 text-green-500 font-bold rounded-3xl border border-green-500/30">
                    <CheckCircle className="animate-bounce" size={24} />
                    Successfully Published!
                    <ExternalLink size={18} />
                  </div>
                )}
                <Link 
                  href="/dashboard" 
                  className="glass-btn-secondary flex items-center justify-center gap-2 px-10 py-6 text-xl font-bold"
                >
                  Return to Hub
                </Link>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}

// Add this at the bottom for the missing icon if not imported
import { CheckCircle } from 'lucide-react';
