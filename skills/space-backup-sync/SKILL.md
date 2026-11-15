# space-backup-sync

Muse 空间同步到 GitHub 私有仓 AokiFish/muse-space：手动快照，不是实时同步；凭证永不入库。

## 规则

1. 目标：https://github.com/AokiFish/muse-space（私有）。完整源码就在磁盘 ~/workspace/ts-spaces/<slug>/；仓库含 muse-home/ + ops/ + 根 RESTORE.md。
2. 程序（按 /opt/hatch/connectors/github/references/snapshot-push.md）：核实分支 head 等于上次同步记录的 SHA → 确认新路径远程不存在 → NUL 分隔 manifest（放源目录外，≤1 MiB、≤2,000 文件、≤16 MiB UTF-8）→ github push-files → 追加记录到 ~/workspace/muse-space-export.muse-github-snapshot-sync.json（临时文件 + 原子改名）。
3. Staging 在 ~/workspace/muse-space-export/；凭证类永不入库。推送须等 Luca 说「推」；审批卡超时不自行重试。
4. 已知缺口：换装 111 张预置 webp 图与运行期 blobs/ 图片库不在仓库里；重建仍需 cron、侧边栏、登录重设。

## 验收

- 记录已追加确认的 SHA；推送路径无凭证；表/行数已交叉核对；缺口已说明。

## 来源

Luca 2026-11-13 定同步要求（设定、源码、数据库、记忆全覆盖，下一 Muse 能直接还原；凭证永不入库）。同步 #4：2026-11-13，389c14c7，16 空间、38 表 / 1,252 行；#5 staging 已完成未推。见 ~/MEMORY.md。
