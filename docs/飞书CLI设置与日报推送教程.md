---
title: 用飞书 CLI 接入个人信息决策雷达：Codex 与 WorkBuddy 完整教程
date: 2026-11-15
source_task: 跨平台 Signal Radar Skill 与个人飞书日报自动推送教程
project: 紫鲸AI内容中台
tags:
  - Signal Radar
  - 飞书CLI
  - Codex
  - WorkBuddy
  - 自动化
summary: 说明如何配置官方 Lark CLI、选择个人飞书目标会话、安装跨平台 Skill，并通过 Codex 或 WorkBuddy 配合本机调度器生成和推送每日信息决策报告。
reusable_insights:
  - Skill 指导信息筛选和报告生成；连接器、持久化、调度和消息推送由脚本和运行时承担。
  - 真实飞书发送前应确认身份、会话和内容，先使用 dry-run。
  - WorkBuddy 云端任务不能默认访问本机 CLI；飞书 CLI 推送应在本地任务或本机调度器运行。
next_actions:
  - 配置 sources.json 与 profile.json，并在测试群完成一条 dry-run/首发验收。
  - 确认目标 chat_id 后安装 LaunchAgent；先运行一周并复盘误报漏报。
related_files:
  - 研究文章.md
  - 附件-Skill/signal-radar/SKILL.md
  - 附件-Skill/signal-radar/profile.example.json
---

# 用飞书 CLI 接入个人信息决策雷达：Codex 与 WorkBuddy 完整教程

作者：半肥猫 · 紫鲸 AI

