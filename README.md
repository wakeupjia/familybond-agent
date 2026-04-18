# FamilyBond 家话

面向异地家庭与老人沟通场景的陪伴型 DeepAgent，基于 LangChain Deep Agents SDK。

## 功能

- **概念追问**：将不熟悉的词语或概念转化为适合长辈理解的生活化表达
- **生活近况**：接住老人的日常表达，概括核心生活信息并保存
- **健康签到**：识别并记录血压、吃药等健康信息
- **消息转译**：将年轻人的现代语境表达转译为老人友好的中文

## 目录结构

```
familybond/
├── agent.py              # 主入口：DeepAgent 定义 + CLI
├── storage.py            # 本地 JSON 读写封装
├── AGENTS.md             # Agent 身份与规则（长期记忆）
├── skills/               # 任务导向型处理说明
│   ├── clarify-for-elder/
│   ├── summarize-life-update/
│   └── parse-health-checkin/
├── data/                 # 业务数据（本地 JSON）
└── runtime/              # DeepAgent FilesystemBackend 目录
```

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

## 使用

```bash
# 老人问概念
python agent.py --role elder "什么是普拉提？"

# 老人描述近况
python agent.py --role elder "今天去给菜浇水了，下午有点累。"

# 老人健康签到
python agent.py --role elder "今天血压 135/85，药也吃了。"

# 年轻人消息转译
python agent.py --role young "我今天加班，还去练普拉提了。"
```

## 技术栈

- **DeepAgent SDK** — Agent 编排框架（memory, skills, tools, backend）
- **ChatOpenAI** — 兼容 OpenAI API 的 LLM 接口
- **FilesystemBackend** — 本地文件系统持久化
- **本地 JSON** — 业务数据存储
