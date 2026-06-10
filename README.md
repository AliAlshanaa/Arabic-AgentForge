<div align="center">

<h1>🤖 Arabic AgentForge</h1>

<p><strong>The First Arabic-Native Multi-Agent Framework for Enterprise</strong></p>

[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Arabic First](https://img.shields.io/badge/Arabic-Native-orange?style=flat-square)](docs/arabic.md)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=flat-square&logo=docker)](docker-compose.yml)
[![Stars](https://img.shields.io/github/stars/ali-alshanaa/arabic-agentforge?style=flat-square)](https://github.com/ali-alshanaa/arabic-agentforge)

</div>

---

## What is Arabic AgentForge?

**Arabic AgentForge** is the first open-source multi-agent AI framework built natively for Arabic-speaking enterprises. It solves the fundamental problem every Arabic developer faces: **current AI tools don't truly understand Arabic**.

Unlike adapting English-first frameworks, Arabic AgentForge is built from the ground up with Arabic linguistics, Gulf dialects, RTL rendering, and enterprise ERP integrations in mind.

---

## Why This Exists

The Arabic NLP and enterprise AI space has a critical gap: 500M+ Arabic speakers, rapidly digitizing GCC enterprises, and **zero** production-grade open-source multi-agent frameworks designed for them.

Every existing solution — LangChain, AutoGen, CrewAI — is English-first with Arabic as an afterthought. This project changes that.

| Problem | Solution |
|---------|----------|
| LangChain has no RTL or Arabic context support | Arabic-native text pipeline built from scratch |
| No hallucination guard for Arabic content | Citation enforcement system tuned for Arabic |
| ERP tools don't integrate with AI in Arabic | Pre-built connectors for ERPNext and SAP |
| Data must stay within national borders | Full local deployment via Docker |

---

## Core Features

- 🔤 **Arabic-Native NLP** — Full diacritics support, Gulf/Levantine/Egyptian dialect handling, RTL-aware chunking
- 🤖 **Multi-Agent Orchestration** — LangGraph-compatible agent graphs with Arabic context preservation across turns
- 🛡️ **Hallucination Guard** — Citation enforcement and confidence thresholding designed specifically for Arabic content
- 🔌 **ERP Connectors** — Pre-built ERPNext, SAP, and n8n integrations dominant across GCC enterprises
- 🐳 **Docker-Ready Deployment** — Full local deployment for data sovereignty compliance
- 📊 **Cost-Aware Logging** — Token cost tracking with Arabic-specific tokenization estimates

---

## Quick Start

```bash
pip install arabic-agentforge
```

```python
from arabic_agentforge import ArabicAgent, AgentOrchestrator
from arabic_agentforge.tools import ERPNextTool, TelegramTool
from arabic_agentforge.guards import ArabicHallucinationGuard

# Create an Arabic-native agent
agent = ArabicAgent(
    name="inventory-agent",
    model="gemini-1.5-pro",   # or "qwen2.5", "gpt-4o"
    dialect="gulf",
    hallucination_guard=ArabicHallucinationGuard(
        citation_required=True,
        confidence_threshold=0.85
    )
)

# Attach tools
agent.add_tool(ERPNextTool(base_url="https://your-erp.com"))
agent.add_tool(TelegramTool(bot_token="YOUR_TOKEN"))

# Run a task — input can be Arabic or English
result = agent.run("Create a maintenance ticket for the printer in department 3")
print(result.response)    # Response in Arabic
print(result.citations)   # Sources used
```

Or run via Docker:

```bash
git clone https://github.com/ali-alshanaa/arabic-agentforge.git
cd arabic-agentforge
docker-compose up -d
```

---

## Architecture

```
User Input (Arabic / English)
          │
          ▼
  Arabic NLP Processor
  (Dialect detection → Normalization → RTL Chunking)
          │
          ▼
  Agent Orchestrator  (LangGraph)
  ├── Agent A: Task Router
  ├── Agent B: ERP Connector
  └── Agent C: Response Generator
          │
          ▼
  Hallucination Guard
  (Citation check → Confidence scoring)
          │
          ▼
  Structured Response  (Arabic RTL + citations)
```

---

## Project Structure

```
arabic-agentforge/
├── arabic_agentforge/
│   ├── core/
│   │   ├── agent.py              # Base agent class
│   │   ├── orchestrator.py       # Multi-agent coordination
│   │   └── memory.py             # Conversation memory
│   ├── nlp/
│   │   ├── arabic_processor.py   # Arabic text processing
│   │   ├── dialect_handler.py    # Dialect normalization
│   │   └── chunker.py            # Arabic-aware chunking
│   ├── guards/
│   │   ├── hallucination.py      # Hallucination prevention
│   │   └── citation.py           # Citation enforcement
│   ├── tools/
│   │   ├── erpnext.py            # ERPNext connector
│   │   ├── telegram.py           # Telegram connector
│   │   └── n8n.py                # n8n webhook connector
│   └── connectors/
│       └── erp_bridge.py         # Generic ERP bridge
├── examples/
│   ├── 01_basic_agent.py
│   ├── 02_multi_agent_erp.py
│   └── 03_rag_arabic_docs.py
├── docs/
│   ├── quickstart.md
│   └── api_reference.md
├── tests/
├── docker-compose.yml
└── README.md
```

---

## Use Cases

### 1. Inventory & Maintenance Agent

Connect Telegram to ERPNext automatically — employees send messages in Arabic, agents create tickets, update stock, and respond in natural language.

```python
orchestrator = AgentOrchestrator()
orchestrator.add_agent(inventory_agent)
orchestrator.add_agent(maintenance_agent)

result = orchestrator.run("Where is maintenance request #442?")
```

### 2. Arabic Document RAG

```python
from arabic_agentforge.rag import ArabicRAGPipeline

rag = ArabicRAGPipeline(
    documents="./legal_docs_arabic/",
    citation_mode="strict"
)
answer = rag.query("What are the contract termination conditions?")
print(answer.text)
print(answer.sources)   # Always cited — no hallucination
```

### 3. Enterprise HR Assistant

```python
assistant = ArabicAgent(
    persona="HR Assistant",
    knowledge_base="./hr_policies/",
    response_language="arabic"
)
```

---

## Supported Models

| Model | Arabic Quality | Speed | Cost |
|-------|---------------|-------|------|
| Gemini 1.5 Pro | ⭐⭐⭐⭐⭐ | Fast | Medium |
| Qwen 2.5 72B | ⭐⭐⭐⭐⭐ | Medium | Low |
| GPT-4o | ⭐⭐⭐⭐ | Fast | High |
| Llama 3.1 (local) | ⭐⭐⭐ | Slow | Free |

---

## ERP Integration

Arabic AgentForge ships with production-tested connectors for systems dominant in GCC enterprises:

```python
from arabic_agentforge.tools import ERPNextTool

erp = ERPNextTool(
    base_url="https://your-company.erpnext.com",
    api_key="YOUR_API_KEY",
    arabic_fields=True        # Enables Arabic field mapping
)

agent.add_tool(erp)

# Natural language → ERP action, fully automated
result = agent.run("Add 50 printers to the Riyadh warehouse")
# Automatically creates a Stock Entry in ERPNext
```

---

## Roadmap

- [x] Core Arabic NLP pipeline
- [x] Base agent + orchestrator
- [x] ERPNext connector
- [x] Hallucination guard with citation enforcement
- [ ] Arabic STT integration for voice input
- [ ] Web UI dashboard
- [ ] Azure / AWS deployment templates
- [ ] Fine-tuned Arabic embedding model
- [ ] Arabic agent evaluation benchmark (public leaderboard)

---

## Contributing

Contributions are welcome. Please open an issue before submitting a large PR.

```bash
git clone https://github.com/ali-alshanaa/arabic-agentforge.git
cd arabic-agentforge
pip install -e ".[dev]"
pytest tests/
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT License — free for commercial and personal use. See [LICENSE](LICENSE).

---

<div align="center">

Built from real production experience across Arabic enterprise deployments in Syria, Saudi Arabia, UAE, and Qatar.

⭐ **Star this repo** if it saves you time building Arabic AI systems.

[LinkedIn](https://linkedin.com/in/ali-alshanaa) · [Issues](https://github.com/ali-alshanaa/arabic-agentforge/issues) · [Discussions](https://github.com/ali-alshanaa/arabic-agentforge/discussions)

</div>
