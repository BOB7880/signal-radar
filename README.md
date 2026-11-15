# Signal Radar · 信息决策雷达

把个人业务目标转成一套可追溯的资讯筛选、核验、评分与行动流程。跨平台 Skill 适配 Codex、Claude Code、腾讯 WorkBuddy；脚本支持公开 RSS/GitHub Release 采集和通过官方 `lark-cli` 推送 Markdown 到飞书。

> Skill 是工作流规则；脚本提供可重复的采集与推送；定时器由 Codex/WorkBuddy/操作系统提供。仓库不会承诺 Skill 单独运行就能联网或每日唤醒。

## 项目资料

- 公司：紫鲸 AI
- 作者：半肥猫
- 网站：[www.zjai.ink](https://www.zjai.ink)
- 公众号：半肥猫 AI研习社（二维码见文末）
- 许可：MIT

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
