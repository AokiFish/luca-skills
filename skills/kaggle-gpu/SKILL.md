# kaggle-gpu

Kaggle 只用 Aoo 号；模型挂数据集，不重复下载；显存爆了按清单修，不瞎猜。

## 规则

1. 用 Aoo 号（lsh531298158@gmail.com，用户名 aixiaobei1024）：手机已验证、身份已验证、GPU T4 x2、互联网已开。mimiailab 号（ailuca369@gmail.com）未手机验证、GPU 与互联网置灰——已知状态，不催 Luca 去验证它。浏览器里的 Google 账号与 Kaggle 登录账号不是同一个，别混淆。
2. 模型挂 Kaggle Dataset，从 /kaggle/input 加载；绝不每会话重下权重——下一次、存到 output Dataset、以后先查挂载文件。ic-light-models v2 数据集已完成（9.42GB，SHA256 已校验），重跑直接挂载。
3. 视频 Notebook OOM 修法清单：文本编码器放 CPU / 降分辨率与帧数 / 换更大显存；Wan2.1 必须用 -Diffusers 仓库。enable_model_cpu_offload 也可能在 T5 编码器前向爆掉，不要默认它能修好。GPU 额度按会话墙上时间计，含空闲时间。
4. Kaggle/GPU 话题在专聊讨论，不占主 bot 上下文。

## 验收

- 运行先挂数据集、无重下载；OOM 修法出自清单；账号用的是 Aoo。

## 来源

Luca 2026-11-14 定（Kaggle 模型挂数据集）；2026-11-13 morning-coffee OOM（CogVideoX-2b 单张 T4 爆满，CPU offload 也爆在 T5 前向）；IC-Light 2026-11-14 跑通。见 ~/MEMORY.md。
