export const POST_TYPES = [
  { value: 'simple_topic', label: 'Simple Topic', description: 'Fast generation from a topic.' },
  { value: 'advanced_github', label: 'Advanced GitHub', description: 'Use repository context and key message.' },
  { value: 'hackathon_project', label: 'Hackathon Project', description: 'Create a project-story style post.' },
];

export const CONTENT_TYPES = [
  'simple_topic',
  'advanced_github',
  'hackathon_project',
  'thought_leadership',
];

export const TONES = [
  'professional',
  'casual',
  'humorous',
  'inspirational',
];

export const AUDIENCES = [
  'professionals',
  'developers',
  'founders',
  'entrepreneurs',
  'tech_leaders',
  'general',
];
