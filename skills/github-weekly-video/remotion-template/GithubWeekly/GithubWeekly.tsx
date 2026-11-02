import React from "react";
import {
  AbsoluteFill,
  Audio,
  interpolate,
  Sequence,
  staticFile,
  useCurrentFrame,
} from "remotion";
import {
  CoverScene,
  OutroScene,
  ProjectDetailScene,
  ProjectIntroScene,
} from "./scenes";
import {VO_FILE} from "./data";

/* CUTS / DURATION 由配音时长决定。
   流程：scripts/gen_voiceover.py 生成配音并输出 cuts.json（每场景帧数）
         → scripts/build.py 用正则把下面这组数字替换为真实值。
   此处为「示例时长」（≈149s，基于男声配音），即便没生成配音也能直接渲染示例版。 */
const CUTS = {
  coverEnd: 455,      // 15.2s
  p1IntroEnd: 634,    // 21.1s
  p1End: 1281,        // 42.7s
  p2IntroEnd: 1428,   // 47.6s
  p2End: 1994,        // 66.5s
  p3IntroEnd: 2153,   // 71.8s
  p3End: 2646,        // 88.2s
  p4IntroEnd: 2789,   // 93.0s
  p4End: 3282,        // 109.4s
  p5IntroEnd: 3449,   // 115.0s
  p5End: 3956,        // 131.9s
};

export const GITHUB_WEEKLY_DURATION = 4471; // ≈149s

/* Fade in/out wrapper（instant: 首帧即完全可见，供封面出首帧图） */
const Fade: React.FC<{len: number; instant?: boolean; children: React.ReactNode}> = ({
  len,
  instant,
  children,
}) => {
  const frame = useCurrentFrame();
  const fadeIn = instant
    ? 1
    : interpolate(frame, [0, 6], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
  const fadeOut = interpolate(frame, [len - 6, len], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill style={{opacity: Math.min(fadeIn, fadeOut)}}>
      {children}
    </AbsoluteFill>
  );
};

export const GithubWeekly: React.FC = () => {
  const scenes: {from: number; len: number; node: React.ReactNode}[] = [
    {from: 0, len: CUTS.coverEnd, node: <CoverScene />},
    {from: CUTS.coverEnd, len: CUTS.p1IntroEnd - CUTS.coverEnd, node: <ProjectIntroScene index={0} />},
    {from: CUTS.p1IntroEnd, len: CUTS.p1End - CUTS.p1IntroEnd, node: <ProjectDetailScene index={0} />},
    {from: CUTS.p1End, len: CUTS.p2IntroEnd - CUTS.p1End, node: <ProjectIntroScene index={1} />},
    {from: CUTS.p2IntroEnd, len: CUTS.p2End - CUTS.p2IntroEnd, node: <ProjectDetailScene index={1} />},
    {from: CUTS.p2End, len: CUTS.p3IntroEnd - CUTS.p2End, node: <ProjectIntroScene index={2} />},
    {from: CUTS.p3IntroEnd, len: CUTS.p3End - CUTS.p3IntroEnd, node: <ProjectDetailScene index={2} />},
    {from: CUTS.p3End, len: CUTS.p4IntroEnd - CUTS.p3End, node: <ProjectIntroScene index={3} />},
    {from: CUTS.p4IntroEnd, len: CUTS.p4End - CUTS.p4IntroEnd, node: <ProjectDetailScene index={3} />},
    {from: CUTS.p4End, len: CUTS.p5IntroEnd - CUTS.p4End, node: <ProjectIntroScene index={4} />},
    {from: CUTS.p5IntroEnd, len: CUTS.p5End - CUTS.p5IntroEnd, node: <ProjectDetailScene index={4} />},
    {from: CUTS.p5End, len: GITHUB_WEEKLY_DURATION - CUTS.p5End, node: <OutroScene />},
  ];

  return (
    <AbsoluteFill style={{backgroundColor: "#f4f1e8"}}>
      {scenes.map((s, i) => (
        <Sequence key={i} from={s.from} durationInFrames={s.len}>
          <Fade len={s.len} instant={i === 0}>{s.node}</Fade>
        </Sequence>
      ))}
      {/* 旁白（可选）：VO_FILE 在 data.ts 设置；留空字符串则不渲染音频，仅靠字幕 */}
      {VO_FILE ? (
        <Audio
          src={staticFile(VO_FILE)}
          volume={(f) =>
            interpolate(f, [0, 8, GITHUB_WEEKLY_DURATION - 20, GITHUB_WEEKLY_DURATION - 4],
              [0, 0.92, 0.92, 0], {extrapolateLeft: "clamp", extrapolateRight: "clamp"})
          }
        />
      ) : null}
    </AbsoluteFill>
  );
};
