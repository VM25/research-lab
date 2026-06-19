"use client";

import { useId } from "react";

export interface Series {
  name: string;
  color: string;
  values: (number | null)[];
  dashed?: boolean;
  fill?: boolean;
  width?: number;
}

interface Props {
  dates: string[];          // "YYYY-MM"
  series: Series[];
  height?: number;
  yFormat?: (v: number) => string;
  baselineZero?: boolean;   // include 0 in the y-domain (for drawdowns / returns)
  ariaLabel?: string;
}

const W = 760;
const PAD = { t: 16, r: 18, b: 28, l: 46 };

export default function LineChart({
  dates, series, height = 300, yFormat = (v) => v.toFixed(0),
  baselineZero = false, ariaLabel,
}: Props) {
  const uid = useId().replace(/[:]/g, "");
  const H = height;
  const innerW = W - PAD.l - PAD.r;
  const innerH = H - PAD.t - PAD.b;
  const n = dates.length;

  const allVals = series.flatMap((s) => s.values.filter((v): v is number => v !== null));
  let lo = Math.min(...allVals);
  let hi = Math.max(...allVals);
  if (baselineZero) { lo = Math.min(lo, 0); hi = Math.max(hi, 0); }
  if (!isFinite(lo) || !isFinite(hi)) { lo = 0; hi = 1; }
  const span = hi - lo || 1;
  lo -= span * 0.06; hi += span * 0.06;

  const x = (i: number) => PAD.l + (n <= 1 ? 0 : (i / (n - 1)) * innerW);
  const y = (v: number) => PAD.t + innerH - ((v - lo) / (hi - lo)) * innerH;

  // y ticks (nice-ish)
  const ticks = 4;
  const tickVals = Array.from({ length: ticks + 1 }, (_, k) => lo + ((hi - lo) * k) / ticks);

  // x year labels
  const yearIdx: { i: number; label: string }[] = [];
  let lastYear = "";
  dates.forEach((d, i) => {
    const yr = d.slice(0, 4);
    if (yr !== lastYear && (i === 0 || Number(yr) % 3 === 0)) {
      yearIdx.push({ i, label: yr });
      lastYear = yr;
    }
  });

  const pathFor = (vals: (number | null)[]) => {
    let d = "";
    let pen = false;
    vals.forEach((v, i) => {
      if (v === null) { pen = false; return; }
      d += `${pen ? "L" : "M"}${x(i).toFixed(1)} ${y(v).toFixed(1)} `;
      pen = true;
    });
    return d.trim();
  };

  const areaFor = (vals: (number | null)[]) => {
    const base = y(baselineZero ? 0 : lo);
    let d = "";
    let startI = -1; let pen = false;
    vals.forEach((v, i) => {
      if (v === null) { pen = false; return; }
      if (!pen) { startI = i; d += `M${x(i).toFixed(1)} ${base.toFixed(1)} L${x(i).toFixed(1)} ${y(v).toFixed(1)} `; }
      else d += `L${x(i).toFixed(1)} ${y(v).toFixed(1)} `;
      pen = true;
    });
    if (startI >= 0) {
      const lastReal = [...vals].reverse().findIndex((v) => v !== null);
      const lastI = lastReal === -1 ? vals.length - 1 : vals.length - 1 - lastReal;
      d += `L${x(lastI).toFixed(1)} ${base.toFixed(1)} Z`;
    }
    return d;
  };

  return (
    <svg viewBox={`0 0 ${W} ${H}`} width="100%" role="img"
         aria-label={ariaLabel ?? "Line chart"} style={{ overflow: "visible" }}>
      <defs>
        {series.filter((s) => s.fill).map((s, k) => (
          <linearGradient key={k} id={`g-${uid}-${k}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={s.color} stopOpacity="0.22" />
            <stop offset="100%" stopColor={s.color} stopOpacity="0" />
          </linearGradient>
        ))}
      </defs>

      {/* gridlines + y labels */}
      {tickVals.map((tv, k) => (
        <g key={k}>
          <line x1={PAD.l} x2={W - PAD.r} y1={y(tv)} y2={y(tv)} stroke="var(--series-grid)" strokeWidth="1" />
          <text x={PAD.l - 8} y={y(tv) + 3} textAnchor="end" className="axis-label">{yFormat(tv)}</text>
        </g>
      ))}
      {baselineZero && (
        <line x1={PAD.l} x2={W - PAD.r} y1={y(0)} y2={y(0)} stroke="var(--line)" strokeWidth="1.5" />
      )}

      {/* x year labels */}
      {yearIdx.map((yr, k) => (
        <text key={k} x={x(yr.i)} y={H - 8} textAnchor="middle" className="axis-label">{yr.label}</text>
      ))}

      {/* area fills (behind lines) */}
      {series.map((s, k) => s.fill ? (
        <path key={`a-${k}`} d={areaFor(s.values)} fill={`url(#g-${uid}-${k})`} stroke="none" />
      ) : null)}

      {/* lines */}
      {series.map((s, k) => (
        <path key={`l-${k}`} d={pathFor(s.values)} fill="none" stroke={s.color}
              strokeWidth={s.width ?? 2.2} strokeLinejoin="round" strokeLinecap="round"
              strokeDasharray={s.dashed ? "5 5" : undefined} />
      ))}
    </svg>
  );
}
