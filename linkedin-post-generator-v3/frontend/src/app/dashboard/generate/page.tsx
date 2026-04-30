'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import toast from 'react-hot-toast';
import { motion } from 'framer-motion';
import { ArrowLeft, Sparkles, Copy } from 'lucide-react';
import Link from 'next/link';
import { AUDIENCES, CONTENT_TYPES, POST_TYPES, TONES } from '@/features/post-generator/config';

type GeneratedResponse = {
  success: boolean;
  post: string;
  hashtags?: string;
  mode_used: string;
  quality_score?: Record<string, number> | number;
};

export default function GeneratePostPage() {
  const router = useRouter();
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
  const [generatedPost, setGeneratedPost] = useState<GeneratedResponse | null>(null);

  const isHackathon = formData.post_type === 'hackathon_project';
  const isAdvanced = formData.post_type === 'advanced_github';

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
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <Link href="/dashboard" className="text-primary-600 hover:underline flex items-center gap-2">
            <ArrowLeft size={16} />
            Back to Dashboard
          </Link>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Generate LinkedIn Post</h1>

        {!generatedPost ? (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="card">
            <form onSubmit={handleGenerate} className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-2">Post Type</label>
                <select
                  value={formData.post_type}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      post_type: e.target.value,
                      mode: e.target.value === 'advanced_github' ? 'advanced' : 'simple',
                    }))
                  }
                  className="input-field"
                >
                  {POST_TYPES.map((postType) => (
                    <option key={postType.value} value={postType.value}>
                      {postType.label}
                    </option>
                  ))}
                </select>
              </div>

              {!isHackathon && (
                <>
                  <div>
                    <label className="block text-sm font-medium mb-2">Content Type</label>
                    <select
                      value={formData.content_type}
                      onChange={(e) => setFormData({ ...formData, content_type: e.target.value })}
                      className="input-field"
                    >
                      {CONTENT_TYPES.map((contentType) => (
                        <option key={contentType} value={contentType}>
                          {contentType}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Topic *</label>
                    <input
                      type="text"
                      value={formData.topic}
                      onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
                      className="input-field"
                      required
                    />
                  </div>
                </>
              )}

              {isAdvanced && (
                <>
                  <div>
                    <label className="block text-sm font-medium mb-2">GitHub URL (optional)</label>
                    <input
                      type="text"
                      value={formData.github_url}
                      onChange={(e) => setFormData({ ...formData, github_url: e.target.value })}
                      className="input-field"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Custom Text (optional)</label>
                    <textarea
                      value={formData.text_input}
                      onChange={(e) => setFormData({ ...formData, text_input: e.target.value })}
                      className="input-field"
                      rows={3}
                    />
                  </div>
                </>
              )}

              {isHackathon && (
                <>
                  <div>
                    <label className="block text-sm font-medium mb-2">Hackathon Name *</label>
                    <input
                      type="text"
                      value={formData.hackathon_name}
                      onChange={(e) => setFormData({ ...formData, hackathon_name: e.target.value })}
                      className="input-field"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Project Name *</label>
                    <input
                      type="text"
                      value={formData.project_name}
                      onChange={(e) => setFormData({ ...formData, project_name: e.target.value })}
                      className="input-field"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Problem Statement *</label>
                    <textarea
                      value={formData.problem_statement}
                      onChange={(e) => setFormData({ ...formData, problem_statement: e.target.value })}
                      className="input-field"
                      rows={3}
                      required
                    />
                  </div>
                </>
              )}

              <div>
                <label className="block text-sm font-medium mb-2">Tone</label>
                <select
                  value={formData.tone}
                  onChange={(e) => setFormData({ ...formData, tone: e.target.value })}
                  className="input-field"
                >
                  {TONES.map((tone) => (
                    <option key={tone} value={tone}>
                      {tone}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Target Audience</label>
                <select
                  value={formData.audience}
                  onChange={(e) => setFormData({ ...formData, audience: e.target.value })}
                  className="input-field"
                >
                  {AUDIENCES.map((audience) => (
                    <option key={audience} value={audience}>
                      {audience}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Additional Context (optional)</label>
                <textarea
                  value={formData.context}
                  onChange={(e) => setFormData({ ...formData, context: e.target.value })}
                  className="input-field"
                  rows={4}
                />
              </div>

              <button
                type="submit"
                disabled={isGenerating}
                className="btn-primary w-full flex items-center justify-center gap-2"
              >
                <Sparkles size={18} />
                {isGenerating ? 'Generating...' : 'Generate Post'}
              </button>
            </form>
          </motion.div>
        ) : (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
            <div className="card">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold">Generated Post</h2>
                <button onClick={copyToClipboard} className="btn-secondary flex items-center gap-2">
                  <Copy size={16} />
                  Copy
                </button>
              </div>

              <div className="bg-gray-50 p-6 rounded-lg whitespace-pre-wrap mb-4">{generatedPost.post}</div>
              {generatedPost.hashtags && (
                <div className="bg-white border p-4 rounded-lg whitespace-pre-wrap mb-4">{generatedPost.hashtags}</div>
              )}

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Quality Score:</span>
                  <span className="ml-2 font-semibold">{qualityScore}%</span>
                </div>
                <div>
                  <span className="text-gray-600">Mode:</span>
                  <span className="ml-2 font-semibold">{generatedPost.mode_used}</span>
                </div>
              </div>
            </div>

            <div className="flex gap-4">
              <button onClick={() => setGeneratedPost(null)} className="btn-primary flex-1">
                Generate Another
              </button>
              <button onClick={() => router.push('/dashboard')} className="btn-secondary flex-1">
                Back to Dashboard
              </button>
            </div>
          </motion.div>
        )}
      </main>
    </div>
  );
}
