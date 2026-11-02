import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import {
  BrowserBar,
  COLORS,
  GitHubMark,
  PixelFrame,
  RankPill,
  SubtitleBar,
  WatermarkBar,
} from "./components/Chrome";
import {ProjectMockup} from "./components/Mockups";
import {
  formatStars,
  formatTotal,
  PROJECTS,
  WEEK_NEW_STARS,
  WEEK_SHORT,
  WEEK_WORD,
} from "./data";

const FONT_MONO =
  '"JetBrains Mono", "SF Mono", "Cascadia Code", Consolas, monospace';
const FONT_CN =
  '"PingFang SC", "Microsoft YaHei", "Noto Sans SC", system-ui, sans-serif';

/* 封面装饰：底部城市天际线（深绿剪影） */
const SKYLINE: {w: number; h: number; x: number; c: string}[] = [
  {x: 0, w: 90, h: 150, c: "#14522e"},
  {x: 80, w: 70, h: 230, c: "#1b6b3a"},
  {x: 160, w: 110, h: 120, c: "#124a28"},
  {x: 270, w: 80, h: 190, c: "#1b6b3a"},
  {x: 350, w: 120, h: 100, c: "#14522e"},
  {x: 470, w: 70, h: 260, c: "#1e7a42"},
  {x: 545, w: 110, h: 140, c: "#124a28"},
  {x: 655, w: 85, h: 210, c: "#1b6b3a"},
  {x: 740, w: 120, h: 110, c: "#14522e"},
  {x: 860, w: 75, h: 240, c: "#1b6b3a"},
  {x: 935, w: 110, h: 130, c: "#124a28"},
  {x: 1040, w: 60, h: 180, c: "#1b6b3a"},
];

/* 封面语言图标：菱形色块 */
const LangDot: React.FC<{color: string}> = ({color}) => (
  <svg width={40} height={40} viewBox="0 0 40 40">
    <rect x={20 - 13} y={20 - 13} width={26} height={26} rx={5}
      transform={`rotate(45 20 20)`} fill={color} />
  </svg>
);

