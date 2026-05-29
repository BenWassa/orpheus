import { EMOTION_ORDER, EMOTIONS, THEME_ORDER, THEMES } from '../taxonomy';
import type {
  CoOccurrence,
  DepthLabel,
  EmotionCategory,
  NarrativeSummary,
  OrpheusReport,
  PrevalenceItem,
  PrevalenceLabel,
  SafetyFlag,
  ThemeCategory,
  WindowScores,
} from '../types';

type UnknownRecord = Record<string, unknown>;

const prevalenceWeights: Record<PrevalenceLabel, number> = {
  dominant: 0.45,
  high: 0.3,
  moderate: 0.15,
  present: 0.08,
  'not represented': 0.02,
};

function isRecord(value: unknown): value is UnknownRecord {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function asRecord(value: unknown): UnknownRecord {
  return isRecord(value) ? value : {};
}

function asString(value: unknown, fallback: string): string {
  return typeof value === 'string' && value.length > 0 ? value : fallback;
}

function asNumber(value: unknown, fallback = 0): number {
  return typeof value === 'number' && Number.isFinite(value) ? value : fallback;
}

function asDepthLabel(value: unknown): DepthLabel {
  return value === 'surface' || value === 'engaged' || value === 'immersive' ? value : 'engaged';
}

function asPrevalenceLabel(value: unknown): PrevalenceLabel {
  if (value === 'dominant' || value === 'high' || value === 'moderate' || value === 'present' || value === 'not represented') {
    return value;
  }
  return 'present';
}

function normalizePrevalenceItems(value: unknown): PrevalenceItem[] {
  if (!Array.isArray(value)) return [];
  return value.flatMap((item) => {
    const row = asRecord(item);
    const category = row.category;
    if (typeof category !== 'string') return [];
    if (!(category in EMOTIONS) && !(category in THEMES)) return [];
    return [{ category: category as EmotionCategory | ThemeCategory, prevalence: asPrevalenceLabel(row.prevalence) }];
  });
}

function normalizeScores<T extends string>(value: unknown, categories: readonly T[]): Partial<Record<T, number>> {
  const source = asRecord(value);
  return categories.reduce<Partial<Record<T, number>>>((acc, category) => {
    const score = source[category];
    if (typeof score === 'number' && Number.isFinite(score)) {
      acc[category] = Math.max(0, Math.min(1, score));
    }
    return acc;
  }, {});
}

function fillScoresFromTopItems<T extends EmotionCategory | ThemeCategory>(
  scores: Partial<Record<T, number>>,
  topItems: PrevalenceItem[],
  allowed: readonly T[],
): Partial<Record<T, number>> {
  if (Object.values(scores).some((score) => typeof score === 'number' && score > 0)) return scores;

  const allowedSet = new Set<string>(allowed);
  return topItems.reduce<Partial<Record<T, number>>>((acc, item) => {
    if (allowedSet.has(item.category)) acc[item.category as T] = prevalenceWeights[item.prevalence];
    return acc;
  }, {});
}

function normalizeWindow(value: unknown): WindowScores {
  const source = asRecord(value);
  const topEmotions = normalizePrevalenceItems(source.top_emotions);
  const topThemes = normalizePrevalenceItems(source.top_themes);

  return {
    emotion: fillScoresFromTopItems(normalizeScores(source.emotion, EMOTION_ORDER), topEmotions, EMOTION_ORDER),
    theme: fillScoresFromTopItems(normalizeScores(source.theme, THEME_ORDER), topThemes, THEME_ORDER),
    top_emotions: topEmotions,
    top_themes: topThemes,
    depth_label: asDepthLabel(source.depth_label),
    top_artists: Array.isArray(source.top_artists)
      ? source.top_artists.map((artist) => {
          const row = asRecord(artist);
          return { artist: asString(row.artist, 'Unknown artist'), weight: asNumber(row.weight) };
        })
      : [],
    top_tracks: Array.isArray(source.top_tracks)
      ? source.top_tracks.map((track, index) => {
          const row = asRecord(track);
          return {
            uri: asString(row.uri ?? row.track_uri, `track-${index}`),
            name: typeof row.name === 'string' ? row.name : undefined,
            artist: typeof row.artist === 'string' ? row.artist : undefined,
            album: typeof row.album === 'string' ? row.album : undefined,
            weight: typeof row.weight === 'number' ? row.weight : undefined,
            depth_score: typeof row.depth_score === 'number' ? row.depth_score : undefined,
            depth_label: asDepthLabel(row.depth_label),
            play_count: typeof row.play_count === 'number' ? row.play_count : undefined,
            emotion_scores: normalizeScores(row.emotion_scores, EMOTION_ORDER),
            theme_scores: normalizeScores(row.theme_scores, THEME_ORDER),
          };
        })
      : [],
  };
}

function normalizeSafetyFlag(item: unknown): SafetyFlag | null {
  const source = asRecord(item);
  const type = asString(source.flag_type ?? source.type, 'other');
  const severity = source.severity === 'warning' || source.severity === 'info' ? source.severity : 'caution';
  const message = asString(source.message ?? source.detail, '');

  if (!message) return null;

  return {
    flag_type: type === 'rumination_alert' || type === 'potential_rumination' ? type : 'other',
    severity,
    message,
    recommendation: typeof source.recommendation === 'string' ? source.recommendation : undefined,
    triggered_at: typeof source.triggered_at === 'string' ? source.triggered_at : undefined,
  };
}

function normalizeCoOccurrence(item: unknown): CoOccurrence | null {
  const source = asRecord(item);
  const pair = Array.isArray(source.pair) ? source.pair : [source.emotion, source.theme];
  const emotion = pair[0];
  const theme = pair[1];

  if (typeof emotion !== 'string' || !(emotion in EMOTIONS)) return null;
  if (typeof theme !== 'string' || !(theme in THEMES)) return null;

  return {
    pair: [emotion as EmotionCategory, theme as ThemeCategory],
    emotion: emotion as EmotionCategory,
    theme: theme as ThemeCategory,
    strength: source.strength === 'strong' ? 'strong' : 'moderate',
    observed: asNumber(source.observed),
    expected: asNumber(source.expected),
    narrative: asString(source.narrative, 'These categories appear together more often than expected.'),
  };
}

function composeNarrative(report: OrpheusReport): NarrativeSummary {
  const topEmotion = report.state.top_emotions[0]?.category;
  const topTheme = report.state.top_themes[0]?.category;
  const emotionLabel = topEmotion && topEmotion in EMOTIONS ? EMOTIONS[topEmotion as EmotionCategory].label : 'recent emotion';
  const themeLabel = topTheme && topTheme in THEMES ? THEMES[topTheme as ThemeCategory].label : 'life themes';

  const keyInsights = [
    ...report.shifts.map((shift) => shift.narrative),
    ...report.trends.map((trend) => trend.narrative),
    ...report.co_occurrences.map((pair) => pair.narrative),
  ].slice(0, 3);

  return {
    headline: `Your listening centers around ${emotionLabel} and ${themeLabel}.`,
    key_insights: keyInsights.length > 0 ? keyInsights : ['This report has enough structure to begin exploration.'],
    caveats: ['This summary is composed from the normalized backend report.'],
  };
}

export function parseOrpheusReport(input: unknown): OrpheusReport {
  const root = asRecord(input);
  const metadata = asRecord(root.metadata);
  const windows = asRecord(root.windows);
  const state = normalizeWindow(windows.state ?? root.state);
  const trait = normalizeWindow(windows.trait ?? root.trait);

  const report: OrpheusReport = {
    metadata: {
      generated_at: asString(root.generated_at ?? metadata.generated_at, new Date().toISOString()),
      model_version: asString(root.model_version ?? metadata.model_version, 'unknown-model'),
      schema_version: asString(metadata.schema_version, '1.0'),
      note: typeof metadata.note === 'string' ? metadata.note : undefined,
    },
    state,
    trait,
    shifts: Array.isArray(root.shifts) ? (root.shifts as OrpheusReport['shifts']) : [],
    trends: Array.isArray(root.trends) ? (root.trends as OrpheusReport['trends']) : [],
    clusters: Array.isArray(root.clusters) ? (root.clusters as OrpheusReport['clusters']) : [],
    clusters_status: typeof root.clusters_status === 'string' ? root.clusters_status : undefined,
    co_occurrences: Array.isArray(root.co_occurrences)
      ? root.co_occurrences.flatMap((item) => {
          const normalized = normalizeCoOccurrence(item);
          return normalized ? [normalized] : [];
        })
      : [],
    safety_flags: Array.isArray(root.safety_flags)
      ? root.safety_flags.flatMap((item) => {
          const normalized = normalizeSafetyFlag(item);
          return normalized ? [normalized] : [];
        })
      : [],
  };

  const narrative = root.narrative;
  const fallbackNarrative = composeNarrative(report);
  report.narrative = isRecord(narrative)
    ? {
        headline: asString(narrative.headline, fallbackNarrative.headline),
        key_insights: Array.isArray(narrative.key_insights)
          ? narrative.key_insights.filter((item): item is string => typeof item === 'string')
          : fallbackNarrative.key_insights,
        caveats: Array.isArray(narrative.caveats)
          ? narrative.caveats.filter((item): item is string => typeof item === 'string')
          : undefined,
      }
    : composeNarrative(report);

  return report;
}
