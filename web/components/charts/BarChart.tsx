"use client";

export interface Bar {
  label: string;
  value: number;
  highlight?: boolean;
  sub?: string;
}

interface Props {
  bars: Bar[];
  height?: number;
  yFormat?: (v: number) => string;
  ariaLabel?: string;
}

const W = 820;
const PAD = { t: 18, r: 16, b: 42, l: 52 };

/* Monochrome bars. Sign is read from direction across a zero baseline:
   positive = solid ink fill, negative = hollow (outlined). The selected
   bar is full-opacity ink; others are dimmed. No colour status coding. */
export default function BarChart({ bars, height = 220, yFormat = (v) => v.toFixed(0), ariaLabel }: Props) {
  const H = height;
  const innerW = W - PAD.l - PAD.r;
  const innerH = H - PAD.t - PAD.b;
  const vals = bars.map((b) => b.value);
  let lo = Math.min(0, ...vals), hi = Math.max(0, ...vals);
  if (!isFinite(lo) || !isFinite(hi)) { lo = 0; hi = 1; }
  const span = hi - lo || 1;
  hi += span * 0.14; if (lo < 0) lo -= span * 0.1;

  const y = (v: number) => PAD.t + innerH - ((v - lo) / (hi - lo)) * innerH;
  const zeroY = y(0);
  const n = bars.length;
  const slot = innerW / n;
  const bw = Math.min(58, slot * 0.5);

  const ticks = 4;
  const tickVals = Array.from({ length: ticks + 1 }, (_, k) => lo + ((hi - lo) * k) / ticks);

  return (
    <svg viewBox={`0 0 ${W} ${H}`} width="100%" className="chart-svg" role="img" aria-label={ariaLabel ?? "Bar chart"}>
      {tickVals.map((tv, k) => (
        <g key={k}>
          <line x1={PAD.l} x2={W - PAD.r} y1={y(tv)} y2={y(tv)} stroke="rgba(236,234,230,0.07)" strokeWidth="1" />
          <text x={PAD.l - 9} y={y(tv) + 4} textAnchor="end" className="ax">{yFormat(tv)}</text>
        </g>
      ))}
      <line x1={PAD.l} x2={W - PAD.r} y1={zeroY} y2={zeroY} stroke="rgba(236,234,230,0.34)" strokeWidth="1" />

      {bars.map((b, i) => {
        const cx = PAD.l + slot * i + slot / 2;
        const top = Math.min(y(b.value), zeroY);
        const h = Math.max(1, Math.abs(y(b.value) - zeroY));
        const positive = b.value >= 0;
        const op = b.highlight ? 1 : 0.5;
        return (
          <g key={i}>
            {positive ? (
              <rect x={cx - bw / 2} y={top} width={bw} height={h} fill="var(--ink)" opacity={op}
                    stroke={b.highlight ? "var(--ink)" : "none"} />
            ) : (
              <rect x={cx - bw / 2} y={top} width={bw} height={h} fill="none"
                    stroke="var(--ink)" strokeWidth="1.4" opacity={Math.max(op, 0.6)} />
            )}
            {b.highlight && (
              <rect x={cx - bw / 2} y={positive ? top - 3 : top + h + 1} width={bw} height="2" fill="var(--ink)" />
            )}
            <text x={cx} y={positive ? top - 7 : top + h + 14} textAnchor="middle"
                  className="ax" style={{ fontSize: 11, fill: b.highlight ? "var(--ink)" : "var(--ink-3)" }}>
              {yFormat(b.value)}
            </text>
            <text x={cx} y={H - 22} textAnchor="middle" className="ax"
                  style={{ fontSize: 11, fill: b.highlight ? "var(--ink)" : "var(--ink-3)" }}>{b.label}</text>
            {b.sub && (
              <text x={cx} y={H - 9} textAnchor="middle" className="ax-faint" style={{ fontSize: 9.5 }}>{b.sub}</text>
            )}
          </g>
        );
      })}
    </svg>
  );
}
