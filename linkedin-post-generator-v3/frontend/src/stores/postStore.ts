import { create } from 'zustand';

interface Post {
  id: number;
  topic: string;
  content: string;
  tone?: string;
  hashtags?: string[];
  quality_score?: number;
  fact_check_score?: number;
  status: string;
  created_at: string;
}

interface PostState {
  posts: Post[];
  currentPost: Post | null;
  isLoading: boolean;
  setPosts: (posts: Post[]) => void;
  setCurrentPost: (post: Post | null) => void;
  setLoading: (loading: boolean) => void;
}

export const usePostStore = create<PostState>()((set) => ({
  posts: [],
  currentPost: null,
  isLoading: false,
  
  setPosts: (posts) => set({ posts }),
  setCurrentPost: (post) => set({ currentPost: post }),
  setLoading: (loading) => set({ isLoading: loading }),
}));
