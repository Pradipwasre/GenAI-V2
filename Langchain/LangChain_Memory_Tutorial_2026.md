# LangChain Memory — Complete Teaching Guide (2026)

> **For:** Freshers learning LangChain (Day 2 — after PromptTemplate / ChatPromptTemplate / MessagesPlaceholder)
> **Prerequisite:** `.env` file with `OPENAI_API_KEY=sk-...`

---

## 0. First, the Big Mindset Shift (5 minutes of class time)

In old LangChain, memory was a **plug-in object** you attached to a chain:

```text
ConversationBufferMemory          → keep everything
ConversationBufferWindowMemory    → keep last K turns
ConversationSummaryMemory         → summarize old turns
```

These classes are now **legacy / deprecated** (scheduled for removal in LangChain 2.0) [^8^]. The modern mental model is simpler and maps exactly to your diagram:

| Question | Modern answer |
|---|---|
| Where does short-term memory live? | In the **Agent State** |
| What saves the state between turns? | A **Checkpointer** |
| How do I separate conversations? | A **`thread_id`** |
| Where does long-term memory live? | A **Store** (works across threads) |
| What are the 3 long-term types? | **Semantic** (facts), **Episodic** (experiences), **Procedural** (rules/behavior) |

One-line mapping for the whiteboard:

```text
ConversationBufferMemory        → MessagesState + Checkpointer (full history)
ConversationBufferWindowMemory  → trim_messages() before calling the LLM
ConversationSummaryMemory       → SummarizationNode (langmem) / summary field in state
```

---

## 1. Setup (same for every practice file)

```bash
pip install langchain langchain-openai langgraph langmem python-dotenv
```

**.env** (in the same folder as your scripts):

```ini
OPENAI_API_KEY=sk-your-key-here
```

Every practice file starts the same way:

```python
from dotenv import load_dotenv
load_dotenv()   # reads OPENAI_API_KEY from .env automatically

from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
```

---

# PART 1 — SHORT-TERM MEMORY (Current Thread)

## 1.1 Concept: Agent State + Checkpointer

**What it is:** The full message history of *one conversation*, saved automatically after every turn.

**How it works:**
1. Your agent's state holds `messages` (this is the "Agent State" box in your diagram).
2. You compile the graph with a **checkpointer** → after every run, the state is snapshotted.
3. You pass a **`thread_id`** in the config → LangGraph reloads that thread's messages before the next turn [^1^][^6^].

**Where to use it:**
- Any multi-turn chatbot (support bot, tutor bot, interviewer)
- Anything where the user says *"yes"*, *"make it shorter"*, *"what about the second one?"* — pronouns and follow-ups only work with memory
- Human-in-the-loop flows (pause → resume later)

