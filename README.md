# 🧠 Cottage Memory

*A lightweight structured memory system for AI agents, combining conversational state, persistent identity, and semantic recall.*

---

## ✨ Overview

Cottage Memory is a lightweight layered memory architecture designed for AI agents that need both:

- **short-term conversational context**
- **persistent identity and knowledge**
- **long-term semantic recall**

It separates memory into distinct roles rather than treating everything as one store.

---

## 🧩 Memory Model

Cottage Memory consists of **four distinct memory layers**:

---

### 🗂️ 1. Conversations Memory

Represents **discrete conversations**.

- Each conversation has an ID
- Conversations can be created, deleted, and restored
- A **default conversation** is used when none is specified

This is the top-level container for interaction history.

---

### 💬 2. Chat Memory

Stores **messages within a conversation**.

- Maintains ordered message history
- Tracks roles (`user`, `assistant`, etc.)
- Supports context window construction
- Enables truncation / eviction for token limits

This is the **working memory** of the agent.

---

### 🧬 3. Core Memory

Persistent **key/value memory** always available to the agent.

Two namespaces:

- `user` → facts/preferences about the user
- `agent` → system-level identity and behavior

#### Example:

```json
{
  "user": {
    "name": "Karen",
    "preferences": "prefers direct, thoughtful explanations"
  },
  "agent": {
    "persona": "helpful, reflective assistant"
  }
}
```

Core memory is:

- always included in context
- small, stable, and curated
- not subject to eviction

---

### 🔍 4. Contextual Memory (Vector Store)

Long-term, **semantic memory**.

- Stores embeddings of past content
- Enables similarity-based retrieval
- Used to surface relevant information dynamically

This is where the agent “remembers meaning,” not just text.

---

## 🏗️ Architecture

```text
Cottage_memory/
│
├── _db/
│   ├── models/                # database schemas + persistence logic
│   └── repositories/          # CRUD
│
├── memory/
│   ├── conversations_memory.py
│   ├── chat_memory.py
│   ├── core_memory.py
│   └── contextual_memory.py   # vector-backed
│
└── __init__.py
```

---

## ⚙️ Installation

```bash
pip install git+https://github.com/karencfisher/Cottage-memory
```

## Initialize database

```bash
cottage-init-db --db-path <path to DB>
```

---

## 🚀 Quick Example

```python
from Cottage_memory.memory import ConversationsMemory, ChatMemory, CoreMemory, ContextualMemory

# Initialize
conversations = ConversationsMemory()
chat = ChatMemory(40, 10)   # requires maximum number of messages, number to evict when full
core = CoreMemory()
context = ContextualMemory()

# Create or use conversation
conv_id = conversations.add_conversation('New Conversation')

# Get conversations - returns list of dictionaries {id: <id>, 'title': <title>}
convs = conversations.get_conversations() 

# Add chat message
chat.add_message(conv_id, role="user", content="I'm working on Cottage Memory.")

# Get messages - returns list of dictionaries {'role': <role>, 'content': <content>}
messages = chat.get_messages()

# Store core memory
core.add_memory(role="user", key="project", value="Cottage Memory system")

# Get memories - returns nested dictionaries 'user' and 'agent' sections
core_memories = core.get_memories()

# Store contextual memory (vector)
context.add_memory("User is building a layered memory system for AI agents.")

# Retrieve relevant context
results = context.query_memories("memory system")
```

---

## 🔄 Memory Roles at Runtime

When constructing context for the model:

1. **Core Memory** → always included
2. **Chat Memory** → recent messages within token limits
3. **Contextual Memory** → retrieved via semantic search
4. **Conversation** → determines scope of chat history

---

## 🪦 Deletion Model

Cottage Memory uses **soft deletion**:

- Conversations are not permanently removed
- Records are marked as deleted
- Can be restored later

This preserves history and supports recovery.

---

## 🧭 Design Philosophy

### Separation of Concerns
Different memory types serve different roles:
- chat ≠ identity ≠ long-term knowledge

### Local-First Simplicity
- SQLite-based persistence
- Inspectable, debuggable data
- Minimal external dependencies

### Agent-Oriented Design
Memory exists to support:
- reasoning
- continuity
- personalization

---

## 🧪 Status

🚧 Active development — structure is stable, APIs may evolve.

---

## 🌱 Future Directions

- Contextual memory curation / editing
- Memory summarization and compression
- Multi-agent memory separation
- Improved retrieval ranking
- Streaming + async integration

---

## 🪶 Closing

Cottage Memory models not just storage, but **how an agent maintains continuity across time**:

- what it is told (chat)
- what it knows (core)
- what it can recall (contextual)
