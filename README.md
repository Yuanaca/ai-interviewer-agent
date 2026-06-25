# Interview Intelligence - AI 智能面试系统

基于 **LangGraph + FastAPI + Vue 3 + MongoDB + ChromaDB (RAG)** 的全栈智能面试问答系统。

## 🏗 项目架构

```
agnet/
├── backend/                    # Python 后端
│   ├── main.py                # FastAPI 入口
│   ├── config.py              # 全局配置
│   ├── requirements.txt       # Python 依赖
│   ├── graph/                 # LangGraph 面试状态图
│   │   ├── state.py           # 状态定义
│   │   ├── interview_graph.py # 图编排
│   │   └── nodes/             # 图节点
│   │       └── interview_nodes.py
│   ├── routers/               # API 路由
│   │   ├── interview.py       # 面试会话
│   │   ├── jobs.py            # 职位管理
│   │   └── knowledge.py       # 知识库 + RAG
│   ├── services/              # 服务层
│   │   ├── llm_service.py     # LLM 抽象层
│   │   ├── mongodb.py         # MongoDB 数据库
│   │   └── rag_service.py     # RAG 向量检索
│   └── models/
│       └── schemas.py         # Pydantic 数据模型
│
├── frontend/                  # Vue 3 前端
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── src/
│       ├── main.js
│       ├── App.vue
│       ├── style.css
│       ├── router/index.js
│       ├── stores/
│       │   ├── settings.js    # LLM 配置 Store
│       │   └── interview.js   # 面试状态 Store
│       ├── api/index.js       # API 客户端
│       └── views/
│           ├── Dashboard.vue
│           ├── InterviewRoom.vue
│           ├── JobPositions.vue
│           ├── KnowledgeBase.vue
│           ├── Reports.vue
│           └── Settings.vue
│
└── stitch_langgraph_rag_interviewer/  # 原始前端模板（参考）
```

## 🚀 快速启动

### 前置条件

- Python 3.10+
- Node.js 18+
- MongoDB（本地运行 `mongod`）
- （可选）ChromaDB 向量数据库已内嵌，无需额外安装

### 1. 启动后端

```powershell
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动后端 (http://localhost:8000)
python main.py
```

API 文档自动生成：http://localhost:8000/docs

### 2. 启动前端

```powershell
cd frontend

# 安装依赖
npm install

# 启动开发服务器 (http://localhost:5173)
npm run dev
```

前端开发服务器会自动代理 `/api` 请求到后端 `localhost:8000`。

### 3. 配置使用

1. 打开 http://localhost:5173
2. 进入「设置」页面
3. 选择模型提供商（OpenAI / DeepSeek / 智谱 / 通义千问等）
4. 填入 API Key
5. 进入「面试室」开始 AI 面试

## 🔧 关键技术选型

| 层次 | 技术 | 说明 |
|------|------|------|
| 后端框架 | FastAPI | 高性能异步 Web 框架 |
| 编排引擎 | LangGraph | 面试流程状态图编排 |
| 数据库 | MongoDB (Motor) | 异步文档存储 |
| 向量检索 | ChromaDB | RAG 语义搜索 |
| LLM | 多模型支持 | OpenAI / DeepSeek / 智谱 / 千问 / Ollama |
| 前端框架 | Vue 3 + Vite | SPA 单页应用 |
| UI 样式 | Tailwind CSS | 暗色主题 + Glassmorphism |
| 状态管理 | Pinia | Vue 3 官方状态管理 |

## 🔄 LangGraph 面试流程图

```
[INIT]
  ↓
[RESUME_ANALYSIS]    ← 解析候选人简历
  ↓
[RAG_RETRIEVAL]      ← 知识库语义检索
  ↓
[QUESTION_GENERATION] ← 生成个性化面试题
  ↓
[ASKING] ←→ [EVALUATING] → [NEXT_QUESTION]  (循环 N 次)
                              ↓
                    [REPORT_GENERATION]      ← 生成综合报告
                              ↓
                        [COMPLETED]
```

## 📡 API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/interview/create` | POST | 创建面试会话 |
| `/api/interview/answer` | POST | 提交回答（触发评估+下一题） |
| `/api/interview/state/{id}` | GET | 获取会话状态 |
| `/api/interview/report/{id}` | GET | 获取面试报告 |
| `/api/jobs/` | CRUD | 职位管理 |
| `/api/knowledge/` | CRUD | 知识库管理 |
| `/api/knowledge/search` | POST | RAG 语义搜索 |
| `/api/knowledge/rebuild-index` | POST | 重建向量索引 |

## 🎨 设计系统

采用暗色主题 + Glassmorphism 设计风格：
- 背景色：`#0b1326` (Deep Navy)
- 主色：`#c3c0ff` (Indigo)
- 强调色：`#b3c5ff` (AI Blue) / `#4edea3` (Cyber Green)
- 字体：Inter + JetBrains Mono
