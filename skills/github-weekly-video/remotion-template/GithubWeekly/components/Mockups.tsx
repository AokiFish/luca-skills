import React from "react";
import {interpolate, useCurrentFrame} from "remotion";

const BAR_H = 56;

const Chrome: React.FC<{title: string; dark?: boolean}> = ({title, dark}) => (
  <div
    style={{
      height: BAR_H,
      display: "flex",
      alignItems: "center",
      gap: 10,
      padding: "0 20px",
      backgroundColor: dark ? "#161b22" : "#eae6d9",
      borderBottom: `1px solid ${dark ? "#30363d" : "#d6d2c4"}`,
      flexShrink: 0,
    }}
  >
    <span style={{width: 12, height: 12, borderRadius: "50%", backgroundColor: "#e05a4e"}} />
    <span style={{width: 12, height: 12, borderRadius: "50%", backgroundColor: "#e8b93c"}} />
    <span style={{width: 12, height: 12, borderRadius: "50%", backgroundColor: "#4caf50"}} />
    <span style={{marginLeft: 12, fontSize: 20, color: dark ? "#8b949e" : "#6b7280", fontFamily: "monospace"}}>
      {title}
    </span>
  </div>
);

function wrap(bg: string): React.CSSProperties {
  return {
    width: "100%", height: "100%", borderRadius: 20, overflow: "hidden",
    border: "1px solid #30363d", backgroundColor: bg,
    display: "flex", flexDirection: "column",
  };
}

