# Memory Policy

这是当前记忆系统的轻量策略层，建立在：

- Markdown 文件（真源头）
- QMD（文件索引 / 文本检索）
- LanceDB（结构化记忆镜像）

## 分层

### 1. inbox
适合：
- 临时信息
- 刚发生但尚未确认的重要信息
- 未判断是否长期保留的内容

### 2. episodic
适合：
- `memory/YYYY-MM-DD.md`
- 每日发生的事件、操作、上下文
- 近期工作过程

### 3. semantic
适合：
- `MEMORY.md`
- 稳定的身份信息、长期偏好、长期项目、明确规则

## 状态

- `candidate`：候选记忆，通常来自 daily/inbox
- `confirmed`：已确认、适合长期使用
- `archived`：保留但降权
- `superseded`：被新信息覆盖

## 写入原则

优先写入 daily：
- 今天发生的事
- 最近完成的工作
- 尚未确认是否长期重要的信息

提升到 long-term：
- 用户明确说“记住这个”
- 会稳定影响行为的偏好/规则
- 长期有效的环境信息
- 已重复出现、被多次验证的事实

## 检索原则

检索时同时考虑：
- exact keyword hit
- summary/title 命中
- importance
- confidence
- layer priority（semantic > episodic > inbox）

优先返回：
1. 长期稳定事实
2. 最近强相关事件
3. 需要时再回到原始 daily 细节

## 后续升级方向

以后如果 embedding provider 稳定，可在 LanceDB 中增加：
- `vector`
- semantic similarity
- rerank
- 自动晋升/降权
