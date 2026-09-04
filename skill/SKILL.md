---
name: desktop-signin-automation
description: 通用桌面应用签到自动化。适用于依赖本地登录态的每日签到任务，含源码获取、凭据探测、进程监测、cron 注册。
version: 1.0.0
author: hermes-agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [signin, automation, desktop, cron]
    related_skills: [github-publishing, hermes-agent]
---

# Skill: 通用桌面应用签到自动化

## 触发
用户需要为某个桌面应用配置每日签到自动化任务，且该应用的登录态存储在本地文件中。

## 参考项目
本 skill 基于 [workbuddy_auto_signin](https://github.com/HEFIVE1102/workbuddy_auto_signin) 开源项目构建。

## 核心逻辑

1. **源码获取**：从 GitHub 克隆 `workbuddy_auto_signin`，提取 signin.py 核心逻辑
2. **凭据探测**：查找应用写出的会话文件（通常含 accessToken/refreshToken）
3. **进程监测**：检测目标应用是否运行，未运行则启动（runner.py 实现）
4. **接口调用**：用会话文件中的 token 调用签到接口
5. **幂等处理**：查询状态→未签才领，重复运行安全

## 执行步骤

### 第 1 步：克隆项目

```bash
git clone https://github.com/HEFIVE1102/workbuddy_auto_signin.git /tmp/desktop-signin
# 复制核心签到脚本到 Hermes scripts
cp /tmp/desktop-signin/examples/<app>/signin.py ~/AppData/Local/hermes/scripts/
cp /tmp/desktop-signin/runner.py ~/AppData/Local/hermes/scripts/
```

### 第 2 步：验证凭据文件位置

- Windows: `%LOCALAPPDATA%/<app>/auth/`
- macOS: `~/Library/Application Support/<app>/auth/`
- Linux: `~/.config/<app>/auth/`
- 或设置环境变量 `WORKBUDDY_AUTH_FILE` 覆盖

### 第 3 步：确认应用可执行文件路径

- 常见路径：`D:\Programs\<App>\<App>.exe`、`C:\Program Files\<App>\`
- 用 `tasklist /fi "imagename eq <App>.exe"` 检测是否运行

### 第 4 步：运行 runner.py

```bash
python runner.py --app "<exe路径>" --signin "<signin.py路径>" [--wait 30]
```

或注册 Hermes cron job：
```bash
hermes cron create --name "<App> 签到" --schedule "30 9 * * *" \
    --script workbuddy_checkin.py --no-agent
```

## 响应契约

| 状态码 | 含义 | 处理 |
|--------|------|------|
| CLAIMED | 成功领取 | 记录积分、连签天数 |
| ALREADY | 今日已签 | 幂等安全，不计失败 |
| INACTIVE | 活动未开启 | 正常跳过 |
| NO_SESSION | 登录态过期 | 需重新登录桌面端 |
| NO_AUTH | 凭据文件未找到 | 需先登录桌面端 |
| ERROR | 其他错误 | 查看详细日志 |

## 依赖

- Python 3.6+（零外部依赖，仅标准库）
- 目标应用桌面端已登录

## 注意事项

- 签名脚本本身不打印 token，可安全分享
- 进程监测逻辑通用，可适配任意桌面应用
- cron job 建议用 `no_agent: true` 模式，纯脚本执行更快

## 扩展其他应用

修改 `examples/<app>/signin.py` 中的：
1. `AUTH_BASENAME` - 凭据文件路径
2. `DEFAULT_ENDPOINT` - API endpoint
3. `build_headers()` - 请求头构造（可选）

然后修改 `runner.py` 中的 `--app` 参数即可。
