// Corner RGB anchors: [r, g, b]
export const MOOD_CORNERS = {
  TL: [255, 71, 71],   // high arousal, negative valence — Red
  TR: [255, 204, 0],   // high arousal, positive valence — Yellow
  BL: [59, 130, 246],  // low arousal, negative valence — Blue
  BR: [74, 222, 128],  // low arousal, positive valence — Green
} as const;

export function moodColorRGBA(valence: number, arousal: number, alpha = 0.18) {
  // Normalize from [-1,1] to [0,1]
  const x = Math.max(0, Math.min(1, (valence + 1) / 2));
  const y = Math.max(0, Math.min(1, (arousal + 1) / 2));

  const { TL, TR, BL, BR } = MOOD_CORNERS;

  // Bilinear interpolation
  const wTL = (1 - x) * y;
  const wTR = x * y;
  const wBL = (1 - x) * (1 - y);
  const wBR = x * (1 - y);

  const r = Math.round(wTL * TL[0] + wTR * TR[0] + wBL * BL[0] + wBR * BR[0]);
  const g = Math.round(wTL * TL[1] + wTR * TR[1] + wBL * BL[1] + wBR * BR[1]);
  const b = Math.round(wTL * TL[2] + wTR * TR[2] + wBL * BL[2] + wBR * BR[2]);

  // Relative luminance (sRGB). Text uses tinted ink/paper to match the design system.
  const rl = 0.2126 * (r / 255) + 0.7152 * (g / 255) + 0.0722 * (b / 255);
  const text = rl < 0.45 ? 'oklch(0.982 0.007 116 / 0.93)' : 'oklch(0.245 0.025 142 / 0.88)';

  const bg = `rgba(${r}, ${g}, ${b}, ${alpha})`;
  const border = `rgba(${r}, ${g}, ${b}, ${Math.min(0.9, alpha + 0.12)})`;
  const solid = `rgb(${r}, ${g}, ${b})`;

  return { background: bg, border, color: text, solid };
}