网站：[www.zjai.ink](https://www.zjai.ink)

公众号：半肥猫 AI研习社
更新日期：2026-11-15

## 1. 这套流程由什么组成

这个项目不是“只有一段提示词”。它分成四层：

1. `SKILL.md`：告诉 Codex、Claude Code、WorkBuddy 如何读用户画像、核验证据、评分和写报告；
2. `collect_sources.py`：从公开 RSS 和指定 GitHub 仓库 Release 收集原始项目，并记录来源失败、重复 ID 和采集时间；
3. Agent 运行时：Codex 或 WorkBuddy 读取采集结果，按 Skill 生成一篇带引用的 Markdown；
4. `push_to_feishu.py`：调用本机官方 `lark-cli`，把 Markdown 推到明确指定的飞书会话。

项目源码、Skill、测试与本教程已公开在 [GitHub：BOB7880/signal-radar](https://github.com/BOB7880/signal-radar)。

定时器负责按时启动流水线。它与 Skill 是不同部件。最简单可维护的个人方案是 macOS LaunchAgent + Codex CLI + 本机 Lark CLI。WorkBuddy 可以加载同一 Skill；它的本地/云端任务执行环境不同，云任务不可默认访问本机 CLI。

```text
LaunchAgent（每日触发）
  → collect_sources.py（公开 RSS / GitHub Release）
  → Codex exec（只读采集结果，按 Skill 筛选）
  → reports/YYYY-MM-DD.md
  → push_to_feishu.py
  → lark-cli（用户身份或机器人身份）
  → 指定飞书群 / 单聊
```

默认只采集公开内容。RSS 示例和 GitHub 仓库清单都可以自行替换。未认证 GitHub API 有速率限制，源配置不应放私密 token。

## 2. 安装官方 Lark CLI

先安装官方 CLI。安装命令可能随发行方式调整，优先查阅 [Lark CLI 官方仓库](https://github.com/larksuite/cli)；当前官方 README 提供 npm 安装方式。安装后确认：

```bash
lark-cli --version
lark-cli im +messages-send --help
```

需要在终端完成 OAuth 登录。发个人身份消息时，应按 CLI 的缺失权限提示授予所需 scope；常见消息发送权限包含 `im:message`，用户身份可能还需 `im:message.send_as_user`。按最小权限授权，不要复制 token 到项目配置。CLI 将认证保存在自己的配置中。

```bash
lark-cli auth login --scope "im:message" --no-wait --json
```

按它返回的授权步骤在浏览器完成登录；如果后续发送报 `missing_scopes`，再根据错误提示申请具体权限。核对当前身份和授权状态：

```bash
lark-cli auth status --json --verify
lark-cli whoami
```

以上命令可能展示用户、租户和授权信息，不要把完整输出贴到公开 issue 或 GitHub。

## 3. 选定目标飞书会话

推荐把日报发到只包含自己的私人群，或指定单聊。先查找可见会话：

```bash
lark-cli im +chat-search --query "我的雷达日报" --as user
```

CLI 返回的会话 ID 通常以 `oc_` 开头。核对名称后，在本机环境变量中设置目标，不要猜测 ID：

```bash
export FEISHU_CHAT_ID='oc_这里换成你确认过的会话ID'
export LARK_IDENTITY='user'
```

如果要发到群里，先确认群名、成员、发送身份和报告内容。机器人身份会以应用身份发出，且机器人需在群中；用户身份则以你本人身份发送。不要混淆两者。

## 4. 安装 Skill

### Codex

在本项目根目录执行：

```bash
python3 scripts/install_skill.py codex
```

也可以手动放到项目级 `.agents/skills/signal-radar/`。重启或新开 Codex 会话，手动让它读取一份样例 inbox，检查是否按 Skill 输出证据等级、评分与实验建议。

### WorkBuddy

将完整 Skill 文件夹导入 WorkBuddy，或在项目根目录执行：

```bash
python3 scripts/install_skill.py workbuddy --base-dir "$PWD"
```

重新载入 WorkBuddy Skills 后，创建本地任务并让它读取 `var/inbox/` 中的样例，产出 Markdown。WorkBuddy 项目文档描述了 Skills 的 `SKILL.md` 加脚本/参考资源结构，也区分本地任务与云端任务。飞书 CLI 在本机，因此云端任务不能假设能调用本机 `lark-cli`。

WorkBuddy 自带的定时任务可以推送到它配置的通知渠道；这与调用本机飞书 CLI 是两条通路。要走本文的 Lark CLI 流程，需要由本机调度器调用本机脚本，或确认 WorkBuddy 版本的本地定时任务确实在同一台机器运行并能访问 CLI。

## 5. 配置来源和业务画像

复制示例文件：

```bash
cp config/sources.example.json config/sources.json
cp config/profile.example.json config/profile.json
```

编辑 `sources.json`，添加你愿意关注的 RSS 和 GitHub `owner/repo`；编辑 `profile.json`，写清楚业务目标、排除主题和每周能投入多少时间。不要把 API Key 写进这两个文件。真实个人配置会被 `.gitignore` 排除。

先只跑采集器：

```bash
python3 scripts/collect_sources.py \
  --config config/sources.json \
  --output var/inbox/sample.json \
  --state var/state/seen.json
```

查看生成的 `var/inbox/sample.json`，它包含候选条目、发布日期、URL、来源类型、重复标记和每个源的成功/失败状态。脚本不会自动判定内容真实，也不会自行给出业务分数；这些由 Agent 按 Skill 执行。

## 6. 飞书推送：先 dry-run，再人工首发

准备一篇不含敏感信息的样例报告：

```bash
mkdir -p reports
cat > reports/sample.md <<'EOF_REPORT'
# 信息雷达测试

- 这是一次 dry-run，不应真正发出消息。
- [示例来源](https://example.com)
EOF_REPORT
```

先预览命令，不会发送：

```bash
python3 scripts/push_to_feishu.py reports/sample.md --dry-run
```

首次真实发送前，人工确认会话、正文和发送身份，再执行：

```bash
python3 scripts/push_to_feishu.py reports/sample.md
```

本机实际试跑中，CLI 能识别命令，但因用户身份缺少消息发送 scope，dry-run 返回 `authorization / missing_scope`；没有发出消息。完成登录与最小 scope 授权后再重复 dry-run。

脚本使用 `FEISHU_CHAT_ID` 和 `LARK_IDENTITY`，通过子进程调用 `lark-cli im +messages-send --markdown @sample.md`；不会读取、保存或输出访问令牌。它使用报告日期和正文哈希生成幂等键，减少短时间重复推送。退出码非零时会安全报告失败，错误详情由你在本机查看。

Markdown 按飞书富文本消息渲染，和 GitHub Markdown 不完全相同。长报告可能不适合直接放在消息正文；可以改成短摘要 + 飞书文档链接，或调整脚本发送文件。这个初版不自动创建云文档。

## 7. Codex + macOS LaunchAgent 每日自动跑

### 7.1 手动完成整条链路

确认 `codex`、`python3`、`lark-cli` 可在终端运行；`config/sources.json`、`config/profile.json` 已配置；`FEISHU_CHAT_ID` 指向正确会话。先手动跑：

```bash
export FEISHU_CHAT_ID='oc_确认过的会话ID'
export LARK_IDENTITY='user'
scripts/run_codex_daily.sh
```

流程先收集，再让 `codex exec` 以只读模式阅读资料并按 Skill 生成 Markdown，最后调用飞书 CLI。若没有达到筛选阈值，模型输出 `NO_SEND`，不会推送。报告和采集状态位于 `reports/`、`var/`，这些运行目录不会提交到 GitHub。

### 7.2 创建 LaunchAgent

复制模板后，将 `__REPO_ROOT__` 替换成项目绝对路径，将 `__USER__` 替换成 macOS 用户名；编辑 `EnvironmentVariables` 中的路径和飞书会话。plist 中不要写 token。

```bash
mkdir -p ~/Library/LaunchAgents
cp launchd/com.zijinai.signal-radar.plist.template ~/Library/LaunchAgents/com.zijinai.signal-radar.plist
```

确认 schedule（模板默认每天 09:00，时区由 macOS 用户会话环境决定；请将 Mac 系统时区设为 Asia/Macau，或按本机时间换算），然后加载：

```bash
launchctl bootstrap "gui/$(id -u)" ~/Library/LaunchAgents/com.zijinai.signal-radar.plist
launchctl print "gui/$(id -u)/com.zijinai.signal-radar"
```

立即测试可用 `launchctl kickstart -k "gui/$(id -u)/com.zijinai.signal-radar"`，它会执行真实流水线；首次验证建议用 `FEISHU_CHAT_ID` 指向测试群，并在 `scripts/run_codex_daily.sh` 中暂时加 `--dry-run` 或先运行推送脚本的 `--dry-run`。确认后再移除 dry-run。

暂停与卸载：

```bash
launchctl bootout "gui/$(id -u)/com.zijinai.signal-radar"
rm ~/Library/LaunchAgents/com.zijinai.signal-radar.plist
```

Mac 需在登录状态运行；睡眠时可能延后执行。查看 `logs/` 下的 stdout/stderr。LaunchAgent 读取不到交互式 shell 的变量，因此模板提供 EnvironmentVariables；路径写成绝对路径。

## 8. WorkBuddy 两种用法

### 用法 A：交互式本地运行

在 WorkBuddy 中导入 Skill，选择本地任务，指令示例：

> 使用 Signal Radar Skill。运行 `scripts/collect_sources.py` 采集配置来源，读取 `config/profile.json`，按证据等级和评分规则生成今天的中文日报，保存到 `reports/YYYY-MM-DD.md`。如果没有达到阈值，文件内容写 `NO_SEND`。先不要发送飞书消息，等我检查报告。

检查后，再运行：

```bash
python3 scripts/push_to_feishu.py reports/YYYY-MM-DD.md --dry-run
```

确认目标和正文，再去掉 `--dry-run`。

### 用法 B：WorkBuddy 定时任务

在 WorkBuddy 项目中加入 Skill 和 `config/profile.json`，建立本地任务并配置每日运行提示词。只有在当前版本的本地/后台任务明确能访问安装了 `lark-cli` 的本机目录时，才让任务调用 `scripts/push_to_feishu.py`。若任务使用云端执行，改用产品自带通知连接器，或使用本教程的 LaunchAgent 执行本机推送脚本。先跑一次单次任务和 dry-run，再开启每天的自动发送。

腾讯 WorkBuddy 官方文档说明定时任务可以按时间触发并向创建者推送结果，且产品区分本地与云端任务；请在当前版本 UI 中确认任务模式与本机命令访问能力，不要依赖不同版本不一致的菜单名称。

## 9. 安全、故障与恢复

- `missing_scope`：只按 CLI 错误提示申请缺少的 scope；用户身份重新登录授权，Bot 身份则在开发者后台配置权限。
- `FEISHU_CHAT_ID` 缺失：脚本停止，不猜目标。
- 报告为空或 `NO_SEND`：不发消息。
- API/RSS 单源失败：采集结果记录错误；报告必须披露覆盖缺口。全部来源失败时停止自动生成，避免把“抓取失败”伪装成安静日。
- 重复推送：检查报告日期与 idempotency key；不要通过重复点击“重试”盲发。
- CLI 升级后参数变化：先看 `lark-cli im +messages-send --help` 和官方 README，再改适配器。
- 不把 `config/profile.json`、`config/sources.json` 中的私人内容、`var/` 日志、用户 ID 或密钥提交公开仓库。
- 首期限定只读采集与发消息；Agent 不得自动发布内容、触达客户或变更生产数据。

## 10. 作者资料

- 项目：Signal Radar / 信息决策雷达
- 公司：紫鲸 AI
- 作者：半肥猫
- 网站：[www.zjai.ink](https://www.zjai.ink)
- 公众号：半肥猫 AI研习社


## 11. 官方依据

- [Lark CLI 官方仓库](https://github.com/larksuite/cli)
- [Lark CLI 官方开发者文档](https://open.larksuite.com/document/mcp_open_tools/feishu-cli-let-ai-actually-do-your-work-in-feishu)
- [WorkBuddy Skills 官方文档](https://cloud.tencent.com/document/product/1831/137452)
- [WorkBuddy 上手指南：定时任务自动推送](https://cloud.tencent.com/document/product/1831/139457)
- [WorkBuddy 项目与本地/云端任务模式](https://cloud.tencent.com/document/product/1831/138797)
- [Codex Skill 安装路径](https://developers.openai.com/api/reference/cli)