function chip(text: string, color: string, delay: number, frame: number): React.CSSProperties {
  const o = interpolate(frame, [delay, delay + 10], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
  return {
    opacity: o,
    transform: `translateY(${(1 - o) * 14}px)`,
    padding: "8px 20px",
    borderRadius: 999,
    border: `2px solid ${color}`,
    color,
    fontSize: 22,
    fontWeight: 700,
    fontFamily: "monospace",
    backgroundColor: `${color}1a`,
  };
}

/* #1 impeccable — 设计词汇表作用于代码 */
const VocabMock: React.FC = () => {
  const frame = useCurrentFrame();
  const code = [
    {t: "function Pricing() {", c: "#e6edf3"},
    {t: "  return <Card>…</Card>", c: "#e6edf3"},
    {t: "}", c: "#e6edf3"},
  ];
  const notes = [
    {word: "polish", color: "#3fb950", hint: "间距 · 层次 · 细节", at: 30},
    {word: "bold", color: "#f78166", hint: "更敢用对比和留白", at: 60},
    {word: "critique", color: "#d29922", hint: "挑出平庸之处", at: 90},
    {word: "audit", color: "#58a6ff", hint: "逐项过验收清单", at: 120},
  ];
  const passO = interpolate(frame, [160, 175], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
  return (
    <div style={wrap("#0d1117")}>
      <Chrome title="impeccable — design vocab → agent" dark />
      <div style={{flex: 1, display: "flex", gap: 20, padding: 24}}>
        {/* code panel */}
        <div style={{flex: 1.2, backgroundColor: "#161b22", borderRadius: 14, padding: 20, fontFamily: "monospace", fontSize: 20, lineHeight: 2}}>
          <div style={{color: "#8b949e", fontSize: 16}}>// Agent 正在生成界面</div>
          {code.map((l, i) => (
            <div key={i} style={{color: l.c}}>{l.t}</div>
          ))}
          {notes.map((n, i) => (
            <div key={i} style={{color: n.color, fontSize: 17, marginTop: 6, opacity: interpolate(frame, [n.at, n.at + 10], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"})}}>
              {"↳ "}{n.word}: {n.hint}
            </div>
          ))}
        </div>
        {/* vocab chips */}
        <div style={{flex: 1, display: "flex", flexDirection: "column", gap: 14, justifyContent: "center", alignItems: "center"}}>
          {notes.map((n, i) => (
            <div key={i} style={chip(n.word, n.color, n.at, frame)}>{n.word}</div>
          ))}
          <div style={{...chip("✓ audit passed", "#3fb950", 160, frame), marginTop: 10, opacity: passO}}>
            ✓ audit passed
          </div>
        </div>
      </div>
    </div>
  );
};

/* #2 hallmark — before / after 变身 */
const SkillMock: React.FC = () => {
  const frame = useCurrentFrame();
  const t = interpolate(frame, [40, 110], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
  const steps = ["艺术指导", "参考图", "浏览器走查"];
  const radius = 2 + t * 18;
  const pad = 16 + t * 10;
  return (
    <div style={wrap("#0d1117")}>
      <Chrome title="hallmark — anti AI-slop" dark />
      <div style={{flex: 1, display: "flex", gap: 24, padding: 26, alignItems: "center"}}>
        {/* before card */}
        <div style={{flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 14}}>
          <div style={{fontSize: 20, color: "#8b949e", fontFamily: "monospace"}}>BEFORE · AI slop</div>
          <div style={{width: "100%", backgroundColor: "#3d444d", padding: 16, borderRadius: 4}}>
            <div style={{height: 18, width: "70%", backgroundColor: "#656c76", marginBottom: 10}} />
            <div style={{height: 12, width: "90%", backgroundColor: "#656c76", marginBottom: 8}} />
            <div style={{height: 12, width: "55%", backgroundColor: "#656c76"}} />
          </div>
        </div>
        {/* arrow */}
        <div style={{fontSize: 56, color: "#3fb950", fontWeight: 900, opacity: interpolate(frame, [30, 45], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"})}}>→</div>
        {/* after card */}
        <div style={{flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 14}}>
          <div style={{fontSize: 20, color: "#3fb950", fontFamily: "monospace"}}>AFTER · 有设计感</div>
          <div style={{
            width: "100%", padding: pad,
            borderRadius: radius,
            background: `linear-gradient(135deg, rgba(47,164,79,${0.15 + t * 0.25}), rgba(88,166,255,${0.1 + t * 0.2}))`,
            border: "1px solid #30363d",
            boxShadow: `0 ${8 * t}px ${24 * t}px rgba(0,0,0,${0.4 * t})`,
          }}>
            <div style={{height: 20, width: "70%", backgroundColor: "#e6edf3", borderRadius: 6, marginBottom: 12}} />
            <div style={{height: 12, width: "90%", backgroundColor: "#8b949e", borderRadius: 6, marginBottom: 8}} />
            <div style={{display: "flex", gap: 8, marginTop: 14}}>
              <div style={{height: 26, width: 74, borderRadius: 999, backgroundColor: "#238636"}} />
              <div style={{height: 26, width: 74, borderRadius: 999, border: "1px solid #58a6ff"}} />
            </div>
          </div>
        </div>
      </div>
      {/* steps */}
      <div style={{display: "flex", gap: 12, padding: "0 26px 22px"}}>
        {steps.map((s, i) => {
          const o = interpolate(frame, [120 + i * 18, 132 + i * 18], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
          return (
            <div key={i} style={{opacity: o, flex: 1, textAlign: "center", padding: "10px 0", borderRadius: 10, backgroundColor: "#161b22", border: "1px solid #30363d", color: "#e6edf3", fontSize: 20}}>
              ✓ {s}
            </div>
          );
        })}
      </div>
    </div>
  );
};

/* #3 security-audit-skill — 多阶段审计流水线 */
const AuditMock: React.FC = () => {
  const frame = useCurrentFrame();
  const phases = [
    {name: "侦察 recon", at: 20},
    {name: "分析 analyze", at: 65},
    {name: "验证 verify", at: 110},
    {name: "报告 report", at: 155},
  ];
  const findings = [
    {sev: "HIGH", color: "#f85149", text: "注入风险：未转义的用户输入", at: 185},
    {sev: "MED", color: "#d29922", text: "依赖：2 个过期待升级", at: 215},
    {sev: "LOW", color: "#58a6ff", text: "配置：调试模式未关闭", at: 245},
  ];
  return (
    <div style={wrap("#0d1117")}>
      <Chrome title="security-audit-skill — multi-phase" dark />
      <div style={{flex: 1, display: "flex", gap: 24, padding: 26}}>
        {/* phases */}
        <div style={{flex: 1, display: "flex", flexDirection: "column", gap: 18, justifyContent: "center"}}>
          {phases.map((p, i) => {
            const o = interpolate(frame, [p.at, p.at + 12], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
            const done = frame > p.at + 30;
            return (
              <div key={i} style={{opacity: o, display: "flex", alignItems: "center", gap: 14}}>
                <div style={{
                  width: 44, height: 44, borderRadius: "50%",
                  backgroundColor: done ? "#238636" : "#21262d",
                  border: `2px solid ${done ? "#3fb950" : "#30363d"}`,
                  color: "#fff", display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: 22, fontWeight: 800,
                }}>{done ? "✓" : i + 1}</div>
                <div style={{color: "#e6edf3", fontSize: 24, fontFamily: "monospace"}}>{p.name}</div>
              </div>
            );
          })}
        </div>
        {/* findings */}
        <div style={{flex: 1.3, backgroundColor: "#161b22", borderRadius: 14, padding: 20, display: "flex", flexDirection: "column", gap: 14, justifyContent: "center"}}>
          <div style={{color: "#8b949e", fontSize: 17, fontFamily: "monospace"}}>findings.json — 机器可读</div>
          {findings.map((f, i) => {
            const o = interpolate(frame, [f.at, f.at + 12], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
            return (
              <div key={i} style={{opacity: o, display: "flex", alignItems: "center", gap: 12, backgroundColor: "#0d1117", border: "1px solid #30363d", borderRadius: 10, padding: "10px 14px"}}>
                <span style={{backgroundColor: f.color, color: "#fff", fontSize: 15, fontWeight: 800, padding: "2px 10px", borderRadius: 6, fontFamily: "monospace"}}>{f.sev}</span>
                <span style={{color: "#e6edf3", fontSize: 19}}>{f.text}</span>
              </div>
            );
          })}
          <div style={{color: "#3fb950", fontSize: 18, fontFamily: "monospace", opacity: interpolate(frame, [275, 290], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"})}}>
            ✓ 结论可独立验证 · 可复核
          </div>
        </div>
      </div>
    </div>
  );
};

/* #4 t3code — 手机 + 桌面驾驶舱 */
const CockpitMock: React.FC = () => {
  const frame = useCurrentFrame();
  const agents = [
    {name: "claude-code", task: "重构支付模块", p: 0.86},
    {name: "codex", task: "补齐 API 测试", p: 0.54},
    {name: "gemini", task: "Review PR #142", p: 0.22},
  ];
  return (
    <div style={wrap("#0f1b2d")}>
      <Chrome title="t3code — agent control surface" dark />
      <div style={{flex: 1, display: "flex", gap: 26, padding: 26, alignItems: "center"}}>
        {/* phone */}
        <div style={{opacity: interpolate(frame, [10, 25], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"}), width: 190, height: 380, borderRadius: 28, border: "3px solid #30363d", backgroundColor: "#010409", padding: 16, display: "flex", flexDirection: "column", gap: 12}}>
          <div style={{width: 60, height: 8, borderRadius: 4, backgroundColor: "#30363d", margin: "0 auto"}} />
          <div style={{color: "#e6edf3", fontSize: 17, fontFamily: "monospace"}}>iOS / Android</div>
          {agents.map((a, i) => (
            <div key={i} style={{backgroundColor: "#161b22", borderRadius: 10, padding: 10, opacity: interpolate(frame, [50 + i * 20, 62 + i * 20], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"})}}>
              <div style={{color: "#3fb950", fontSize: 13, fontFamily: "monospace"}}>● {a.name}</div>
              <div style={{color: "#8b949e", fontSize: 12, marginTop: 4}}>{a.task}</div>
            </div>
          ))}
        </div>
        {/* desktop list */}
        <div style={{flex: 1, display: "flex", flexDirection: "column", gap: 16}}>
          <div style={{color: "#8b949e", fontSize: 18, fontFamily: "monospace"}}>本机 Agent · 统一下发任务 / 查看进度</div>
          {agents.map((a, i) => {
            const o = interpolate(frame, [30 + i * 20, 44 + i * 20], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
            const w = interpolate(frame, [44 + i * 20, 44 + i * 20 + 200], [0, a.p * 100], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
            return (
              <div key={i} style={{opacity: o, backgroundColor: "#16233d", borderRadius: 12, padding: "14px 18px"}}>
                <div style={{display: "flex", justifyContent: "space-between", marginBottom: 8}}>
                  <span style={{color: "#e6edf3", fontFamily: "monospace", fontSize: 20}}>{a.name}</span>
                  <span style={{color: "#8b949e", fontSize: 17}}>{a.task}</span>
                </div>
                <div style={{height: 8, borderRadius: 4, backgroundColor: "#0d1117", overflow: "hidden"}}>
                  <div style={{width: `${w}%`, height: "100%", backgroundColor: "#3fb950"}} />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

/* #5 dsh-purge — 提示词切换面板（中性播报） */
const PurgeMock: React.FC = () => {
  const frame = useCurrentFrame();
  const rows = [
    {m: "model-A", at: 25},
    {m: "model-B", at: 55},
    {m: "model-C", at: 85},
  ];
  return (
    <div style={wrap("#0d1117")}>
      <Chrome title="dsh-purge — prompt profiles" dark />
      <div style={{flex: 1, display: "flex", flexDirection: "column", gap: 16, padding: 26, justifyContent: "center"}}>
        <div style={{color: "#d29922", fontSize: 20, border: "1px solid #d29922", borderRadius: 10, padding: "10px 16px", backgroundColor: "#d2992215"}}>
          ⚠ 争议项目：本质为绕过模型安全限制，此处仅作榜单播报
        </div>
        {rows.map((r, i) => {
          const o = interpolate(frame, [r.at, r.at + 12], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
          return (
            <div key={i} style={{opacity: o, display: "flex", alignItems: "center", gap: 14, backgroundColor: "#161b22", border: "1px solid #30363d", borderRadius: 12, padding: "14px 18px", fontFamily: "monospace"}}>
              <span style={{color: "#e6edf3", fontSize: 21, width: 130}}>{r.m}</span>
              <span style={{color: "#8b949e", fontSize: 21}}>→</span>
              <span style={{color: "#58a6ff", fontSize: 21}}>prompt-{r.m.split("-")[1]}</span>
              <span style={{flex: 1}} />
              <span style={{color: "#3fb950", fontSize: 18}}>switched</span>
            </div>
          );
        })}
        <div style={{color: "#8b949e", fontSize: 18, fontFamily: "monospace", opacity: interpolate(frame, [120, 135], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"})}}>
          一周 +6,644 ★ · 讨论度与争议齐飞
        </div>
      </div>
    </div>
  );
};

export const ProjectMockup: React.FC<{kind: string}> = ({kind}) => {
  switch (kind) {
    case "vocab": return <VocabMock />;
    case "skill": return <SkillMock />;
    case "audit": return <AuditMock />;
    case "cockpit": return <CockpitMock />;
    case "purge": return <PurgeMock />;
    default: return null;
  }
};