/* ======================= 封面（首帧即成稿，仅氛围微动） ======================= */
export const CoverScene: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{backgroundColor: "#f6f3ea", fontFamily: FONT_CN, overflow: "hidden"}}>
      {/* 顶部周榜 pill */}
      <div
        style={{
          position: "absolute", top: 110, left: 0, right: 0,
          display: "flex", justifyContent: "center",
        }}
      >
        <div
          style={{
            backgroundColor: "#1e7a42", color: "#fff",
            padding: "14px 44px", borderRadius: 999,
            fontSize: 40, fontWeight: 800, letterSpacing: 2,
          }}
        >
          {WEEK_SHORT}
        </div>
      </div>

      {/* 主标题 */}
      <div style={{position: "absolute", top: 230, left: 0, right: 0, textAlign: "center"}}>
        <div style={{display: "flex", justifyContent: "center", alignItems: "center", gap: 18}}>
          <span style={{fontSize: 170, fontWeight: 900, color: "#111", letterSpacing: 2, lineHeight: 1.1}}>
            Github
          </span>
          <GitHubMark size={110} color="#111" />
        </div>
        <div style={{fontSize: 150, fontWeight: 900, color: "#111", lineHeight: 1.25, marginTop: 6}}>
          {WEEK_WORD}<span style={{color: "#1e7a42"}}>AI</span>热榜
        </div>
        {/* 绿色下划弧线 */}
        <svg width={560} height={40} viewBox="0 0 560 40" style={{marginTop: -8}}>
          <path d="M10 30 Q 280 -10 550 26" stroke="#1e7a42" strokeWidth={12} fill="none" strokeLinecap="round" />
        </svg>
        {/* TOP 5 pill */}
        <div style={{display: "flex", justifyContent: "center", marginTop: 26}}>
          <div style={{backgroundColor: "#1e7a42", color: "#fff", padding: "12px 56px", borderRadius: 16, fontSize: 54, fontWeight: 900, letterSpacing: 6}}>
            TOP 5
          </div>
        </div>
      </div>

      {/* 榜单行 */}
      <div style={{position: "absolute", top: 950, left: 90, right: 90, display: "flex", flexDirection: "column", gap: 34}}>
        {PROJECTS.map((p) => {
          const tw = 0.75 + 0.25 * Math.sin((frame + p.rank * 20) / 14);
          return (
            <div key={p.rank} style={{display: "flex", alignItems: "center", gap: 22}}>
              <div
                style={{
                  width: 64, height: 64, borderRadius: 14,
                  background: "linear-gradient(180deg,#27a55a,#176337)",
                  color: "#fff", fontSize: 34, fontWeight: 900,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  flexShrink: 0,
                }}
              >
                {p.rank}
              </div>
              <LangDot color={p.langColor} />
              <div style={{fontSize: 44, fontWeight: 800, color: "#111", fontFamily: FONT_MONO, flex: 1, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis"}}>
                {p.name}
              </div>
              <div style={{fontSize: 38, fontWeight: 800, color: "#e8842c", fontFamily: FONT_MONO, opacity: tw}}>
                ★ {formatStars(p.totalStars)}
              </div>
            </div>
          );
        })}
      </div>

      {/* 星星点缀 */}
      {[
        {x: 120, y: 300}, {x: 930, y: 260}, {x: 70, y: 820}, {x: 990, y: 860}, {x: 150, y: 1500},
      ].map((s, i) => (
        <span
          key={i}
          style={{
            position: "absolute", left: s.x, top: s.y,
            color: "#e8842c", fontSize: 34,
            opacity: 0.5 + 0.5 * Math.sin((frame + i * 25) / 16),
          }}
        >
          ✦
        </span>
      ))}

      {/* 底部天际线 + 两个小卡片 */}
      <div style={{position: "absolute", bottom: 0, left: 0, right: 0, height: 320}}>
        {SKYLINE.map((b, i) => (
          <div key={i} style={{position: "absolute", bottom: 0, left: b.x, width: b.w, height: b.h, backgroundColor: b.c, borderRadius: "6px 6px 0 0"}} />
        ))}
        {/* 终端小卡 */}
        <div style={{position: "absolute", bottom: 60, left: 90, width: 420, height: 210, backgroundColor: "#0d1117", borderRadius: 18, padding: 22, display: "flex", flexDirection: "column", gap: 14, border: "3px solid #14522e"}}>
          <div style={{display: "flex", gap: 8}}>
            <span style={{width: 12, height: 12, borderRadius: "50%", backgroundColor: "#e05a4e"}} />
            <span style={{width: 12, height: 12, borderRadius: "50%", backgroundColor: "#e8b93c"}} />
            <span style={{width: 12, height: 12, borderRadius: "50%", backgroundColor: "#4caf50"}} />
          </div>
          {[
            {w: "85%", c: "#3fb950"},
            {w: "70%", c: "#58a6ff"},
            {w: "55%", c: "#d29922"},
          ].map((l, i) => (
            <div key={i} style={{width: l.w, height: 14, borderRadius: 7, backgroundColor: l.c}} />
          ))}
        </div>
        {/* 图表小卡 */}
        <div style={{position: "absolute", bottom: 60, right: 90, width: 420, height: 210, backgroundColor: "#0d1117", borderRadius: 18, padding: 22, display: "flex", alignItems: "flex-end", gap: 12, border: "3px solid #14522e"}}>
          {[0.4, 0.7, 0.5, 0.9, 0.65, 1].map((h, i) => (
            <div key={i} style={{flex: 1, height: `${h * 100}%`, borderRadius: 6, backgroundColor: i === 3 ? "#e8842c" : "#27a55a"}} />
          ))}
        </div>
      </div>

      <SubtitleBar
        text={`${WEEK_WORD} GitHub 周榜出炉，${PROJECTS.length} 个项目一周狂揽 ${WEEK_NEW_STARS.toLocaleString("en-US")} 颗星。`}
      />
    </AbsoluteFill>
  );
};

/* 数字滚动 */
const CountUp: React.FC<{to: number; from?: number; start?: number; end?: number; suffix?: string}> = ({
  to, from = 0, start = 8, end = 55, suffix = "",
}) => {
  const frame = useCurrentFrame();
  const v = interpolate(frame, [start, end], [from, to], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <span>
      {Math.round(v).toLocaleString("en-US")}
      {suffix}
    </span>
  );
};

