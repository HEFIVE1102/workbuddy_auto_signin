# WorkBuddy 每日签到自动领取脚本

> **基于** [88lin/workbuddy-auto-signin](https://github.com/88lin/workbuddy-auto-signin)（MIT）构建  
> **本仓库**：提供配置化 runner + Hermes skill 集成，方便复用和扩展

## 特性

| 特性 | 说明 |
|------|------|
| 零依赖 | 纯 Python 标准库，无需 pip install |
| 进程监测 | 自动检测桌面端是否运行，未运行则启动 |
| 幂等安全 | 查询状态→未签才领，重复运行不重复领取 |
| 成长中心 | 自动领旅行礼物/派Buddy/开盲盒/领任务奖 |
| 跨平台 | Windows/macOS/Linux 自动探测凭据文件位置 |
| 多运行方式 | cron 定时、Hermes skill、手动调试 |

## 快速开始

### 1. 前置条件

- ✅ 已安装并**登录过 WorkBuddy 桌面端**
- ✅ 本机有 **Python 3**（无需第三方包）

### 2. 运行方式

#### 方式 A：直接运行 signin.py（Windows 任务计划程序 + pythonw.exe）

```powershell
# 创建定时任务：每天 09:30 静默运行，错过后下次启动时补跑
$pythonw = "pythonw.exe"   # 或完整路径
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

#### 方式 B：使用 runner.py（带进程监测）

```bash
python runner.py \
    --app "D:/Programs/WorkBuddy/WorkBuddy.exe" \
    --signin "examples/workbuddy/signin.py" \
    --wait 30
```

#### 方式 C：Hermes skill 集成

```bash
# 复制到 Hermes scripts 目录
cp examples/workbuddy/signin.py ~/AppData/Local/hermes/scripts/
cp runner.py ~/AppData/Local/hermes/scripts/

# 创建 Hermes cron job（每天 09:30）
hermes cron create --name "WorkBuddy 签到" --schedule "30 9 * * *" \
    --script workbuddy_checkin.py --no-agent
```

### 3. 查看日志

```bash
tail -5 examples/workbuddy/signin.log
```

## 命令参考

| 命令 | 作用 |
|------|------|
| `python signin.py auto` | 签到 + 成长中心 |
| `python signin.py silent` | 同 auto，输出写入日志文件 |
| `python signin.py growth` | 仅成长中心 |
| `python signin.py status` | 查询签到状态 |
| `python signin.py claim` | 仅领取签到 |
| `python signin.py all` | 查询状态 + 领取 |

## 环境变量

| 变量 | 作用 |
|------|------|
| `WORKBUDDY_AUTH_FILE` | 手动指定凭据文件路径（自动探测失败时使用） |
| `WORKBUDDY_SIGNIN_LOG` | 静默模式日志文件路径 |
| `APP_EXE` | 应用可执行文件路径（runner.py 用） |
| `WAIT_SECONDS` | 启动后等待秒数（runner.py 用） |

## 凭据文件位置

脚本自动探测以下位置：

- **Windows**: `%LOCALAPPDATA%\CodeBuddyExtension\Data\Public\auth\workbuddy-desktop.info`
- **macOS**: `~/Library/Application Support/CodeBuddyExtension/Data/Public/auth/workbuddy-desktop.info`
- **Linux**: `~/.config/CodeBuddyExtension/Data/Public/auth/workbuddy-desktop.info`

## 排错

| 现象 | 处理 |
|------|------|
| `NO_AUTH / 未找到登录凭据` | 先登录 WorkBuddy 桌面端；或设置 `WORKBUDDY_AUTH_FILE` |
| `NO_SESSION / HTTP 401\|403` | 登录态过期——重新登录桌面端 |
| `INACTIVE / 签到活动未开启` | 非签到季，属正常，无需处理 |
| 调试原始返回 | `python signin.py status` 或 `python signin.py all` |

## 响应契约

| 结果码 | 含义 |
|--------|------|
| `CLAIMED` | 成功领取 |
| `ALREADY` | 今日已签（幂等） |
| `INACTIVE` | 活动未开启 |
| `NO_SESSION` | 登录态过期，需重新登录 |
| `NO_AUTH` | 凭据文件未找到 |
| `ERROR` | 其他错误 |

## 目录结构

```
workbuddy_auto_signin/
├── runner.py          # 通用外壳：进程监测 + 启动 + 签到
├── examples/
│   └── workbuddy/
│       ├── signin.py  # 核心签到脚本（来自 88lin/workbuddy-auto-signin，MIT）
│       └── README.md  # WorkBuddy 示例说明
├── skill/
│   └── SKILL.md       # Hermes skill 文档
├── LICENSE            # MIT + 感谢 88lin
└── README.md          # 本文档
```

## 协议

[MIT](LICENSE) © 2026 本仓库贡献者  
依赖上游 [88lin/workbuddy-auto-signin](https://github.com/88lin/workbuddy-auto-signin)（MIT，© 2026 88lin）

## 免责声明

本项目为**非官方**工具，与腾讯或 WorkBuddy 无任何隶属关系。签到接口系从桌面端逆向得到，仅供个人自动化使用。请遵守相关服务条款，使用风险自负。接口可能随时变动且不另行通知。
