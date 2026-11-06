# 登录与 cookie

## 一、登录命令

```powershell
.\.venv\Scripts\sau.exe douyin login --account <name> --headed
```

- `--account` 是本地会话别名（可自定义，如 `mimi`），不是平台昵称。
- 一个别名对应一个 cookie 文件，多账号隔离。

## 二、二维码

登录流程会把二维码存成图片并打印到控制台：

```
cookies\<platform>_<account>_login_qrcode_YYYYMMDD_HHMMSS.png
```

**把这张图片直接展示给用户扫**，不要只回复路径。扫码成功后 CLI 会清理临时二维码文件。

抖音成功标志：页面跳到 `https://creator.douyin.com/creator-micro/home`，输出 `Douyin login flow completed: ...cookies\douyin_<account>.json`。

## 三、校验与失效

```powershell
.\.venv\Scripts\sau.exe douyin check --account <name>
```

- 返回 `valid`：可发布。
- 返回 `invalid`：cookie 缺失或过期，重新 `login`。
- cookie 文件位置：`cookies\<platform>_<account>.json`；有效期通常数月，CLI 每次发布成功后会刷新。

## 四、注意事项

1. 登录必须 `--headed`：无头模式在当前环境缺少 headless shell，会启动失败。
2. 不要在非交互环境里硬跑登录；浏览器窗口和二维码是给用户操作的。
3. 登录态是本地文件，不要提交到仓库、不要写进命令或日志。
4. 多账号：换 `--account` 别名即可，互不影响。
