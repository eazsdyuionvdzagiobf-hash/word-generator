# Memory System (QMD + LanceDB)

当前采用双层记忆：

- **QMD**：OpenClaw 的主 memory backend，负责 Markdown 文件索引与文本检索
- **LanceDB**：本地结构化记忆镜像，存文本与元数据，暂不依赖 embeddings

## 当前实现

### 真源头

- `MEMORY.md`
- `memory/*.md`

### 文件索引层

- QMD 负责 collection / 文件级检索
- 已禁用 QMD embedding 路径，避免 CPU-only 本地模型带来的高延迟与不稳定

### 结构化层

- LanceDB 数据库目录：`data/memory-lancedb`
- 表名：`memory_text`

当前结构化字段包括：

- `source_file`
- `title`
- `memory_type`
- `memory_layer`
- `status`
- `summary`
- `tags`
- `importance`
- `confidence`
- `text`
- `created_at`
- `updated_at`
- `last_seen_at`
- `checksum`

## 脚本

### 1. 同步 Markdown 记忆到 LanceDB

```bash
python3 scripts/lancedb_memory_sync.py
```

### 2. 搜索 LanceDB 记忆镜像

```bash
python3 scripts/lancedb_memory_search.py Telegram
```

### 3. 混合检索（QMD + LanceDB）

```bash
python3 scripts/memory_hybrid_search.py Telegram
```

## Memory Policy

详见：`memory-policy.md`

核心思路：

- `daily` → `episodic`
- `MEMORY.md` → `semantic`
- long-term 记忆默认 `confirmed`
- daily 记忆默认 `candidate`
- 检索时综合 exact match、summary/title 命中、importance、confidence、layer priority

## 说明

当前 LanceDB 是**结构化文本记忆库**，不是语义向量记忆库。

也就是说目前支持：

- 本地存储
- 元数据字段
- 文本 contains 搜索
- 混合检索底座
- 后续升级为 embedding/vector search 的数据底座

以后如果补上稳定的 embedding provider（如 Ollama / OpenAI-compatible embeddings / 其他本地 embedding 管道），可以直接在这套 LanceDB 结构上继续升级。
