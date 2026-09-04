<div align="center">

# 🤖 workbuddy_auto_signin

**通用桌面应用签到自动化工具**

零依赖 · 纯标准库 · 进程监测 · 幂等安全

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Win%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

</div>

---

> 本项目提供**配置化 runner** + **通用签到方法论** + **WorkBuddy 示例**，方便用户快速接入其他桌面应用的自动签到。

## 📦 项目定位

本仓库基于上游 [88lin/workbuddy-auto-signin](https://github.com/88lin/workbuddy-auto-signin)（MIT）构建，增加了：

- **runner.py**：通用外壳，自动检测应用进程、启动应用、调用签到脚本
- **skill/SKILL.md**：Hermes Agent skill 集成文档，一键注册定时任务
- **方法论总结**：可复用到其他桌面应用的签到自动化

## ✨ 特性

| 特性 | 说明 |
|------|------|
| 🧩 零依赖 | 纯 Python 标准库，不用 `pip install` |
| 🔍 进程监测 | 自动检测桌面端是否运行，未运行则启动 |
| 🔁 幂等安全 | 查询状态→未签才领，重复运行不重复领取 |
| 🎁 成长中心 | 自动领旅行礼物 / 派 Buddy / 开盲盒 / 领任务奖 |
| 🌐 跨平台 | Windows / macOS / Linux 自动探测凭据文件位置 |
| ⏰ 多运行方式 | cron / Hermes skill / 手动调试 |
| 🔒 无密钥 | 仓库不含任何密钥，只读取运行者本机登录凭据 |

## 🚀 快速开始

### 前置条件

1. ✅ 已安装并**登录过 WorkBuddy 桌面端**（登录后自动写出凭据文件）
2. ✅ 本机有 **Python 3**（任意版本，无需第三方包）

### 克隆仓库

```bash
git clone https://github.com/HEFIVE1102/workbuddy_auto_signin.git
cd workbuddy_auto_signin
```

### 运行方式

#### 方式 A：直接运行 signin.py（Windows 任务计划程序）

```powershell
# 创建定时任务：每天 09:30 静默运行，错过后下次启动时补跑
$pythonw = "pythonw.exe"   # 或完整路径，如 C:\Python313\pythonw.exe
$signin  = (Resolve-Path "examples/workbuddy/signin.py").Path

$action   = New-ScheduledTaskAction -Execute $pythonw -Argument "`"$signin`" silent"
$trigger  = New-ScheduledTaskTrigger -Daily -At "09:30"
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -Hidden `
            -DontStopIfGoingOnBatteries -AllowStartIfOnBatteries `
            -ExecutionTimeLimit (New-TimeSpan -Minutes 10)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

Register-ScheduledTask -TaskName "WorkBuddyAutoSignin" `
    -Action $action -Trigger $trigger -Settings $settings -Principal $principal
```

查看日志：
```bash
tail -5 examples/workbuddy/signin.log
```

卸载定时任务：
```powershell
Unregister-ScheduledTask -TaskName "WorkBuddyAutoSignin" -Confirm:$false
```

#### 方式 B：使用 runner.py（带进程监测，推荐）

```bash
python runner.py \
    --app "D:/Programs/WorkBuddy/WorkBuddy.exe" \
    --signin "examples/workbuddy/signin.py" \
    --wait 30
```

> `--wait`：启动应用后等待秒数（默认 30s，给桌面端登录初始化时间）

#### 方式 C：Hermes Agent 集成

1. 复制脚本到 Hermes scripts 目录：
```bash
cp examples/workbuddy/signin.py ~/AppData/Local/hermes/scripts/
cp runner.py ~/AppData/Local/hermes/scripts/
```

2. 创建 Hermes cron job：
```bash
hermes cron create \
    --name "WorkBuddy 签到" \
    --schedule "30 9 * * *" \
    --script workbuddy_checkin.py \
    --no-agent
```

详见 [skill/SKILL.md](skill/SKILL.md)。

## 📖 命令参考

| 命令 | 作用 |
|------|------|
| `python examples/workbuddy/signin.py auto` | 签到 + 成长中心 |
| `python examples/workbuddy/signin.py silent` | 同 auto，输出写入日志文件（配合定时任务） |
| `python examples/workbuddy/signin.py growth` | 仅成长中心 |
| `python examples/workbuddy/signin.py status` | 查询签到状态（调试） |
| `python examples/workbuddy/signin.py claim` | 仅领取签到（调试） |
| `python examples/workbuddy/signin.py all` | 查询状态 + 领取 |

## ⚙️ 环境变量

| 变量 | 作用 |
|------|------|
| `WORKBUDDY_AUTH_FILE` | 手动指定凭据文件路径（自动探测失败时使用） |
| `WORKBUDDY_SIGNIN_LOG` | 静默模式日志文件路径（默认 `signin.log`） |
| `APP_EXE` | 应用可执行文件路径（runner.py 用） |
| `SIGNIN_SCRIPT` | 签到脚本路径（runner.py 用） |
| `WAIT_SECONDS` | 启动后等待秒数（runner.py 用） |
| `LOG_FILE` | 日志文件路径（runner.py 用） |

## 🔍 凭据文件位置

脚本自动探测以下位置（按顺序）：

- **Windows**: `%LOCALAPPDATA%\CodeBuddyExtension\Data\Public\auth\workbuddy-desktop.info`
- **macOS**: `~/Library/Application Support/CodeBuddyExtension/Data/Public/auth/workbuddy-desktop.info`
- **Linux**: `~/.config/CodeBuddyExtension/Data/Public/auth/workbuddy-desktop.info`

## 🛠️ 扩展其他应用

本项目已内置 WorkBuddy 示例，可按以下步骤扩展到其他桌面应用：

1. **克隆项目**：`git clone https://github.com/HEFIVE1102/workbuddy_auto_signin.git`
2. **参考 signer.py 结构**：查看 `examples/workbuddy/signin.py`，理解凭据探测 + API 调用流程
3. **修改示例脚本**：
   - 修改 `AUTH_BASENAME`（凭据文件名）
   - 修改 `DEFAULT_ENDPOINT`（API endpoint）
   - 修改 `build_headers()`（请求头构造，可选）
4. **创建新示例目录**：`mkdir examples/<app>/ && cp examples/workbuddy/signin.py examples/<app>/`
5. **更新 runner.py 调用**：`python runner.py --app "<App.exe路径>" --signin "examples/<app>/signin.py"`

详细说明见 [skill/SKILL.md](skill/SKILL.md) → "扩展其他应用" 章节。

## 🧪 排错

| 现象 | 处理 |
|------|------|
| `NO_AUTH / 未找到登录凭据` | 先登录 WorkBuddy 桌面端；或设置 `WORKBUDDY_AUTH_FILE` |
| `NO_SESSION / HTTP 401\|403` | 登录态过期——重新登录桌面端，自动化自动恢复 |
| `INACTIVE / 签到活动未开启` | 非签到季，属正常，无需处理 |
| 调试原始返回 | `python examples/workbuddy/signin.py status` 或 `all` |

## 📊 响应契约

| 结果码 | 含义 | 处理 |
|--------|------|------|
| `CLAIMED` | 成功领取 | 记录积分、连签天数 |
| `ALREADY` | 今日已签（幂等） | 安全跳过，不计失败 |
| `INACTIVE` | 活动未开启 | 正常跳过 |
| `NO_SESSION` | 登录态过期 | 需重新登录桌面端 |
| `NO_AUTH` | 凭据文件未找到 | 需先登录桌面端 |
| `ERROR` | 其他错误 | 查看详细日志 |

## 📁 目录结构

```
workbuddy_auto_signin/
├── runner.py              # 通用外壳：进程监测 + 启动 + 签到
├── examples/
│   └── workbuddy/
│       └── signin.py      # 核心签到脚本（来自 88lin/workbuddy-auto-signin，MIT）
├── skill/
│   └── SKILL.md           # Hermes skill 文档 + 扩展指南
├── LICENSE                # MIT + 感谢 88lin
└── README.md              # 本文档
```

## 🔐 安全与隐私

- 脚本只读取**你自己本机**的 WorkBuddy 会话文件，不含、不内嵌、不传输任何第三方密钥
- 永远不会打印 `accessToken`，`Authorization` 头不会出现在日志里
- 可安全 fork、分享、在自己机器上运行——它只作用于**你自己的**登录态

## 📄 协议

本项目采用 [MIT License](LICENSE)，可自由使用、修改、分发。

依赖上游 [88lin/workbuddy-auto-signin](https://github.com/88lin/workbuddy-auto-signin)（MIT，© 2026 88lin）。

## ⚠️ 免责声明

> [!WARNING]
> 本项目为**非官方**工具，与腾讯或 WorkBuddy 无任何隶属关系。签到接口系从桌面端 `app.asar` 逆向得到，仅供个人自动化使用。使用风险自负；接口可能随时变动且不另行通知。请遵守相关服务条款。

---

**Made with ❤️ by HEFIVE1102** | 基于 [88lin/workbuddy-auto-signin](https://github.com/88lin/workbuddy-auto-signin)
