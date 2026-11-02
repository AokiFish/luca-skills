import React from "react";
import {interpolate, useCurrentFrame} from "remotion";

export const COLORS = {
  bg: "#f4f1e8",
  ink: "#1c2128",
  inkSoft: "#3b424a",
  muted: "#6b7280",
  green: "#2ea44f",
  greenSoft: "#3fb950",
  navy: "#0f1b2d",
  browser: "#eae6d9",
  border: "#d6d2c4",
  card: "#faf8f1",
};

const FONT_MONO =
  '"JetBrains Mono", "SF Mono", "Cascadia Code", Consolas, monospace';
const FONT_CN =
  '"PingFang SC", "Microsoft YaHei", "Noto Sans SC", system-ui, sans-serif';

/* ---------------- GitHub mark (simple octocat silhouette) ---------------- */
export const GitHubMark: React.FC<{size?: number; color?: string}> = ({
  size = 28,
  color = COLORS.ink,
}) => (
  <svg width={size} height={size} viewBox="0 0 16 16" fill={color}>
    <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.7-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8Z" />
  </svg>
);

/* ---------------- Edge pixel decoration ---------------- */
const PIXELS: {side: "L" | "R"; y: number; size: number; a: number}[] = [
  {side: "L", y: 180, size: 26, a: 0.55},
  {side: "L", y: 240, size: 18, a: 0.35},
  {side: "L", y: 310, size: 22, a: 0.5},
  {side: "L", y: 400, size: 14, a: 0.3},
  {side: "L", y: 520, size: 20, a: 0.45},
  {side: "L", y: 640, size: 16, a: 0.3},
  {side: "L", y: 780, size: 24, a: 0.5},
  {side: "L", y: 920, size: 14, a: 0.25},
  {side: "L", y: 1080, size: 20, a: 0.4},
  {side: "L", y: 1240, size: 16, a: 0.3},
  {side: "L", y: 1400, size: 22, a: 0.45},
  {side: "L", y: 1560, size: 14, a: 0.25},
  {side: "L", y: 1700, size: 18, a: 0.35},
  {side: "R", y: 200, size: 20, a: 0.45},
  {side: "R", y: 280, size: 16, a: 0.3},
  {side: "R", y: 380, size: 24, a: 0.55},
  {side: "R", y: 500, size: 14, a: 0.25},
  {side: "R", y: 660, size: 20, a: 0.4},
  {side: "R", y: 820, size: 16, a: 0.3},
  {side: "R", y: 980, size: 22, a: 0.5},
  {side: "R", y: 1140, size: 14, a: 0.25},
  {side: "R", y: 1300, size: 18, a: 0.35},
  {side: "R", y: 1460, size: 22, a: 0.5},
  {side: "R", y: 1620, size: 16, a: 0.3},
  {side: "R", y: 1760, size: 20, a: 0.4},
];

export const PixelFrame: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <>
      {PIXELS.map((p, i) => {
        const tw = interpolate((frame + i * 7) % 90, [0, 45, 90], [p.a * 0.4, p.a, p.a * 0.4]);
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              top: p.y,
              [p.side === "L" ? "left" : "right"]: 18,
              width: p.size,
              height: p.size,
              backgroundColor: COLORS.greenSoft,
              opacity: tw,
              borderRadius: 3,
            }}
          />
        );
      })}
    </>
  );
};

