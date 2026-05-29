import type { EmotionCategory, ThemeCategory } from './types';

export const EMOTION_ORDER: EmotionCategory[] = [
  'joyful_activation',
  'triumphant_power',
  'peacefulness',
  'tenderness',
  'nostalgia_longing',
  'sadness_melancholy',
  'tension_anxiety',
  'anger_defiance',
];

export const THEME_ORDER: ThemeCategory[] = [
  'interpersonal_devotion',
  'heartbreak_loss',
  'adversity_resilience',
  'identity_autonomy',
  'status_ambition',
  'hedonism_escape',
  'place_heritage',
  'existentialism_spirituality',
];

export const EMOTIONS: Record<
  EmotionCategory,
  { label: string; short: string; valence: number; arousal: number; color: string; description: string }
> = {
  joyful_activation: {
    label: 'Joyful Activation',
    short: 'Joy',
    valence: 0.8,
    arousal: 0.6,
    color: 'oklch(0.72 0.16 74)',
    description: 'Uplifting, energetic joy; peak happiness paired with kinetic motion.',
  },
  triumphant_power: {
    label: 'Triumphant Power',
    short: 'Power',
    valence: 0.58,
    arousal: 0.82,
    color: 'oklch(0.58 0.16 286)',
    description: 'Confident forward motion, overcoming obstacles, and standing on solid ground.',
  },
  peacefulness: {
    label: 'Peacefulness',
    short: 'Peace',
    valence: 0.78,
    arousal: -0.7,
    color: 'oklch(0.66 0.13 166)',
    description: 'Calm, still, meditative music that releases pressure rather than raising it.',
  },
  tenderness: {
    label: 'Tenderness',
    short: 'Tender',
    valence: 0.68,
    arousal: -0.32,
    color: 'oklch(0.71 0.14 348)',
    description: 'Soft, intimate connection and quiet devotion without urgency.',
  },
  nostalgia_longing: {
    label: 'Nostalgia & Longing',
    short: 'Longing',
    valence: 0.18,
    arousal: -0.42,
    color: 'oklch(0.66 0.13 238)',
    description: 'Wistful memory, future-facing questions, and looking back to understand the present.',
  },
  sadness_melancholy: {
    label: 'Sadness & Melancholy',
    short: 'Sadness',
    valence: -0.78,
    arousal: -0.58,
    color: 'oklch(0.52 0.14 255)',
    description: 'Low-valence reflection, quiet grief, and the emotional gravity of loss.',
  },
  tension_anxiety: {
    label: 'Tension & Anxiety',
    short: 'Tension',
    valence: -0.62,
    arousal: 0.5,
    color: 'oklch(0.6 0.18 28)',
    description: 'Constricted, unsettled energy and anticipation of change.',
  },
  anger_defiance: {
    label: 'Anger & Defiance',
    short: 'Defiance',
    valence: -0.72,
    arousal: 0.82,
    color: 'oklch(0.43 0.16 28)',
    description: 'Confrontational release, rebellion, and high-energy refusal.',
  },
};

export const THEMES: Record<
  ThemeCategory,
  { label: string; short: string; color: string; valence?: number; arousal?: number; description: string }
> = {
  interpersonal_devotion: {
    label: 'Connection & Devotion',
    short: 'Connection',
    color: 'oklch(0.56 0.13 238)',
    valence: 0.6,
    arousal: -0.1,
    description: 'Romantic, familial, and friendly bonding.',
  },
  heartbreak_loss: {
    label: 'Heartbreak & Loss',
    short: 'Loss',
    color: 'oklch(0.58 0.17 28)',
    valence: -0.7,
    arousal: -0.2,
    description: 'Relational ending, mourning, and absence.',
  },
  adversity_resilience: {
    label: 'Resilience & Adversity',
    short: 'Resilience',
    color: 'oklch(0.55 0.15 286)',
    valence: 0.15,
    arousal: 0.25,
    description: 'Survival, endurance, and standing up through difficult weather.',
  },
  identity_autonomy: {
    label: 'Identity & Autonomy',
    short: 'Identity',
    color: 'oklch(0.68 0.15 74)',
    valence: 0.2,
    arousal: 0.05,
    description: 'Self-actualization, anti-conformity, and finding one’s raw truth.',
  },
  status_ambition: {
    label: 'Ambition & Status',
    short: 'Ambition',
    color: 'oklch(0.52 0.15 274)',
    valence: 0.25,
    arousal: 0.45,
    description: 'Competitive drive, material elevation, and victory.',
  },
  hedonism_escape: {
    label: 'Pleasure & Escapism',
    short: 'Escape',
    color: 'oklch(0.64 0.15 342)',
    valence: 0.4,
    arousal: 0.6,
    description: 'Sensory delight, party dynamics, drift, and urgent fun.',
  },
  place_heritage: {
    label: 'Place & Heritage',
    short: 'Place',
    color: 'oklch(0.64 0.14 136)',
    valence: 0.3,
    arousal: -0.05,
    description: 'Hometown roots, memory landmarks, and historical soil.',
  },
  existentialism_spirituality: {
    label: 'Meaning & Spirituality',
    short: 'Meaning',
    color: 'oklch(0.59 0.15 312)',
    valence: -0.05,
    arousal: -0.15,
    description: 'Mortality, faith, cosmic scale, and searching for answers.',
  },
};

export function categoryLabel(category: EmotionCategory | ThemeCategory): string {
  if (category in EMOTIONS) return EMOTIONS[category as EmotionCategory].label;
  return THEMES[category as ThemeCategory].label;
}

export function categoryColor(category: EmotionCategory | ThemeCategory): string {
  if (category in EMOTIONS) return EMOTIONS[category as EmotionCategory].color;
  return THEMES[category as ThemeCategory].color;
}
