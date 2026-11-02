# 配音工作流

## 声音选择（随时可换）

| 参数 | 含义 | 参考声源 |
| --- | --- | --- |
| `woman`（默认） | 女声 | `{VOICE_DIR}/ai-weekly-woman.mp3` |
| `man`（`/M` 或"男声"） | 男声 | `{VOICE_DIR}/ai-weekly-man.mp3` |

- `VOICE_DIR` 默认是 `D:\self-media\projects\luca-video\Voiceover`。想换声音，往这个目录放新的参考文件，或改 `VOICE_DIR`。
- 用户说"换女声/换男声/换一个声音"，就按新指定性别重新克隆，其他流程不变。

## 铁律：先克隆，再配音

不能用 TTS 播音腔直接念。**必须**拿参考声源先克隆音色，再让克隆声音念完整解说词。
（同一段旁白必须一次性生成完整音频，禁止拆成多段——拆段会在句间插入停顿，听起来一卡一卡。）

## 解说词（narration.txt）

每行 = 一个场景的台词，固定 12 行顺序：
1. 封面开场
2. 项目1 过场
3. 项目1 详解
4. 项目2 过场
5. 项目2 详解
6. 项目3 过场
7. 项目3 详解
8. 项目4 过场
9. 项目4 详解
10. 项目5 过场
11. 项目5 详解
12. 片尾

模板（语速快、自然、有换气，不要播音腔）：
```
{WEEK_WORD} GitHub 周榜出炉，五个项目一周狂揽 {总星数} 颗星。
第一名 {name}，{一句亮点}。
{详解两点：做什么 + 为什么火}。
第二名 {name}，{一句亮点}。
{详解两点}。
第三名 {name}，{一句亮点}。
{详解两点}。
第四名 {name}，{一句亮点}。
{详解两点}。
第五名 {name}，{一句亮点}。
{详解两点}。{WEEK_WORD} GitHub 周榜收官，关注我每周三分钟刷完 GitHub 一周风云。
```

## 克隆 + 生成（agent 执行）

1. `FileBatchUpload` 上传参考声源（`{VOICE_DIR}/ai-weekly-{woman|man}.mp3`）拿 URL。
2. 调 `audio_to_audio_plus`：
   - `audio_reference_url_list` = [参考声源 URL]
   - `prompt` = "完全模仿 @音频1 的声音音色、语速、语气和说话风格，在安静室内连续地说完整段，不要省略：{narration 全文}"
   - 结果 URL → `curl` 下载到 `public/vo/vo-full.mp3`
3. 若生成被截断（没说完），重新生成更长的版本，直到完整。

## 对齐 + 渲染（脚本）

```powershell
cd <remotion-project>
python scripts/build.py --project-root . --date 2026-11-02 --vo public/vo/vo-full.mp3 --narration narration.txt
```

`build.py` 会自动：复制配音 → 跑 `gen_cuts.py`（silencedetect 停顿 + 字数比例对齐 CUTS）→ 渲染 mp4 → 首帧封面 → 生成字幕。
