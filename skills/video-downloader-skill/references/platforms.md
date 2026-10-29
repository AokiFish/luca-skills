# 各平台下载说明与 Cookie 获取

通用规则：大多数平台用 `python download.py "<URL>"` 即可。下面只写「需要额外操作」或「有坑」的平台。

## YouTube
- 公开视频：无需 cookie。
- 年龄限制 / 私享 / 某些地区限制：加 `--browser chrome` 或 `--cookies cookies.txt`（用 Google 账号登录态）。

## X / Twitter
- 公开推文：通常直接成功。
- 部分媒体（尤其受保护账号、敏感媒体）需登录态：`--browser chrome`。
- 注意 X 链接形式：`https://x.com/user/status/123` 或旧 `twitter.com`，yt-dlp 都认。

## Bilibili
- 公开视频：直接成功。
- 番剧 / 会员专享 / 区域限制：需要 `SESSDATA` cookie。
  - 登录 bilibili.com → 开发者工具 → Application → Cookies → 复制 `SESSDATA` 值 → 写进 cookies.txt（Netscape 格式），或用带登录态的浏览器 `--browser chrome`。
  - 注意 `SESSDATA` 有时效，过期需重新取。

## 抖音 Douyin
- 状态：⚠️ 尽力而为。yt-dlp 有 `Douyin` 提取器，但：
  - 经常被限流（Too Many Requests），需要 cookie 或换时间重试。
  - 直播、部分区域内容可能失败。
- 推荐：用已登录抖音的浏览器 `--browser chrome`；失败就报限制，不盲试。

## 小红书 Xiaohongshu
- 状态：⚠️ 脆弱，高概率失败。
- yt-dlp 的 `XiaoHongShu` 提取器**只支持部分视频笔记**，图文 / 纯文字笔记不支持。
- 必须登录态：用浏览器登录小红书后 `--browser chrome`，或导出 cookies.txt。
- 若连续失败：直接告诉用户「小红书视频笔记下载不稳定，建议换直链或本地下载后上传」，不要反复尝试。

## TikTok
- 通常可用；部分地区 / 限流时加 `--browser chrome`。

## 微博 Weibo
- 公开微博视频通常直接成功；登录态内容需 cookie。

## 通用 Cookie 导出方式
1. 浏览器装扩展「Get cookies.txt LOCALLY」（注意要选 LOCALLY 版，避免上传 cookie）。
2. 登录目标平台，访问目标页面，点扩展导出 cookies.txt。
3. 调用：`python download.py "<URL>" --cookies /path/to/cookies.txt`。
4. 或省事方案：`python download.py "<URL>" --browser chrome`（读取本机已登录浏览器的 cookie，需浏览器已登录且未被锁定）。
