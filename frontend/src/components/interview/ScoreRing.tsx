"use client";
import { motion } from "framer-motion";

interface Props {
  value: number;
  max?: number;
  size?: number;
  stroke?: number;
}

export function ScoreRing({ value, max = 10, size = 180, stroke = 14 }: Props) {
  const pct = Math.max(0, Math.min(1, value / max));
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - pct);

  const color =
    pct >= 0.75 ? "stroke-green-500"
      : pct >= 0.5 ? "stroke-brand-500"
      : pct >= 0.3 ? "stroke-amber-500"
      : "stroke-red-500";

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={stroke}
          className="text-slate-100"
        />
        <motion.circle
          cx={size / 2} cy={size / 2} r={radius}
          fill="none"
          strokeWidth={stroke}
          strokeLinecap="round"
          className={color}
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.2, ease: "easeOut" }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-4xl font-bold tabular-nums">{value.toFixed(1)}</span>
        <span className="text-xs text-slate-400">out of {max}</span>
      </div>
    </div>
  );
}
