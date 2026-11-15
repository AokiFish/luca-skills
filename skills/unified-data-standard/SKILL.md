# unified-data-standard

七个 Studio 的统一数据标准（v1）。独立不等于孤岛，底座是统一 ID 与共享索引。

## 规则

1. ID 前缀：`person:` / `pose:` / `garment:` / `set:` / `scene:` / `camera:` / `lighting:` / `storyboard:` / `panel:`；输出 `look:`；换装内部 `asset:` / `template:` / `video:`。换装 v74 编号映射并入、不推翻、不重排（只做翻译，不改现有 id）。
2. 共享素材索引只登记元数据，不存文件字节；文件留在各 Studio 自己的存储里；跨空间引用只传 canonical ID。
3. 来源枚举里没有 `gia` / `gia-import` / `wavespeed` 这类取值；姿势素材只自制，不导入 GIA 一张图。
4. 身份/姿势分离写死在字段级（见 identity-pose-separation skill）；组合只在输出层。
5. 版本/文件规则：整数版本；删除 = 退役；ID 永不重用；文件名带 ID + 版本。
6. 明确不做的事：不做 3D、不导入 GIA、不合并数据库、不编造、不动现有资产。
7. 开发顺序：定标准 → 完善现有 2D 生成系统 → 独立做 Pose Studio → 人物/服装/场景管理模块 → 最后做 Muse 总控中心。

## 验收

- 每个新素材有 canonical ID + 索引行；跨空间引用只传 ID；无 gia 来源值；无跨库文件字节搬运。

## 来源

Luca 2026-11-15 定（ChatGPT 第 14 轮开发顺序；「全部素材独立，全部网站独立，然后整合一个完整的」）。全文：~/workspace/research_notes/unified-data-standard-2026-11-15/standard-v1.md。
