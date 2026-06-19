"use client";

export interface Bar {
  label: string;
  value: number;
  color?: string;
  highlight?: boolean;
  sub?: string;
}

interface Props {
  bars: Bar[];
  height?: number;
  yFormat?: (v: number) => string;
  baselineZero?: boolean;
  ariaLabel?: string;
}

const W = 760;
const PAD = { t: 14, r: 14, b: 40, l: 46 };

export default function BarChart({
  bars, height = 240, yFormat = (v) => v.toFixed(0),
  baselineZero = true, ariaLabel,
}: Props) {
  const H = height;
  const innerW = W - PAD.l - PAD.r;
  const innerH = H - PAD.t - PAD.b;
  const vals = bars.map((b) => b.value);
  let lo = Math.min(...vals, baselineZero ? 0 : Math.min(...vals));
  let hi = Math.max(...vals, baselineZero ? 0 : Math.max(...vals));
  if (!isFinite(lo) || !isFinite(hi)) { lo = 0; hi = 1; }
  const span = hi - lo || 1;
  hi += span * 0.12; if (lo < 0) lo -= span * 0.08;

  const y = (v: number) => PAD.t + innerH - ((v - lo) / (hi - lo)) * innerH;
  const zeroY = y(0);
  const n = bars.length;
  const slot = innerW / n;
  const bw = Math.min(64, slot * 0.56);

  const ticks = 4;
  const tickVals = Array.from({ length: ticks + 1 }, (_, k) => lo + ((hi - lo) * k) / ticks);

  return (
    <svg viewBox={`0 0 ${W} ${H}`} width="100%" role="img" aria-label={ariaLabel ?? "Bar chart"}>
      {tickVals.map((tv, k) => (
        <g key={k}>
          <line x1={PAD.l} x2={W - PAD.r} y1={y(tv)} y2={y(tv)} stroke="var(--series-grid)" strokeWidth="1" />
          <text x={PAD.l - 8} y={y(tv) + 3} textAnchor="end" className="axis-label">{yFormat(tv)}</text>
        </g>
      ))}
      <line x1={PAD.l} x2={W - PAD.r} y1={zeroY} y2={zeroY} stroke="var(--line)" strokeWidth="1.5" />

      {bars.map((b, i) => {
        const cx = PAD.l + slot * i + slot / 2;
        const top = Math.min(y(b.value), zeroY);
        const h = Math.abs(y(b.value) - zeroY);
        const color = b.color ?? (b.value < 0 ? "var(--rejected)" : "var(--accent)");
        return (
          <g key={i}>
            <rect x={cx - bw / 2} y={top} width={bw} height={Math.max(1, h)}
                  rx="4" fill={color}
                  opacity={b.highlight ? 1 : 0.62}
                  stroke={b.highlight ? "var(--accent-bright)" : "none"}
                  strokeWidth={b.highlight ? 1.5 : 0} />
            <text x={cx} y={top - 6} textAnchor="middle" className="axis-label"
                  style={{ fill: "var(--text-mid)", fontSize: 11 }}>
              {yFormat(b.value)}
            </text>
            <text x={cx} y={H - 22} textAnchor="middle" className="axis-label"
                  style={{ fill: b.highlight ? "var(--text-hi)" : "var(--text-low)", fontSize: 11 }}>
              {b.label}
            </text>
            {b.sub && (
              <text x={cx} y={H - 9} textAnchor="middle" className="axis-label" style={{ fontSize: 9.5 }}>
                {b.sub}
              </text>
            )}
          </g>
        );
      })}
    </svg>
  );
}
