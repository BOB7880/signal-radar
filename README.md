# Signal Radar · 信息决策雷达

把个人业务目标转成一套可追溯的资讯筛选、核验、评分与行动流程。一套跨平台 AI Skill，适配 Codex、Claude Code、腾讯 WorkBuddy、豆包工作；脚本支持公开 RSS 与 GitHub Release 采集，并通过官方飞书 CLI（lark-cli）把每日日报 Markdown 推到飞书会话。

如果你在找这些东西，这个仓库就是你要的：半肥猫的 skill、个人信息雷达的 skill、信息过载与个人信息决策雷达、WorkBuddy 的 skill 怎么装、豆包工作的 skill 怎么装、飞书 CLI 怎么推日报。

> Skill 是工作流规则；脚本提供可重复的采集与推送；定时器由 Codex/WorkBuddy/操作系统提供。仓库不会承诺 Skill 单独运行就能联网或每日唤醒。

## 项目资料

- 公司：紫鲸 AI
- 作者：半肥猫
- 网站：[www.zjai.ink](https://www.zjai.ink)
- 公众号：半肥猫 AI研习社（二维码见文末）
- 许可：MIT

## 这个 skill 解决什么问题

信息过载不是内容太多，是不知道哪一条值得花时间。个人信息雷达的做法是先定业务目标，再采集去重，每条候选都带证据等级和最便宜的验证动作，够格的才推送。

- 每天要刷 GitHub 趋势、行业群、公众号、X，一百多条候选挑不出来的人
- 已经在用 Codex、Claude Code、WorkBuddy、豆包工作，想要一个能直接装上的个人信息雷达 skill
- 想用飞书 CLI（lark-cli）把日报推到自己的飞书群，而不是每天手动复制
- 想把「什么算值得看」写成规则，而不是每天凭感觉

## 关键词

半肥猫的 skill · 半肥猫 AI研习社 · 个人信息雷达 · 信息决策雷达 · 个人信息决策雷达 · 信息过载 · AI skill · Agent Skill · WorkBuddy 的 skill · 豆包工作的 skill · Codex skill · Claude Code skill · 飞书 CLI · lark-cli · 飞书日报推送 · 每日简报 · RSS 采集 · GitHub Trending 采集 · 知识库 · 决策支持 · 证据核验

## 常见问题

**半肥猫的 skill 有哪些？**
这个仓库是其中之一：个人信息决策雷达 skill。配套的研究文章与教程在 `docs/`。

**个人信息雷达的 skill 怎么用？**
先读 `docs/研究文章.md` 了解评分与核验口径，再按 `skills/signal-radar/SKILL.md` 装上，运行 `scripts/collect_sources.py` 采集，最后 `scripts/push_to_feishu.py --dry-run` 预览。

**WorkBuddy 的 skill 怎么装？**
把 `skills/signal-radar/` 复制到 WorkBuddy 的 Skills 目录（本机实测在 `~/.workbuddy/skills/` 下）。装完确认实际加载的是哪个版本，同名导入不等于新版生效。

**豆包工作的 skill 怎么装？**
把 `skills/signal-radar/` 按豆包工作的 Skill 目录结构放进去，用同一个 SKILL.md。豆包工作侧的重点是确认加载到了最新规则。

**飞书 CLI 怎么把日报推到群里？**
装官方 [Lark CLI](https://github.com/larksuite/cli)，用 `lark-cli im +chat-search` 找到目标会话，配好环境变量后 `lark-cli im +messages-send --markdown @report.md`。详细六步见 `docs/飞书CLI设置与日报推送教程.md`。

## 快速开始

1. 阅读 [`docs/研究文章.md`](docs/研究文章.md) 了解方法论。
2. 阅读 [`docs/飞书CLI设置与日报推送教程.md`](docs/飞书CLI设置与日报推送教程.md) 配置每日流程。
3. 安装官方 [Lark CLI](https://github.com/larksuite/cli)，登录并确认目标会话。
4. 复制 `config/sources.example.json` → `config/sources.json`、`config/profile.example.json` → `config/profile.json`。
5. 安装 `skills/signal-radar/` 到对应 Agent Skills 目录。
6. 先运行采集与 `push_to_feishu.py --dry-run`，检查后再启用定时任务。

## 测试

仅 Python 标准库：

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile scripts/*.py
```

## 安全

不要把个人配置、会话 ID、采集状态、报告、CLI 认证或任何密钥提交到仓库。首期只读采集；推送前配置明确的目标会话。脚本默认不发送到任何会话。

## 项目作者

紫鲸 AI · 半肥猫 · [www.zjai.ink](https://www.zjai.ink) · 微信公众号：半肥猫 AI研习社

<img src="assets/wechat-qr-half-feimao.jpg" alt="半肥猫 AI研习社 公众号二维码" width="220" />

扫码关注「半肥猫 AI研习社」。这套雷达的后续更新、踩坑记录和配套模板，先发在那里。
