# FamilyBond 家话

面向异地家庭与老人沟通场景的陪伴型 DeepAgent，基于 LangChain Deep Agents SDK。

系统由两个独立服务组成：

```
飞书用户
  ↓ 发消息
familybond-bot (端口 8000)    ← 飞书通道层，接收消息、回发消息
  ↓ POST /invoke
familybond-agent (端口 9000)  ← 智能处理层，DeepAgent 推理
  ↓ 返回 reply_text
familybond-bot
  ↓ 发回飞书
飞书用户
```

## 功能

- **概念追问 (clarify)**：将不熟悉的词语或概念转化为适合长辈理解的生活化表达
- **生活近况 (summarize)**：接住老人的日常表达，概括核心生活信息并保存
- **健康签到 (health)**：识别并记录血压、吃药等健康信息
- **消息转译 (translation)**：将年轻人的现代语境表达转译为老人友好的中文

## 目录结构

```
familybond/
├── agent.py              # DeepAgent 定义（tools + agent factory）
├── server.py             # FastAPI HTTP 服务，暴露 POST /invoke
├── storage.py            # 本地 JSON 读写封装
├── AGENTS.md             # Agent 身份与规则（长期记忆）
├── skills/               # 任务导向型处理说明
│   ├── clarify-for-elder/
│   ├── summarize-life-update/
│   └── parse-health-checkin/
├── data/                 # 业务数据（本地 JSON）
│   ├── family_context.json
│   ├── recent_updates.json
│   ├── health_logs.json
│   └── translation_logs.json
└── runtime/              # DeepAgent FilesystemBackend 目录
```

## 环境要求

- Python >= 3.11
- [uv](https://docs.astral.sh/uv/) 包管理器
- 智谱 AI API Key（GLM-5.1 模型）

## 安装

```bash
cd familybond
uv sync
```

## 配置

复制 `.env.example` 为 `.env` 并填入 API Key：

```bash
cp .env.example .env
```

`.env` 需要包含：

```bash
# 必填：智谱 AI API Key
OPENAI_API_KEY=your_key_here
```

可选环境变量：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `AGENT_PORT` | `9000` | HTTP 服务监听端口 |

## 启动服务

```bash
# 方式一：直接运行
uv run python server.py

# 方式二：通过 uvicorn 启动（可自定义参数）
uv run uvicorn server:app --host 0.0.0.0 --port 9000 --reload
```

启动后会看到：

```
INFO:     Uvicorn running on http://0.0.0.0:9000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

> 服务启动时会初始化 DeepAgent（加载 AGENTS.md、skills、tools），首次启动可能需要几秒钟。

## API 接口

### POST /invoke

接收标准化的用户消息，调用 DeepAgent 处理，返回回复。

**请求**

```
POST /invoke
Content-Type: application/json
```

```json
{
  "user_id": "ou_xxx",
  "user_role": "elder",
  "message": "什么是普拉提？",
  "source": "feishu",
  "session_id": "feishu_ou_xxx"
}
```

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `user_id` | string | 是 | - | 用户唯一标识（飞书 open_id） |
| `user_role` | string | 否 | `"elder"` | 用户角色，当前支持 `elder` / `young` |
| `message` | string | 是 | - | 纯文本消息内容 |
| `source` | string | 否 | `"feishu"` | 消息来源渠道 |
| `session_id` | string | 否 | `""` | 会话标识，用于未来做会话隔离 |

**响应**

```json
{
  "reply_text": "普拉提是一种比较缓和的锻炼方式...",
  "intent": "clarify",
  "memory_written": false,
  "meta": {
    "used_context": true
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `reply_text` | string | 最终回复文本，稳定存在且为字符串 |
| `intent` | string | 识别出的任务类型：`clarify` / `summarize` / `health` / `translation` |
| `memory_written` | bool | 是否写入了本地数据文件 |
| `meta` | object | 预留扩展字段 |

### 手动测试

```bash
curl -X POST http://localhost:9000/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "user_role": "elder",
    "message": "什么是普拉提？",
    "source": "feishu",
    "session_id": "test_session"
  }'
```

## CLI 模式（调试用）

无需启动服务，直接在命令行与 Agent 交互：

```bash
# 老人问概念
uv run python agent.py --role elder "什么是普拉提？"

# 老人描述近况
uv run python agent.py --role elder "今天去给菜浇水了，下午有点累。"

# 老人健康签到
uv run python agent.py --role elder "今天血压 135/85，药也吃了。"

# 年轻人消息转译
uv run python agent.py --role young "我今天加班，还去练普拉提了。"
```

## 与 familybond-bot 联调

完整链路需要同时启动两个服务。

**Step 1：启动 Agent 服务**

```bash
cd ~/Desktop/Hackerthon/familybond
uv run python server.py
```

**Step 2：验证 Agent 可用**

```bash
curl -s -X POST http://localhost:9000/invoke \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","message":"你好"}'
```

确认返回包含 `reply_text` 字段。

**Step 3：配置并启动 Bot**

确保 lark-bot 的 `.env` 中配置了 `AGENT_BASE_URL`：

```bash
# lark-bot/.env
APP_ID=your_app_id
APP_SECRET=your_app_secret
AGENT_BASE_URL=http://localhost:9000
```

```bash
cd ~/Desktop/Hackerthon/lark-bot
source .venv/bin/activate
pip install -r requirements.txt
python bot.py
```

**Step 4：飞书端测试**

在飞书中找到 Bot，发送：

```
什么是普拉提？
```

如果一切正常，Bot 会返回一段适合长辈理解的解释。

## 数据说明

Agent 会在运行过程中读写 `data/` 目录下的本地 JSON 文件：

| 文件 | 用途 | 写入时机 |
|------|------|----------|
| `family_context.json` | 家庭成员资料与共享背景 | 手动维护 |
| `recent_updates.json` | 老人生活近况记录 | `summarize` 意图时写入 |
| `health_logs.json` | 健康签到记录 | `health` 意图时写入 |
| `translation_logs.json` | 消息转译记录 | `translation` 意图时写入 |

这些数据由 Agent 的 tools 自动管理，不需要手动编辑。

## 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| Agent 编排 | DeepAgent SDK | memory, skills, tools, backend |
| LLM | 智谱 GLM-5.1 | 通过 OpenAI 兼容接口调用 |
| HTTP 服务 | FastAPI + Uvicorn | 提供 /invoke 接口 |
| 持久化 | FilesystemBackend | runtime/ 目录 |
| 业务存储 | 本地 JSON | data/ 目录 |
| 飞书通道 | lark-oapi (WebSocket) | familybond-bot 项目 |

## 常见问题

**Q: 启动报 `OPENAI_API_KEY` 相关错误？**

确认 `.env` 文件存在且包含有效的 API Key。智谱 AI 的 Key 可在 [open.bigmodel.cn](https://open.bigmodel.cn) 申请。

**Q: Bot 调用 Agent 后返回兜底文案？**

检查 agent 服务是否已启动，以及 lark-bot 的 `AGENT_BASE_URL` 是否正确指向 agent 地址（默认 `http://localhost:9000`）。

**Q: 如何查看 Agent 的推理过程？**

Agent 以 `debug=True` 模式运行，控制台会打印每一步的中间状态（tool calls、model 响应等）。HTTP 请求的日志也会在 uvicorn 输出中显示。
