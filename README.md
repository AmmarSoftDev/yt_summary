# YouTube Video Summarizer 🎥✨

An AI-powered application that generates comprehensive, hierarchical summaries of YouTube videos using multi-agent architecture. Supports both cloud-based (OpenRouter) and local (Ollama) LLM providers.

## Features

- 🤖 **Multi-Agent Architecture**: Chunking → Summarization → Synthesis
- ☁️ **OpenRouter Support**: Free models (Gemini Flash, Llama 3.1, Mistral)
- 🏠 **Ollama Support**: Local models (Qwen2.5, Llama 3.1, Mistral)
- 📊 **Hierarchical Output**: Overview + Topics + Key Takeaways with timestamps
- 🎯 **Smart Chunking**: Intelligent transcript segmentation with overlap
- 💾 **Export**: Save summaries as markdown files
- 🎨 **Beautiful CLI**: Rich terminal interface with progress tracking

## Architecture

```
┌─────────────────┐
│  YouTube Video  │
└────────┬────────┘
         │
    ┌────▼────┐
    │ Extract │  (YouTubeExtractor)
    │Transcript│
    └────┬────┘
         │
    ┌────▼────┐
    │ Chunking│  (ChunkingAgent)
    │  Agent  │
    └────┬────┘
         │
    ┌────▼────────┐
    │Summarization│  (SummarizationAgent)
    │   Agent     │  Process each chunk
    └────┬────────┘
         │
    ┌────▼────┐
    │Synthesis│  (SynthesisAgent)
    │  Agent  │  Create final summary
    └────┬────┘
         │
    ┌────▼────────┐
    │  Hierarchical│
    │   Summary   │
    └─────────────┘
```

## Installation

### 1. Clone or Navigate to Project
```bash
cd c:\Users\PMLS\Desktop\yt_summary
```

### 2. Activate Virtual Environment
```bash
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment

#### For OpenRouter (Cloud):
1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```
2. Get API key from [OpenRouter](https://openrouter.ai/keys)
3. Edit `.env` and add your key:
   ```
   OPENROUTER_API_KEY=your_actual_key_here
   ```

#### For Ollama (Local):
1. Install [Ollama](https://ollama.ai)
2. Pull the recommended model:
   ```bash
   ollama pull qwen3:8b
   ```
   Or use alternatives:
   ```bash
   ollama pull llama3.1:8b
   ollama pull mistral:7b
   ```

## Usage

### Basic Usage (OpenRouter - Default)
```bash
python -m src.main "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Using Ollama (Local)
```bash
python -m src.main "https://www.youtube.com/watch?v=VIDEO_ID" --provider ollama
```

### Save to File
```bash
python -m src.main "https://www.youtube.com/watch?v=VIDEO_ID" -o summary.md
```

### Custom Model
```bash
# OpenRouter with different model
python -m src.main "VIDEO_URL" --model "meta-llama/llama-3.1-8b-instruct:free"

# Ollama with different model
python -m src.main "VIDEO_URL" --provider ollama --model "llama3.1:8b"
```

### Full Command Options
```bash
python -m src.main [-h] [-p {openrouter,ollama}] [-m MODEL] [-o OUTPUT] url

Arguments:
  url                   YouTube video URL or video ID

Options:
  -h, --help           Show help message
  -p, --provider       LLM provider: openrouter or ollama (default: openrouter)
  -m, --model         Model name (overrides default)
  -o, --output        Output file path (optional)
```

## Recommended Models

### OpenRouter (Free Models)
1. **`openai/gpt-oss-20b:free`** ⭐ (Default)
   - Fast and efficient
   - 1M token context window
   - Best for structured summaries

2. **`meta-llama/llama-3.1-8b-instruct:free`**
   - Excellent instruction following
   - Good reasoning

3. **`mistralai/mistral-7b-instruct:free`**
   - Concise outputs
   - Solid performance

### Ollama (Local Models)
1. **`qwen3:8b`** ⭐ (Default)
   - Superior text understanding
   - Excellent summarization quality

2. **`llama3.1:8b`**
   - Great all-rounder
   - Good instruction following

3. **`mistral:7b`**
   - Fast inference
   - Good for shorter summaries

## Output Format

```markdown
# Video Summary

## Overview
[2-3 paragraph narrative overview of the entire video]

## Key Topics

### Topic 1: [Topic Name] (00:00 - 05:30)
- Key point 1
- Key point 2
- Key point 3

[1-2 paragraph narrative explanation]

### Topic 2: [Topic Name] (05:30 - 12:45)
...

## Key Takeaways
- Main takeaway 1
- Main takeaway 2
- Main takeaway 3
```

## Project Structure

```
yt_summary/
├── src/
│   ├── agents/
│   │   ├── chunking_agent.py      # Intelligent transcript chunking
│   │   ├── summarization_agent.py # Chunk-level summarization
│   │   └── synthesis_agent.py     # Final summary synthesis
│   ├── providers/
│   │   ├── base_provider.py       # Abstract LLM provider
│   │   ├── openrouter_provider.py # OpenRouter integration
│   │   └── ollama_provider.py     # Ollama integration
│   ├── utils/
│   │   ├── youtube_extractor.py   # Transcript extraction
│   │   └── text_processing.py     # Text utilities
│   └── main.py                    # CLI application
├── config.yaml                    # Configuration
├── .env.example                   # Environment template
├── requirements.txt               # Dependencies
└── README.md
```

## Examples

### Example 1: Quick Summary
```bash
python -m src.main "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### Example 2: Local Model with Output
```bash
python -m src.main "https://youtu.be/VIDEO_ID" --provider ollama -o my_summary.md
```

### Example 3: Different OpenRouter Model
```bash
python -m src.main "https://www.youtube.com/watch?v=VIDEO_ID" \
  --model "mistralai/mistral-7b-instruct:free"
```

## Troubleshooting

### OpenRouter Issues
- **Error: API key not found**
  - Ensure `.env` file exists with valid `OPENROUTER_API_KEY`
  - Check key at [OpenRouter Keys](https://openrouter.ai/keys)

### Ollama Issues
- **Error: Server not running**
  - Start Ollama: `ollama serve`
  - Check status: `ollama list`

- **Error: Model not found**
  - Pull model: `ollama pull qwen3:8b`
  - List available: `ollama list`

### YouTube Issues
- **Error: No transcript found**
  - Video must have captions/subtitles enabled
  - Some videos don't allow transcript access

## Configuration

Edit [config.yaml](config.yaml) to customize:
- Chunk sizes and overlap
- Default models for each provider
- Temperature and token limits
- Output formatting options

## Requirements

- Python 3.8+
- Active internet connection (for OpenRouter and YouTube)
- Ollama installed (for local models)

## License

MIT License - Feel free to use and modify!

## Contributing

Contributions welcome! Feel free to open issues or submit PRs.

---

**Built with ❤️ using AI agents, OpenRouter, and Ollama**