**Where NOT to use it alone:**
- Remembering a user *across different sessions* (that's long-term memory — Part 2)
- Very long conversations without any trimming (token cost explodes — see 1.3 / 1.4)

### ✅ Practice 1 — `01_short_term_memory_checkpointer.py`

```python
"""Practice 1 — Short-term memory: Agent State + Checkpointer"""
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import InMemorySaver

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# A node = one step of the agent. It receives the FULL state (all past
# messages of this thread, restored by the checkpointer).
def chatbot(state: MessagesState):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}   # appended to state automatically

builder = StateGraph(MessagesState)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

# ★ THE memory line: compile with a checkpointer
graph = builder.compile(checkpointer=InMemorySaver())

# ★ thread_id = "which conversation is this?"
config = {"configurable": {"thread_id": "class-demo-1"}}

r1 = graph.invoke(
    {"messages": [HumanMessage(content="Hi, my name is Rahul and I love biryani.")]},
    config,
)
print("AI:", r1["messages"][-1].content)

# Turn 2 — we only send the NEW message. The checkpointer reloads turn 1.
r2 = graph.invoke(
    {"messages": [HumanMessage(content="What is my name and what food do I love?")]},
    config,
)
print("AI:", r2["messages"][-1].content)   # → remembers Rahul + biryani

# A DIFFERENT thread_id = a fresh, empty conversation
config2 = {"configurable": {"thread_id": "class-demo-2"}}
r3 = graph.invoke(
    {"messages": [HumanMessage(content="What is my name?")]}, config2
)
print("AI (new thread):", r3["messages"][-1].content)   # → doesn't know
```

**Classroom demo tip:** run it once, then comment out `checkpointer=InMemorySaver()` (compile with no checkpointer) and run again — turn 2 fails. Students *see* what the checkpointer does.

> ⚠️ `InMemorySaver` lives in RAM — it dies when the script ends. Perfect for class; for production use a DB-backed one (Section 3.2).

---

## 1.2 The Problem With Full History

Full history (old `ConversationBufferMemory`) has two costs:
- **Tokens/money** — every turn resends the whole transcript
- **Context limit** — long chats eventually overflow

The modern replacements for the old window/summary classes are **transformations applied to state before the LLM call** — not separate memory objects.

---

## 1.3 Window Memory → `trim_messages()` (replaces ConversationBufferWindowMemory)

**What it is:** Keep only the most recent N tokens/messages; silently drop the old ones.

**Where to use it:**
- High-volume, chit-chat-style bots where old turns don't matter (FAQ bots, casual assistants)
- When you want a hard, predictable token budget
- Trade-off to state out loud in class: *cheap and fast, but the bot "forgets" old details — just like the old WindowMemory.*

### ✅ Practice 2 — `02_window_memory_trim.py`

```python
"""Practice 2 — Window memory with trim_messages (modern ConversationBufferWindowMemory)"""
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.messages.utils import trim_messages, count_tokens_approximately
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import InMemorySaver

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def chatbot(state: MessagesState):
    # ★ Keep only the recent ~200 tokens before calling the LLM.
    #    The checkpointer still stores the FULL history —
    #    trimming only affects what the LLM sees.
    recent = trim_messages(
        state["messages"],
        strategy="last",
        token_counter=count_tokens_approximately,
        max_tokens=200,
        start_on="human",   # never cut in the middle of a turn
    )
    return {"messages": [llm.invoke(recent)]}

builder = StateGraph(MessagesState)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)
graph = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "window-demo"}}
graph.invoke({"messages": [HumanMessage("My name is Rahul.")]}, config)

# Push many long messages so the first one falls out of the window...
for i in range(10):
    graph.invoke(
        {"messages": [HumanMessage(f"Tell me an interesting fact number {i}.")]}, config
    )

out = graph.invoke({"messages": [HumanMessage("What is my name?")]}, config)
print("AI:", out["messages"][-1].content)   # → forgot! It fell out of the window.
```

**Classroom discussion:** *"The checkpointer remembered everything, but the LLM only saw the window. Memory for storage ≠ memory for the prompt."* That distinction is the whole lesson.

---

## 1.4 Summary Memory → `SummarizationNode` (replaces ConversationSummaryMemory)

**What it is:** When the history grows past a threshold, an LLM compresses older turns into a running summary; the model then sees *summary + recent messages*.

**Where to use it:**
- Long, meaningful conversations where old details matter: tutoring sessions, therapy/coaching bots, long support tickets
- The middle ground: cheaper than full history, forgets less than a window

### ✅ Practice 3 — `03_summary_memory.py`

```python
"""Practice 3 — Summary memory with langmem's SummarizationNode
   (modern ConversationSummaryMemory)"""
from typing import TypedDict
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import AnyMessage
from langchain_core.messages.utils import count_tokens_approximately
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.checkpoint.memory import InMemorySaver
from langmem.short_term import SummarizationNode, RunningSummary

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

class State(MessagesState):
    context: dict[str, RunningSummary]   # holds the running summary

class LLMInputState(TypedDict):          # private input for the model node
    summarized_messages: list[AnyMessage]
    context: dict[str, RunningSummary]

# ★ This node summarizes old messages once the history passes the limit
summarization_node = SummarizationNode(
    token_counter=count_tokens_approximately,
    model=llm.bind(max_tokens=256),
    max_tokens=512,
    max_tokens_before_summary=512,   # summarize when history exceeds this
    max_summary_tokens=256,
)

def call_model(state: LLMInputState):
    response = llm.invoke(state["summarized_messages"])
    return {"messages": [response]}

builder = StateGraph(State)
builder.add_node(call_model)
builder.add_node("summarize", summarization_node)
builder.add_edge(START, "summarize")        # summarize FIRST...
builder.add_edge("summarize", "call_model") # ...then call the model
graph = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "summary-demo"}}
graph.invoke({"messages": "Hi, my name is Rahul."}, config)
graph.invoke({"messages": "I'm preparing for a LangChain teaching job."}, config)
for topic in ["prompt templates", "chains", "agents"]:
    graph.invoke({"messages": f"Explain {topic} briefly."}, config)

final = graph.invoke({"messages": "What is my name, and what am I preparing for?"}, config)
final["messages"][-1].pretty_print()          # → still remembers Rahul
print("\nRunning summary:", final["context"]["running_summary"].summary)
```

**Key line for students:** the summary lives in **state** (`context`), and state is saved by the **checkpointer** — so even the *summary* survives across turns. Same mechanism, one extra field.

---

# PART 2 — LONG-TERM MEMORY (Across Threads)

## 2.1 Concept: The Store

**The limitation to show first:** everything in Part 1 dies with the `thread_id`. A user who chats on Monday and returns on Friday (new thread) is a stranger.

**The fix:** a **Store** — a key-value database that lives *outside* any thread [^6^].

```text
Checkpointer  →  scoped to ONE thread   →  short-term
Store         →  shared ACROSS threads  →  long-term
```

Three store operations cover everything:

```python
store.put(namespace, key, value)     # write
store.get(namespace, key)            # read one
store.search(namespace, query=...)   # read many / semantic search
```

**Namespaces = folders.** The standard convention is to scope by user or agent:

```python
("users", user_id, "facts")        # this user's facts
("agent", "support-bot", "episodes")  # this agent's experiences
```

**Where to use it:** user profiles & preferences, personalization across sessions, agents that improve with experience, shared team knowledge.

---

## 2.2 Semantic Memory — Facts & Preferences

**What it is:** *Things the agent knows.* "Rahul prefers dark mode." "Priya's company uses Postgres." Modeled after human semantic memory [^5^].

**Where to use it:**
- Personalization ("remember my dietary preferences" in a food app)
- User profiles that survive new sessions
- CRM-style bots that recall company/role/project details

### ✅ Practice 4 — `04_semantic_memory_store.py`

```python
"""Practice 4 — Long-term SEMANTIC memory: facts across threads"""
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from langgraph.store.base import BaseStore

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
store = InMemoryStore()

# ── Step A: the raw Store API (show this on its own first) ──
store.put(("users", "rahul", "facts"), key="name",     value={"data": "Rahul"})
store.put(("users", "rahul", "facts"), key="fav_food", value={"data": "biryani"})

print("What's in the store for rahul:")
for item in store.search(("users", "rahul", "facts")):
    print(f"  {item.key}: {item.value['data']}")

# ── Step B: an agent that reads its memories every turn ──
def chatbot(state: MessagesState, config: RunnableConfig, *, store: BaseStore):
    user_id = config["configurable"]["user_id"]

    # ★ Load long-term memories — works no matter which thread we're in
    memories = store.search(("users", user_id, "facts"))
    memory_text = "\n".join(f"- {m.key}: {m.value['data']}" for m in memories) \
                  or "No memories yet."

    system = SystemMessage(content=(
        "You are a friendly tutor.\n"
        f"Known facts about this user:\n{memory_text}"
    ))
    return {"messages": [llm.invoke([system] + state["messages"])]}

builder = StateGraph(MessagesState)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

# ★ Compile with BOTH: checkpointer (short-term) + store (long-term)
graph = builder.compile(checkpointer=InMemorySaver(), store=store)

# Session 1 (Monday)
cfg1 = {"configurable": {"thread_id": "monday", "user_id": "rahul"}}
graph.invoke({"messages": [HumanMessage("Let's practice Python loops.")]}, cfg1)

# Session 2 (Friday) — NEW thread_id, SAME user_id
cfg2 = {"configurable": {"thread_id": "friday", "user_id": "rahul"}}
out = graph.invoke(
    {"messages": [HumanMessage("What do you remember about me?")]}, cfg2
)
print("\nAI (new thread):", out["messages"][-1].content)   # → knows Rahul + biryani
```

**The one thing students must internalize:** `thread_id` changed, `user_id` didn't. The store is keyed by *who*, not by *which conversation*.

> In a real app, an LLM extraction step writes facts automatically (see `langmem` in 2.5). For class, explicit `store.put()` keeps the mechanism visible.

---

## 2.3 Episodic Memory — Past Experiences

**What it is:** *Things the agent did.* Complete past episodes: situation → action → result. Usually retrieved as few-shot examples so the agent repeats what worked [^5^].

**Where to use it:**
- Support bots: "last time a refund request looked like this, this reply worked"
- Coding agents that recall how they solved a similar bug
- Any agent you want to improve from its own track record

### ✅ Practice 5 — `05_episodic_memory.py`

```python
"""Practice 5 — EPISODIC memory: learning from past experiences"""
from uuid import uuid4
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.store.memory import InMemoryStore

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ★ index=... turns on SEMANTIC search (find episodes by meaning, not key)
store = InMemoryStore(
    index={"dims": 1536, "embed": "openai:text-embedding-3-small"}
)

# ── Step A: save two past support episodes (what worked) ──
episodes = [
    {"situation": "Customer angry about late delivery",
     "response": "Apologized sincerely, gave 10% coupon, escalated to logistics",
     "result": "Customer satisfied, 5-star review"},
    {"situation": "Customer asked for refund on used item",
     "response": "Explained policy politely, offered exchange instead",
     "result": "Customer accepted exchange"},
]
for ep in episodes:
    store.put(
        ("agent", "support-bot", "episodes"),
        key=str(uuid4()),
        value=ep,
    )

# ── Step B: a NEW situation arrives — recall similar episodes ──
new_ticket = "My package arrived damaged and I want my money back"

similar = store.search(
    ("agent", "support-bot", "episodes"),
    query=new_ticket,     # ★ semantic search over past experiences
    limit=2,
)

few_shot = "\n\n".join(
    f"Past situation: {m.value['situation']}\n"
    f"What worked: {m.value['response']}\n"
    f"Outcome: {m.value['result']}"
    for m in similar
)

answer = llm.invoke([
    SystemMessage(content=(
        "You are a support agent. Here is how similar cases were "
        f"handled successfully:\n\n{few_shot}"
    )),
    HumanMessage(content=new_ticket),
])
print("AI:", answer.content)
```

**Teaching point:** this is *RAG over the agent's own history* — the store embeds each episode, so "damaged package / money back" retrieves the refund-and-delivery episodes even though no keywords match exactly.

---

## 2.4 Procedural Memory — Rules & Behavior

**What it is:** *How the agent behaves.* The system prompt itself lives in the store, and gets rewritten from feedback. The agent literally reprograms itself [^5^].

**Where to use it:**
- Agents that adapt their tone/format to a user or team ("shorter answers", "always show code")
- Self-improving assistants: feedback in → better instructions out
- Anything you'd otherwise hard-code and redeploy

### ✅ Practice 6 — `06_procedural_memory.py`

```python
"""Practice 6 — PROCEDURAL memory: the agent improves its own instructions"""
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.store.memory import InMemoryStore

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
store = InMemoryStore()

NS = ("agents", "py-tutor", "prompts")

# ── Step A: the system prompt lives in the STORE, not in the code ──
store.put(NS, key="system_prompt",
          value={"text": "You are a Python tutor. Explain concepts clearly."})

def ask(question: str) -> str:
    current = store.get(NS, "system_prompt").value["text"]   # ★ read rules
    response = llm.invoke([
        SystemMessage(content=current),
        HumanMessage(content=question),
    ])
    return response.content

def update_from_feedback(feedback: str):
    """Rewrite the stored instructions to incorporate feedback."""
    current = store.get(NS, "system_prompt").value["text"]
    new_prompt = llm.invoke(
        "Here are an assistant's current instructions:\n"
        f"{current}\n\n"
        f"A user gave this feedback: {feedback}\n\n"
        "Rewrite the instructions to incorporate the feedback. "
        "Keep them short. Return only the new instructions."
    )
    store.put(NS, key="system_prompt", value={"text": new_prompt.content})  # ★ write rules

# ── Demo ──
print("BEFORE feedback:")
print(ask("What is a Python decorator?"))

update_from_feedback(
    "Your answers are too long. Use a short code example every time, "
    "and explain in max 3 sentences."
)

print("\nAFTER feedback (same question, new behavior):")
print(ask("What is a Python decorator?"))

print("\nStored prompt now:\n", store.get(NS, "system_prompt").value["text"])
```

**Teaching point:** semantic memory changes what the agent *knows*; procedural memory changes what the agent *is*. And because it's in the store, the improved behavior applies to **every future thread** automatically.

---

## 2.5 The Shortcut: `langmem` (mention at the end)

Everything in 2.2–2.4 was done "by hand" so students see the mechanism. In production, the **`langmem`** library automates extraction, deduplication, and updating [^5^][^10^]:

```python
from langmem import create_memory_store_manager

manager = create_memory_store_manager(
    "openai:gpt-4o-mini",
    namespace=("chat", "{user_id}"),
    instructions="Extract the user's preferences and facts in detail",
)

# after a conversation:
manager.invoke({"messages": conversation},
               config={"configurable": {"user_id": "rahul"}})
# → facts are extracted and written to the store automatically
```

It also ships hot-path tools (`create_manage_memory_tool`, `create_search_memory_tool`) that let the agent decide *itself* when to save or recall [^5^]. One slide is enough here — the goal is that students know it exists, not that they memorize it.

---

# PART 3 — Wrap-Up Material

## 3.1 Decision Table (the "where to use" slide)

| Situation | Memory to use | Mechanism |
|---|---|---|
| Follow-ups in one chat ("make it shorter") | Short-term | `MessagesState` + checkpointer + `thread_id` |
| Long chat, tight token budget, old turns don't matter | Window | `trim_messages()` before the LLM call |
| Long chat, old details DO matter | Summary | `SummarizationNode` / summary in state |
| Remember user preferences next week | Long-term **semantic** | `store.put/search` under `("users", user_id, ...)` |
| Repeat what worked before | Long-term **episodic** | Store episodes + semantic search as few-shots |
| Agent should adapt its behavior from feedback | Long-term **procedural** | Store + rewrite the system prompt |
| Real deployed app | All of the above | DB checkpointer + DB store, often via `langmem` |

## 3.2 Production Notes (one slide)

- `InMemorySaver` / `InMemoryStore` = RAM only. For production, swap in `PostgresSaver` / `AsyncPostgresSaver` (or MongoDB / Redis checkpointers) — the graph code doesn't change, only the checkpointer object [^1^][^6^].
- Typical real agent = **checkpointer (thread state) + store (user memory)**, compiled together [^6^].
- Keep store keys clean and fixed (`language_preference`, `timezone`) — free-form keys become undebuggable fast [^3^].

## 3.3 Common Student Mistakes

1. **Forgetting `thread_id`** → "memory doesn't work" (every invoke starts fresh).
2. **Expecting the checkpointer to remember across threads** → that's the store's job.
3. **Trimming ≠ deleting** — the checkpointer keeps full history; trim only affects what the LLM sees.
4. **Using old `ConversationBufferMemory` from a 2023 tutorial** — deprecated; point them to state + checkpointer instead [^2^][^8^].

## 3.4 Homework Exercise

Build a **study-buddy bot** that combines all layers:
1. Short-term memory via checkpointer (`thread_id` per study session).
2. Summarize after 8 messages.
3. Semantic memory: remember the student's name, exam date, weak topics (store, keyed by `user_id`).
4. Procedural memory: after feedback like *"explain more simply"*, update the stored system prompt.
5. Test: start session 2 on a new thread — the bot should greet the student by name and recall the weak topics.

---

## Practice Files (in `langchain-memory-practice/`)

| File | Covers |
|---|---|
| `01_short_term_memory_checkpointer.py` | State + checkpointer + thread_id |
| `02_window_memory_trim.py` | `trim_messages` window memory |
| `03_summary_memory.py` | `SummarizationNode` summary memory |
| `04_semantic_memory_store.py` | Facts across threads |
| `05_episodic_memory.py` | Experience recall with semantic search |
| `06_procedural_memory.py` | Self-updating system prompt |

---

[^1^]: https://docs.langchain.com/oss/python/langgraph/add-memory
[^2^]: https://db0.ai/blog/langchain-memory-deprecated
[^3^]: https://machinelearningplus.com/gen-ai/langgraph-memory-systems-short-long-term-conversation/
[^5^]: https://rywalker.com/research/langmem
[^6^]: https://docs.langchain.com/oss/python/langgraph/persistence
[^8^]: https://oneuptime.com/blog/post/2026-01-27-langchain-memory/view
[^10^]: https://developer.mamezou-tech.com/en/blogs/2025/02/26/langmem-intro/
