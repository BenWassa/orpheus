export function moodColorRGBA(valence: number, arousal: number, alpha = 0.18) {
  // Normalize from [-1,1] to [0,1]
  const x = Math.max(0, Math.min(1, (valence + 1) / 2));
  const y = Math.max(0, Math.min(1, (arousal + 1) / 2));

  // Corner colors (user-provided RGBA), as [r,g,b,a]
  const TL = [255, 71, 71, 0.7]; // high energy negative (Red) top-left
  const TR = [255, 204, 0, 0.7]; // high energy positive (Yellow) top-right
  const BL = [59, 130, 246, 0.7]; // low energy negative (Blue) bottom-left
  const BR = [74, 222, 128, 0.7]; // low energy positive (Green) bottom-right

  // Bilinear interpolation weights
  const wTL = (1 - x) * y;
  const wTR = x * y;
  const wBL = (1 - x) * (1 - y);
  const wBR = x * (1 - y);

  const r = Math.round(wTL * TL[0] + wTR * TR[0] + wBL * BL[0] + wBR * BR[0]);
  const g = Math.round(wTL * TL[1] + wTR * TR[1] + wBL * BL[1] + wBR * BR[1]);
  const b = Math.round(wTL * TL[2] + wTR * TR[2] + wBL * BL[2] + wBR * BR[2]);

  // Compute readable text color based on luminance (sRGB)
  const sr = r / 255;
  const sg = g / 255;
  const sb = b / 255;
  const lum = 0.2126 * sr + 0.7152 * sg + 0.0722 * sb;
  const text = lum < 0.5 ? 'rgba(255,255,255,0.95)' : 'rgba(6,6,6,0.9)';

  const bg = `rgba(${r}, ${g}, ${b}, ${alpha})`;
  const border = `rgba(${r}, ${g}, ${b}, ${Math.min(0.9, alpha + 0.12)})`;

  return { background: bg, border, color: text };
}
