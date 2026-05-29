export interface ProfileInfo {
  name: string;
  reportCount: number;
  latestReportAt: string | null; // ISO-ish timestamp from filename, e.g. "20261129T004730"
}

export type EmotionCategory =
  | 'joyful_activation'
  | 'triumphant_power'
  | 'peacefulness'
  | 'tenderness'
  | 'nostalgia_longing'
  | 'sadness_melancholy'
  | 'tension_anxiety'
  | 'anger_defiance';

export type ThemeCategory =
  | 'interpersonal_devotion'
  | 'heartbreak_loss'
  | 'adversity_resilience'
  | 'identity_autonomy'
  | 'status_ambition'
  | 'hedonism_escape'
  | 'place_heritage'
  | 'existentialism_spirituality';

export type Axis = 'emotion' | 'theme';
export type DepthLabel = 'surface' | 'engaged' | 'immersive';
export type PrevalenceLabel = 'dominant' | 'high' | 'moderate' | 'present' | 'not represented';

export interface PrevalenceItem {
  category: EmotionCategory | ThemeCategory;
  prevalence: PrevalenceLabel;
}

export interface WindowScores {
  emotion: Partial<Record<EmotionCategory, number>>;
  theme: Partial<Record<ThemeCategory, number>>;
  top_emotions: PrevalenceItem[];
  top_themes: PrevalenceItem[];
  depth_label: DepthLabel;
  top_artists: Array<{ artist: string; weight: number }>;
  top_tracks: Track[];
  top_frequency_tracks: Track[];
  from_date?: string; // ISO date string e.g. "2026-03-01"
  to_date?: string;   // ISO date string e.g. "2026-05-29"
  coverage?: WindowCoverage;
}

export interface WindowCoverage {
  scored_plays: number;
  total_plays: number;
  ratio: number; // scored_plays / total_plays, in [0, 1]
}

export interface Track {
  uri: string;
  name?: string;
  artist?: string;
  album?: string;
  weight?: number;
  emotion_scores?: Partial<Record<EmotionCategory, number>>;
  theme_scores?: Partial<Record<ThemeCategory, number>>;
  depth_score?: number;
  depth_label?: DepthLabel;
  play_count?: number;
  qualified_play_count?: number;
  last_played?: string;
  frequency_window_days?: number;
}

export interface Shift {
  category: EmotionCategory | ThemeCategory;
  axis: Axis;
  direction: 'elevated' | 'faded';
  delta: number;
  narrative: string;
}

export interface TrendEvent {
  category: EmotionCategory | ThemeCategory;
  axis: Axis;
  direction: 'rising' | 'falling' | 'spiking' | 'declining';
  magnitude: 'minor' | 'notable';
  narrative: string;
}

export interface ClusterSummary {
  label: string;
  centroid_avd: [number, number, number];
  dominant_emotions: Array<{ category: EmotionCategory; weight: number }>;
  dominant_themes: Array<{ category: ThemeCategory; weight: number }>;
  share_of_listening?: string;
  track_count: number;
  tracks?: Track[];
}

export interface CoOccurrence {
  pair: [EmotionCategory, ThemeCategory];
  strength: 'strong' | 'moderate';
  observed: number;
  expected: number;
  narrative: string;
  emotion: EmotionCategory;
  theme: ThemeCategory;
}

export interface SafetyFlag {
  flag_type: 'rumination_alert' | 'potential_rumination' | 'other';
  severity: 'warning' | 'caution' | 'info';
  message: string;
  recommendation?: string;
  triggered_at?: string;
}

export interface NarrativeSummary {
  headline: string;
  key_insights: string[];
  caveats?: string[];
}

export interface OrpheusReport {
  metadata: {
    generated_at: string;
    model_version: string;
    schema_version: string;
    note?: string;
  };
  state: WindowScores;
  trait: WindowScores;
  shifts: Shift[];
  trends: TrendEvent[];
  clusters: ClusterSummary[];
  clusters_status?: 'ok' | 'no_audio_features' | 'insufficient_audio_data' | 'no_clusters_found' | string;
  co_occurrences: CoOccurrence[];
  safety_flags: SafetyFlag[];
  narrative?: NarrativeSummary;
}
