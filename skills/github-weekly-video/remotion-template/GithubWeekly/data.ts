export type Project = {
  rank: number;
  repo: string; // owner/name
  name: string; // display name
  desc: string; // Chinese one-liner
  lang: string;
  langColor: string;
  totalStars: number;
  weekStars: number;
  tags: string[];
  points: string[]; // 三大看点，逐条入场
  url: string;
  subtitleIntro: string;
  subtitleDetail: string;
  mockup: "vocab" | "skill" | "audit" | "cockpit" | "purge";
};

// ===== 以下为「每期需填写」的配置，由 agent 按真实抓取数据替换 =====
export const WEEK_LABEL = "10.27–11.02 周榜"; // 榜单周期，写在封面小字
export const WEEK_SHORT = "11月第1周";        // 封面绿色 pill 文字
export const WEEK_WORD = "上周";               // 封面/片尾用词：上周 / 本周 / 本季
export const VO_FILE = ""; // 配音文件（public/ 下相对路径）。留空=无声仅字幕；提供后填 "vo/xxx.mp3"。build 时替换为当日文件名
// ===================================================================

export const PROJECTS: Project[] = [
  {
    rank: 1,
    repo: "pbakaus/impeccable",
    name: "impeccable",
    desc: "给编码 Agent 的设计词汇表",
    lang: "Rust",
    langColor: "#f74c00",
    totalStars: 99904,
    weekStars: 12017,
    tags: ["AI 编码", "设计规范"],
    points: [
      "一套教 Agent 审美的设计词汇",
      "polish / bold：界面更精致大胆",
      "critique / audit：上线前拦住 AI 味",
    ],
    url: "github.com/pbakaus/impeccable",
    subtitleIntro: "第一个，impeccable，本周涨了一万两千星，直接登顶。",
    subtitleDetail:
      "它是给编码 Agent 的一套设计词汇表：用 polish 和 bold 引导生成，再用 critique 和 audit 两道审查，拦住一眼假的 AI 页面。",
    mockup: "vocab",
  },
  {
    rank: 2,
    repo: "Nutlope/hallmark",
    name: "hallmark",
    desc: "反 AI 味的设计技能包",
    lang: "CSS",
    langColor: "#563d7c",
    totalStars: 45430,
    weekStars: 11566,
    tags: ["AI 编码", "设计技能"],
    points: [
      "和冠军同赛道：反 AI slop",
      "艺术指导 + 参考图 + 浏览器走查",
      "适配 Claude Code / Cursor / Codex",
    ],
    url: "github.com/Nutlope/hallmark",
    subtitleIntro: "第二个，hallmark，一周进账一万一千多星。",
    subtitleDetail:
      "它和冠军同一赛道：反 AI 味。把艺术指导、参考图和浏览器走查写进 Agent 工作流，让界面像人做的，而不是千篇一律的模板。",
    mockup: "skill",
  },
  {
    rank: 3,
    repo: "cloudflare/security-audit-skill",
    name: "security-audit-skill",
    desc: "Cloudflare 出品的安全审计技能",
    lang: "JavaScript",
    langColor: "#f1e05a",
    totalStars: 56812,
    weekStars: 10069,
    tags: ["安全审计", "Cloudflare"],
    points: [
      "Cloudflare 官方出品",
      "多阶段安全审计流水线",
      "结论可独立验证、机器可读",
    ],
    url: "github.com/cloudflare/security-audit-skill",
    subtitleIntro: "第三个，Cloudflare 官方出品的 security-audit-skill。",
    subtitleDetail:
      "它把安全审计拆成多个阶段交给 Agent 逐步执行，产出可独立验证、机器可读的结论。大厂下场做 Agent 技能，信号值得留意。",
    mockup: "audit",
  },
  {
    rank: 4,
    repo: "pingdotgg/t3code",
    name: "t3code",
    desc: "统管本机 Agent 的驾驶舱",
    lang: "TypeScript",
    langColor: "#3178c6",
    totalStars: 39571,
    weekStars: 6926,
    tags: ["Agent 控制", "Theo"],
    points: [
      "Agent Harness 控制台",
      "手机 / 网页 / 桌面三端齐发",
      "统一接管本机所有编码 Agent",
    ],
    url: "github.com/pingdotgg/t3code",
    subtitleIntro: "第四个，t3code，来自 Theo 的团队。",
    subtitleDetail:
      "它的定位是 Agent 驾驶舱：本机跑着的各种编码 Agent，都能用手机、网页、桌面客户端统一接管、下发任务、看进度。",
    mockup: "cockpit",
  },
  {
    rank: 5,
    repo: "YuJunZhiXue/dsh-purge",
    name: "dsh-purge",
    desc: "榜单上最有争议的社区项目",
    lang: "JavaScript",
    langColor: "#f1e05a",
    totalStars: 15902,
    weekStars: 6644,
    tags: ["提示词", "争议项目"],
    points: [
      "按模型切换不同提示词",
      "绕过模型各自的安全限制",
      "一周 +6.6K，讨论度拉满",
    ],
    url: "github.com/YuJunZhiXue/dsh-purge",
    subtitleIntro: "第五个，dsh-purge，本周榜单上最有争议的一个。",
    subtitleDetail:
      "它通过切换提示词让模型绕过各自的安全限制，本质上是越狱工具。这里只做榜单播报，怎么用、该不该用，大家自行判断。",
    mockup: "purge",
  },
];

export const WEEK_NEW_STARS = PROJECTS.reduce((s, p) => s + p.weekStars, 0);

export function formatStars(n: number): string {
  if (n >= 1000) return `${(n / 1000).toFixed(1)}K`;
  return `${n}`;
}

export function formatTotal(n: number): string {
  return n.toLocaleString("en-US");
}