/* ========================= 项目大字过场 ========================= */
export const ProjectIntroScene: React.FC<{index: number}> = ({index}) => {
  const p = PROJECTS[index];
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const big = spring({frame, fps, config: {damping: 200, stiffness: 90}});
  const sub = spring({frame: frame - 12, fps, config: {damping: 200, stiffness: 90}});
  const barW = interpolate(frame, [30, 70], [0, (p.weekStars / PROJECTS[0].weekStars) * 100], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{backgroundColor: COLORS.bg, fontFamily: FONT_CN}}>
      <PixelFrame />
      <BrowserBar
        tabTitle={p.name}
        index={index + 1}
        total={PROJECTS.length}
        weekStarsLabel={formatStars(p.weekStars)}
      />

      <div style={{position: "absolute", top: 330, left: 80, right: 80}}>
        <div
          style={{
            fontSize: 250, fontWeight: 900, color: COLORS.navy,
            fontFamily: FONT_MONO, lineHeight: 1, opacity: big,
            transform: `scale(${interpolate(big, [0, 1], [0.6, 1])})`,
          }}
        >
          #{String(p.rank).padStart(2, "0")}
        </div>
        <div style={{marginTop: 22, display: "flex", alignItems: "baseline", gap: 18, opacity: sub}}>
          <span style={{fontSize: 64, fontWeight: 800, color: COLORS.ink, fontFamily: FONT_MONO}}>
            {p.name}
          </span>
          <span style={{fontSize: 26, color: p.langColor, fontWeight: 700}}>◆ {p.lang}</span>
        </div>
        <div style={{fontSize: 24, color: COLORS.muted, fontFamily: FONT_MONO, marginTop: 6, opacity: sub}}>
          {p.repo}
        </div>
        <div style={{marginTop: 26, fontSize: 60, fontWeight: 800, color: COLORS.ink, opacity: sub}}>
          {p.desc}
        </div>

        {/* 本周新增星 + 相对条 */}
        <div style={{marginTop: 36, opacity: sub}}>
          <div style={{display: "flex", alignItems: "baseline", gap: 14}}>
            <span style={{fontSize: 84, fontWeight: 900, color: COLORS.green, fontFamily: FONT_MONO}}>
              +<CountUp to={p.weekStars} />
            </span>
            <span style={{fontSize: 28, color: COLORS.muted}}>★ / 本周</span>
          </div>
          <div style={{marginTop: 18, height: 14, borderRadius: 7, backgroundColor: "#d8d4c4", overflow: "hidden", width: "86%"}}>
            <div style={{width: `${barW}%`, height: "100%", background: "linear-gradient(90deg,#2ea44f,#3fb950)"}} />
          </div>
          <div style={{marginTop: 10, fontSize: 20, color: COLORS.muted, fontFamily: FONT_MONO}}>
            占本周 Top5 增速第一名的 {Math.round((p.weekStars / PROJECTS[0].weekStars) * 100)}%
          </div>
        </div>

        <div style={{marginTop: 30, display: "flex", gap: 16, alignItems: "center", flexWrap: "wrap", opacity: sub}}>
          <div style={{padding: "12px 22px", borderRadius: 12, border: `1px solid ${COLORS.border}`, fontSize: 24, color: COLORS.inkSoft, fontFamily: FONT_MONO, backgroundColor: COLORS.card}}>
            总★ {formatTotal(p.totalStars)}
          </div>
          {p.tags.map((t) => (
            <div key={t} style={{padding: "12px 22px", borderRadius: 12, border: `1px solid ${COLORS.border}`, fontSize: 24, color: COLORS.inkSoft, backgroundColor: COLORS.card}}>
              {t}
            </div>
          ))}
        </div>
      </div>

      <SubtitleBar text={p.subtitleIntro} />
      <WatermarkBar />
    </AbsoluteFill>
  );
};

