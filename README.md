# Navan Travel Assistant

An intelligent travel assistant that helps with destination recommendations, packing suggestions, and local attractions.

> **Note:** This project prioritizes showcasing advanced LLM capabilities and prompting techniques over optimizing for assistant response latency. The implementation demonstrates various LLM orchestration patterns, multi-agent architectures, and sophisticated prompting strategies.

## Quick Start

### Option 1: Automated Setup (Recommended)

**For macOS/Linux:**
```bash
./setup.sh
```


The setup script will:
- ✅ Check Python installation
- ✅ Create and activate virtual environment
- ✅ Install all dependencies
- ✅ Check Ollama service
- ✅ Start the server
- ✅ Open your browser automatically

### Option 2: Manual Setup

1. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python -m app.main.main
   ```

4. **Open your browser:**
   Navigate to `http://localhost:8000`

## Prerequisites

- **Python 3.8+**
- **Ollama** - Install from [ollama.ai](https://ollama.ai)
  - Make sure Ollama service is running: `ollama serve`
  - The app uses the model specified in `OLLAMA_MODEL` environment variable (default: `llama3.1:8b`)

## Environment Variables

Create a `.env` file in the project root (optional):

```env
OLLAMA_MODEL=llama3.1:8b
```

## Features

- 🗺️ **Destination Recommendations** - Get personalized travel destination suggestions
- 🧳 **Packing Suggestions** - Smart packing lists based on weather and destination
- 🎯 **Local Attractions** - Discover things to do at your destination
- 🛂 **Visa Information** - Check visa requirements and entry restrictions for your travel destination

## Prompting Techniques

### Key Prompt Engineering Decisions

**1. Value-First Response Strategy**: The system prioritizes providing immediate value over asking clarifying questions. For destination recommendations, if sufficient information exists (budget + origin + preferences), the model provides 3 recommendations immediately rather than asking follow-up questions.

**2. Rule-Based Decision Logic**: Explicit IF/ELSE decision trees in prompts (e.g., `destination_intent_guidance.j2`) ensure consistent behavior. For example: "IF budget mentioned without origin → ask for origin only; ELSE IF 3+ criteria present → provide recommendations immediately."

**3. Strict JSON-Only Output for Extraction**: All extraction prompts use multiple reinforcement techniques ("CRITICAL", "MUST", "ONLY") to enforce JSON-only responses, preventing parsing failures from natural language explanations.

**4. Specialized Role Separation**: Different prompts for different tasks (intent classification, location extraction, date extraction, research) rather than a single monolithic prompt, improving accuracy and reliability.

**5. Context-Aware Prompt Selection**: Prompts are dynamically selected and injected based on extracted intent, ensuring the model receives task-specific guidance at the right moment in the conversation flow.

**6. Explicit Tool Selection Rules**: Research agent prompts include detailed rules with examples for when to use each tool, reducing hallucination and ensuring reliable function calling.

---

This project employs several advanced prompting techniques to improve LLM performance and reliability:

### 1. **Few-Shot Prompting**
Multiple examples are provided in prompts to guide the model's behavior:
- **Intent Extraction**: Includes 10+ examples showing correct classification for each intent category
- **Location Extraction**: Provides examples for real locations, fictional places, and edge cases
- **Date Extraction**: Demonstrates explicit date extraction vs. "NONE" when no date is mentioned

### 2. **Chain of Thought (CoT)**
Explicit step-by-step reasoning instructions are embedded in prompts:
- **Response Generator**: Uses "Think through your response step by step" instructions for destination, packing, and attractions intents
- Guides the model through: information assessment → value determination → approach selection → response structuring

### 3. **Structured Output / JSON Schema Enforcement**
Strict JSON schema requirements ensure reliable parsing:
- **Intent Extractor**: Requires `{"intent": str}` format with validation
- **Location Extractor**: Requires `{"location": str, "is_fictional": bool}` format
- **Date Extractor**: Requires `{"date": str}` format
- All prompts include "CRITICAL" instructions to return ONLY JSON with no additional text

### 4. **Role-Based Prompting**
Different system roles are defined for specialized tasks:
- **Travel Assistant** (`system_prompt.j2`): Main conversational role
- **Intent Classifier**: Specialized for intent classification
- **Location Extractor**: Focused on location identification
- **Date Extractor**: Dedicated to temporal information extraction
- **Research Agent**: Tool-calling agent for external data fetching

### 5. **Template-Based Prompting (Jinja2)**
Dynamic prompt generation using Jinja2 templates:
- Conditional logic based on intent type
- Variable injection (user message, location, date, intent)
- Reusable template components
- Located in `app/prompts/` directory


### 6. **Context Injection**
System messages are dynamically injected based on conversation state:
- Intent-specific system messages inserted before final user message
- External data (weather, country info, visa info) injected as system messages
- Context-aware prompt selection based on extracted intent

### 7. **Conditional Prompting**
Different prompts and strategies based on extracted intent:
- **Destination Intent**: Focuses on recommendation strategy and value-first approach
- **Packing Intent**: Emphasizes destination requirement and weather consideration
- **Attractions Intent**: Highlights practical information (costs, timing, booking needs)
- **Legitimate Intent**: Maintains conversational flow

## LLM Techniques

The system implements several advanced LLM orchestration techniques:

### 1. **Function Calling / Tool Use**
Research agent uses native function calling capabilities:
- **Tool Registry**: Centralized tool management (`fetch_weather`, `fetch_country_info`, `fetch_visa_info`)
- **Function Caller**: Handles tool invocation, execution, and result formatting
- **Multi-tool Support**: Can call multiple tools in parallel for complex queries
- Uses Ollama's native tool calling API with tool schemas

### 2. **Parallel Extraction**
Asynchronous parallel processing for efficiency:
- **ExtractorManager**: Uses `asyncio.gather()` to extract intent, location, and date simultaneously
- Reduces latency by running independent extraction tasks in parallel
- Error handling with `return_exceptions=True` to prevent one failure from blocking others

### 3. **Context Window Management**
Intelligent message history management:
- **MAX_CONTEXT_MESSAGES**: Limited to 15 messages to prevent context overflow
- **Smart Trimming**: Preserves system messages while trimming conversation history
- **Priority System**: Keeps primary system prompt, trims oldest conversation messages first
- **Role-Based Partitioning**: Separates system messages from conversation messages for selective trimming

### 4. **Fallback Mechanisms**
Resilient error handling and fallbacks:
- **Fallback Research**: Direct tool calls when LLM function calling fails
- **Exception Handling**: Graceful degradation with default responses
- **JSON Parsing Fallbacks**: Multiple regex patterns and parsing strategies for extraction
- **Default Intent**: Falls back to "legitimate" intent on extraction errors

### 5. **Structured Extraction Pipeline**
Multi-stage information extraction:
- **Stage 1**: Intent classification (determines query type)
- **Stage 2**: Location extraction (identifies destination)
- **Stage 3**: Date extraction (captures temporal information)
- **Stage 4**: External data fetching (weather, country info, visa requirements)
- **Stage 5**: Response generation (context-aware response creation)

### 6. **Optimization Techniques**
Performance and reliability optimizations:
- **Direct Tool Calls**: Bypasses LLM for simple visa queries (faster execution)
- **Cached Tool Schemas**: Tool schemas cached to avoid repeated generation
- **Limited Token Prediction**: `num_predict` parameter limits output length for extraction tasks (30 tokens) vs. generation (500 tokens)
- **Regex-Based JSON Extraction**: Robust parsing with multiple fallback patterns

## Project Structure

```
app/
├── api/              # API routes and controllers
├── algo/             # Core algorithms (extractors, processors)
├── consts/           # Constants (intents, roles, context)
├── main/             # Application entry point
├── models/           # Data models
├── modules/          # Business logic modules
├── prompts/          # LLM prompt templates
├── services/         # Service layer
└── static/           # Frontend assets (HTML, CSS, JS)
```

## Troubleshooting

- **Port 8000 already in use?** - Change the port in `app/main/main.py`
- **Ollama connection error?** - Make sure Ollama is running: `ollama serve`
- **Module not found?** - Ensure virtual environment is activated and dependencies are installed