/* ---------------- Top browser bar ---------------- */
export const BrowserBar: React.FC<{
  tabTitle: string;
  index?: number;
  total?: number;
  weekStarsLabel?: string;
}> = ({tabTitle, index, total, weekStarsLabel}) => {
  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        right: 0,
        height: 120,
        display: "flex",
        alignItems: "center",
        padding: "0 28px",
        gap: 16,
        backgroundColor: COLORS.bg,
        zIndex: 10,
      }}
    >
      <div style={{display: "flex", gap: 10}}>
        <span style={{width: 22, height: 22, borderRadius: "50%", backgroundColor: "#e05a4e"}} />
        <span style={{width: 22, height: 22, borderRadius: "50%", backgroundColor: "#e8b93c"}} />
        <span style={{width: 22, height: 22, borderRadius: "50%", backgroundColor: "#4caf50"}} />
      </div>
      <div
        style={{
          flex: 1,
          height: 80,
          backgroundColor: COLORS.browser,
          borderRadius: "16px 16px 0 0",
          display: "flex",
          alignItems: "center",
          gap: 12,
          padding: "0 24px",
          maxWidth: 560,
        }}
      >
        <GitHubMark size={26} />
        <span style={{fontSize: 28, fontWeight: 600, color: COLORS.ink, fontFamily: FONT_CN}}>
          {tabTitle}
        </span>
      </div>
      {index !== undefined && total !== undefined && (
        <div
          style={{
            backgroundColor: COLORS.navy,
            color: "#fff",
            padding: "10px 20px",
            borderRadius: 12,
            fontSize: 26,
            fontWeight: 700,
            fontFamily: FONT_MONO,
          }}
        >
          {String(index).padStart(2, "0")} / {String(total).padStart(2, "0")}
        </div>
      )}
      {weekStarsLabel && (
        <div
          style={{
            backgroundColor: COLORS.green,
            color: "#fff",
            padding: "10px 18px",
            borderRadius: 12,
            fontSize: 24,
            fontWeight: 700,
            fontFamily: FONT_MONO,
          }}
        >
          ★ {weekStarsLabel}
        </div>
      )}
    </div>
  );
};

/* ---------------- Bottom watermark bar ---------------- */
export const WatermarkBar: React.FC = () => (
  <div
    style={{
      position: "absolute",
      bottom: 0,
      left: 0,
      right: 0,
      height: 220,
      backgroundColor: COLORS.navy,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      gap: 14,
    }}
  >
    <span style={{color: COLORS.greenSoft, fontSize: 44, fontWeight: 700, fontFamily: FONT_MONO}}>
      &gt;
    </span>
    <span style={{color: "#fff", fontSize: 44, fontWeight: 700, fontFamily: FONT_MONO}}>
      Github Weekly
    </span>
  </div>
);

/* ---------------- Bottom subtitle capsule ---------------- */
export const SubtitleBar: React.FC<{text: string}> = ({text}) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 8], [0, 1], {extrapolateRight: "clamp"});
  return (
    <div
      style={{
        position: "absolute",
        bottom: 260,
        left: 60,
        right: 60,
        display: "flex",
        justifyContent: "center",
        opacity,
      }}
    >
      <div
        style={{
          backgroundColor: COLORS.navy,
          color: "#fff",
          padding: "22px 40px",
          borderRadius: 999,
          fontSize: 38,
          fontWeight: 600,
          fontFamily: FONT_CN,
          textAlign: "center",
          lineHeight: 1.4,
          maxWidth: 960,
        }}
      >
        {text}
      </div>
    </div>
  );
};

/* ---------------- Green star badge ---------------- */
export const StarBadge: React.FC<{label: string; big?: boolean}> = ({label, big}) => (
  <div
    style={{
      backgroundColor: COLORS.green,
      color: "#fff",
      padding: big ? "14px 26px" : "10px 18px",
      borderRadius: 12,
      fontSize: big ? 32 : 26,
      fontWeight: 700,
      fontFamily: FONT_MONO,
      display: "inline-flex",
      alignItems: "center",
      gap: 8,
    }}
  >
    <span>★</span>
    <span>{label}</span>
    <span>★</span>
  </div>
);

/* ---------------- Number pill (#01) ---------------- */
export const RankPill: React.FC<{n: number}> = ({n}) => (
  <div
    style={{
      backgroundColor: COLORS.navy,
      color: "#fff",
      padding: "10px 22px",
      borderRadius: 12,
      fontSize: 30,
      fontWeight: 800,
      fontFamily: FONT_MONO,
    }}
  >
    #{String(n).padStart(2, "0")}
  </div>
);