/* ========================= 项目详解 ========================= */
export const ProjectDetailScene: React.FC<{index: number}> = ({index}) => {
  const p = PROJECTS[index];
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = spring({frame, fps, config: {damping: 200, stiffness: 100}});
  const progress = interpolate(frame, [20, 300], [0, 100], {extrapolateRight: "clamp"});

  return (
    <AbsoluteFill style={{backgroundColor: COLORS.bg, fontFamily: FONT_CN}}>
      <PixelFrame />
      <BrowserBar
        tabTitle={p.name}
        index={index + 1}
        total={PROJECTS.length}
        weekStarsLabel={formatStars(p.weekStars)}
      />

      <div
        style={{
          position: "absolute", top: 150, left: 60, right: 60,
          opacity: enter, transform: `translateY(${(1 - enter) * 24}px)`,
        }}
      >
        <div style={{display: "flex", alignItems: "center", gap: 20}}>
          <RankPill n={p.rank} />
          <div style={{fontSize: 50, fontWeight: 800, color: COLORS.ink, fontFamily: FONT_MONO}}>
            {p.name}
          </div>
          <div style={{flex: 1}} />
          <div style={{fontSize: 26, color: p.langColor, fontWeight: 700}}>◆ {p.lang}</div>
        </div>
        <div style={{marginTop: 10, fontSize: 26, color: COLORS.inkSoft}}>
          <span style={{color: COLORS.green, fontWeight: 700}}>{p.desc}</span>
          <span style={{color: COLORS.muted}}>
            {"  "}·{"  "}总★ {formatTotal(p.totalStars)}{"  "}·{"  "}本周 +{formatStars(p.weekStars)}
          </span>
        </div>
      </div>

      {/* mockup 窗口 */}
      <div
        style={{
          position: "absolute", top: 380, left: 50, right: 50, height: 740,
          opacity: enter, transform: `translateY(${(1 - enter) * 30}px)`,
        }}
      >
        <ProjectMockup kind={p.mockup} />
      </div>

      {/* 三大看点，逐条入场 */}
      <div style={{position: "absolute", top: 1160, left: 70, right: 70, display: "flex", flexDirection: "column", gap: 16}}>
        {p.points.map((pt, i) => {
          const o = interpolate(frame, [60 + i * 30, 78 + i * 30], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          return (
            <div
              key={i}
              style={{
                opacity: o,
                transform: `translateX(${(1 - o) * -30}px)`,
                display: "flex",
                alignItems: "center",
                gap: 16,
                backgroundColor: COLORS.card,
                border: `1px solid ${COLORS.border}`,
                borderRadius: 14,
                padding: "14px 22px",
              }}
            >
              <div
                style={{
                  width: 40, height: 40, borderRadius: "50%", flexShrink: 0,
                  backgroundColor: COLORS.green, color: "#fff",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: 22, fontWeight: 900,
                }}
              >
                {i + 1}
              </div>
              <div style={{fontSize: 28, color: COLORS.ink, fontWeight: 600}}>{pt}</div>
            </div>
          );
        })}
      </div>

      {/* 进度 + url */}
      <div style={{position: "absolute", bottom: 480, left: 60, right: 60, display: "flex", alignItems: "center", gap: 20}}>
        <div style={{flex: 1, height: 10, backgroundColor: "#d8d4c4", borderRadius: 5, overflow: "hidden"}}>
          <div style={{width: `${progress}%`, height: "100%", backgroundColor: COLORS.green}} />
        </div>
        <div style={{fontSize: 24, color: COLORS.navy, fontFamily: FONT_MONO, fontWeight: 600}}>
          {p.url}
        </div>
      </div>

      <SubtitleBar text={p.subtitleDetail} />
      <WatermarkBar />
    </AbsoluteFill>
  );
};

/* ============================= OUTRO ============================= */
export const OutroScene: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = spring({frame, fps, config: {damping: 200, stiffness: 90}});

  return (
    <AbsoluteFill style={{backgroundColor: COLORS.bg, fontFamily: FONT_CN}}>
      <PixelFrame />
      <BrowserBar tabTitle="Github Trending 周榜" />

      <div
        style={{
          position: "absolute", top: 250, left: 60, right: 60, textAlign: "center",
          opacity: enter, transform: `translateY(${(1 - enter) * 30}px)`,
        }}
      >
        <div style={{fontSize: 70, fontWeight: 800, color: COLORS.ink}}>
          {WEEK_WORD} {PROJECTS.length} 个开源信号
        </div>
        <div style={{marginTop: 18, fontSize: 32, color: COLORS.green, fontFamily: FONT_MONO, fontWeight: 600}}>
          {PROJECTS.length} repos · <CountUp to={WEEK_NEW_STARS} start={20} end={80} /> new stars
        </div>
      </div>

      {/* 汇总卡 */}
      <div
        style={{
          position: "absolute", top: 540, left: 60, right: 60,
          borderRadius: 24, border: `1px solid ${COLORS.border}`,
          backgroundColor: COLORS.card, opacity: enter,
          display: "flex", flexDirection: "column", padding: 40, gap: 18,
        }}
      >
        {PROJECTS.map((p, i) => {
          const delay = i * 8;
          const o = interpolate(frame, [20 + delay, 40 + delay], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          return (
            <div
              key={p.rank}
              style={{
                display: "flex", alignItems: "center", gap: 16, opacity: o,
                transform: `translateX(${(1 - o) * -20}px)`,
                padding: "14px 0", borderBottom: `1px solid ${COLORS.border}`,
              }}
            >
              <div style={{width: 52, height: 52, borderRadius: 12, backgroundColor: COLORS.navy, color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 800, fontFamily: FONT_MONO, fontSize: 22, flexShrink: 0}}>
                {p.rank}
              </div>
              <div style={{fontSize: 28, fontWeight: 700, color: COLORS.ink, fontFamily: FONT_MONO}}>
                {p.name}
              </div>
              <div style={{flex: 1, fontSize: 23, color: COLORS.muted}}>{p.desc}</div>
              <div style={{fontSize: 26, color: COLORS.green, fontWeight: 700, fontFamily: FONT_MONO}}>
                +{formatStars(p.weekStars)}
              </div>
            </div>
          );
        })}
      </div>

      {/* 关注引导 */}
      <div
        style={{
          position: "absolute", top: 1250, left: 60, right: 60,
          display: "flex", justifyContent: "center",
          opacity: interpolate(frame, [70, 90], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"}),
        }}
      >
        <div style={{backgroundColor: COLORS.green, color: "#fff", padding: "20px 48px", borderRadius: 999, fontSize: 36, fontWeight: 800}}>
          关注我 · 每周三分钟刷完 GitHub 一周风云
        </div>
      </div>

      <SubtitleBar text={`${WEEK_WORD} GitHub 周榜收官，下周同一时间见。`} />
      <WatermarkBar />
    </AbsoluteFill>
  );
};
