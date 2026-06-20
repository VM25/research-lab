"use client";

export interface Series {
  name: string;
  values: (number | null)[];
  color?: string;       // CSS var; defaults to --ink
  dash?: string;        // stroke-dasharray, e.g. "4 3"
  width?: number;
  label?: boolean;      // draw an end-of-line label
}

interface Props {
  dates: string[];          // "YYYY-MM"
  series: Series[];
  height?: number;
  yFormat?: (v: number) => string;
  baselineZero?: boolean;
  ariaLabel?: string;
}

const W = 820;
const PAD = { t: 14, r: 20, b: 30, l: 56 };

export default function LineChart({
  dates, series, height = 320, yFormat = (v) => v.toFixed(0),
  baselineZero = false, ariaLabel,
}: Props) {
  const H = height;
  const innerW = W - PAD.l - PAD.r;
  const innerH = H - PAD.t - PAD.b;
  const n = dates.length;

  const all = series.flatMap((s) => s.values.filter((v): v is number => v !== null));
  let lo = Math.min(...all), hi = Math.max(...all);
  if (baselineZero) { lo = Math.min(lo, 0); hi = Math.max(hi, 0); }
  if (!isFinite(lo) || !isFinite(hi)) { lo = 0; hi = 1; }
  const span = hi - lo || 1;
  lo -= span * 0.06; hi += span * 0.06;

  const x = (i: number) => PAD.l + (n <= 1 ? 0 : (i / (n - 1)) * innerW);
  const y = (v: number) => PAD.t + innerH - ((v - lo) / (hi - lo)) * innerH;

  const ticks = 5;
  const tickVals = Array.from({ length: ticks + 1 }, (_, k) => lo + ((hi - lo) * k) / ticks);

  const yearIdx: { i: number; label: string }[] = [];
  let lastYear = "";
  dates.forEach((d, i) => {
    const yr = d.slice(0, 4);
    if (yr !== lastYear && Number(yr) % 3 === 0) { yearIdx.push({ i, label: yr }); lastYear = yr; }
  });

  const pathFor = (vals: (number | null)[]) => {
    let d = ""; let pen = false;
    vals.forEach((v, i) => {
      if (v === null) { pen = false; return; }
      d += `${pen ? "L" : "M"}${x(i).toFixed(1)} ${y(v).toFixed(1)} `; pen = true;
    });
    return d.trim();
  };

  const lastReal = (vals: (number | null)[]) => {
    for (let i = vals.length - 1; i >= 0; i--) if (vals[i] !== null) return i;
    return -1;
  };

  return (
    <svg viewBox={`0 0 ${W} ${H}`} width="100%" className="chart-svg" role="img"
         aria-label={ariaLabel ?? "Line chart"} style={{ overflow: "visible" }}>
      {/* gridlines + y axis */}
      {tickVals.map((tv, k) => (
        <g key={k}>
          <line x1={PAD.l} x2={W - PAD.r} y1={y(tv)} y2={y(tv)}
                stroke="rgba(236,234,230,0.07)" strokeWidth="1" />
          <text x={PAD.l - 10} y={y(tv) + 4} textAnchor="end" className="ax">{yFormat(tv)}</text>
        </g>
      ))}
      {/* axes frame */}
      <line x1={PAD.l} x2={PAD.l} y1={PAD.t} y2={PAD.t + innerH} stroke="rgba(236,234,230,0.22)" strokeWidth="1" />
      <line x1={PAD.l} x2={W - PAD.r} y1={PAD.t + innerH} y2={PAD.t + innerH} stroke="rgba(236,234,230,0.22)" strokeWidth="1" />
      {baselineZero && (
        <line x1={PAD.l} x2={W - PAD.r} y1={y(0)} y2={y(0)} stroke="rgba(236,234,230,0.34)" strokeWidth="1" />
      )}

      {/* x year labels with ticks */}
      {yearIdx.map((yr, k) => (
        <g key={k}>
          <line x1={x(yr.i)} x2={x(yr.i)} y1={PAD.t + innerH} y2={PAD.t + innerH + 4} stroke="rgba(236,234,230,0.22)" strokeWidth="1" />
          <text x={x(yr.i)} y={H - 8} textAnchor="middle" className="ax">{yr.label}</text>
        </g>
      ))}

      {/* lines (secondary first so primary sits on top) */}
      {series.map((s, k) => (
        <path key={k} d={pathFor(s.values)} fill="none"
              stroke={s.color ?? "var(--ink)"} strokeWidth={s.width ?? 2}
              strokeLinejoin="round" strokeLinecap="round" strokeDasharray={s.dash} />
      ))}

      {/* end-of-line markers for labelled series */}
      {series.map((s, k) => {
        if (!s.label) return null;
        const i = lastReal(s.values);
        if (i < 0) return null;
        const vy = y(s.values[i] as number);
        return <circle key={`m${k}`} cx={x(i)} cy={vy} r="2.6" fill={s.color ?? "var(--ink)"} />;
      })}
    </svg>
  );
}
