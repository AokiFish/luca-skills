# x-post-reading

遇到 X 推文链接，优先用 api.fxtwitter.com 经 CLI/curl 读取，不用浏览器打开。

## 规则

1. 用法：`curl -s "https://api.fxtwitter.com/<用户名>/status/<id>" -H "Accept: application/json"`，必须带 Accept 头，否则返回 Cloudflare 挑战页。备选 api.vxtwitter.com，同路径。
2. 返回 JSON 含正文、发布时间、点赞/转发/回复/浏览、媒体链接，无需登录、无需 API Key。
3. 用户端点间歇性 404；404 时帖子数据从该帖作者字段取，不要凭记忆编。
4. 引用帖子数据时写明来源端点；粉丝数等数字须逐条核验，不编总数。

## 验收

- 读帖结果写明 fxtwitter 返回的字段（正文、时间、互动数）；浏览器打开只作为 curl 失败后的备用，并说明原因。

## 来源

Luca 2026-11-12 立。已实测：2026-11-12 @mimiAIStudio 的 KriptoK 首帖取回正常。见 ~/AGENTS.md「X 推文读取规则」。
