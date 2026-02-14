# Configuration Guide - Smart Notes

This guide explains how to configure Smart Notes to work with your Anki setup.

## Quick Start

1. **Install the addon:** Tools > Addons > Get Addon, paste `1531888719`
2. **Open settings:** Tools > Smart Notes > Configure
3. **Choose your AI provider** and start generating fields!

---

## Essential Configuration

### Authentication (Premium Features)

When you first open Smart Notes, you'll be prompted to start a free trial or sign in.

**`auth_token`** - Auto-managed. Do not edit manually.
- Obtained after you subscribe or start your free trial
- Required to use most Smart Notes features
- Stored securely in your Anki profile

---

## Chat / AI Generation

These settings control how Smart Notes generates text for your fields.

### Provider Selection

**`chat_provider`** - Choose your AI provider:
- **`openai`** (Default) - Uses ChatGPT. Requires Smart Notes subscription.
- **`anthropic`** - Uses Claude. Requires Smart Notes subscription.
- **`deepseek`** - Uses DeepSeek. Requires Smart Notes subscription.
- **`ollama`** - Free, local AI model. Requires Ollama installed on your computer.

**UI Location:** Tools > Smart Notes > Language Models > Provider

### Model Selection

**`chat_model`** - Choose which specific model to use:

**OpenAI models:**
- `gpt-5` - Newest, most capable
- `gpt-4o-mini` (Default) - Fast, cheap, good quality
- `gpt-5-mini` - Fast, newer
- `gpt-5-nano` - Very fast, lower quality

**Anthropic (Claude) models:**
- `claude-opus-4-1` - Most powerful
- `claude-sonnet-4-0` - Balanced
- `claude-3-5-haiku-latest` - Fast, cheaper

**DeepSeek:**
- `deepseek-v3` - Only option

**Ollama (Local):**
- Any model you've downloaded (e.g., `llama3.2`, `mistral`, `neural-chat`)
- Must be pulled in Ollama first: `ollama pull llama3.2`

**UI Location:** Tools > Smart Notes > Language Models > Model

### Temperature (Creativity Level)

**`chat_temperature`** - How creative/random responses are:
- **0** - Deterministic, precise, repetitive
- **1** (Default) - Balanced
- **2** - Creative, varied, random

**UI Location:** Tools > Smart Notes > Language Models > Creativity

---

## Text-to-Speech (TTS)

These settings control how Smart Notes speaks your notes.

### TTS Provider

**`tts_provider`** - Choose your text-to-speech service:
- **`google`** (Default) - Free, 30+ languages, good quality
- **`openai`** - Premium, natural voice, requires subscription
- **`elevenLabs`** - Premium, 250+ voices, most natural, requires subscription
- **`azure`** - Premium, Microsoft voices, requires subscription

**UI Location:** Tools > Smart Notes > Text-to-Speech > Provider

### TTS Voice

**`tts_voice`** - Choose which voice to use:
- Depends on your provider
- **Google voices:** `en-US-Casual-K`, `en-GB-Standard-A`, `ja-JP-Neural2-A`, etc.
- **OpenAI voices:** `alloy`, `echo`, `fable`, `onyx`, `nova`
- **ElevenLabs:** 250+ voice options available in settings
- **Azure:** `en-US-GuyNeural`, `en-GB-LibbyNeural`, etc.

**UI Location:** Tools > Smart Notes > Text-to-Speech > Voice

### TTS Model

**`tts_model`** - Quality/speed tradeoff:
- **`standard`** (Default) - Good balance of quality and speed
- Other options depend on your TTS provider

**UI Location:** Tools > Smart Notes > Text-to-Speech > Model

---

## Advanced Settings

### Local Ollama Setup

If you want to use free, local AI models with Ollama:

**Setup steps:**
1. Install Ollama from [ollama.ai](https://ollama.ai)
2. Run: `ollama serve` (keeps Ollama running)
3. In Smart Notes settings, set `chat_provider` to `ollama`
4. Download a model: `ollama pull llama3.2` (in another terminal)
5. Select your model in Smart Notes

**`ollama_endpoint`** - Where Ollama is running:
- Default: `http://localhost:11434`
- Change only if you're running Ollama on a different computer

**`ollama_model`** - Which model to use:
- Default: `llama3.2`
- Examples: `mistral`, `neural-chat`, `dolphin-mixtral`

**UI Location:** Tools > Smart Notes > Language Models > (Ollama section)

---

## Feature Toggles

### Generation Behavior

**`generate_at_review`** - Auto-generate fields during review:
- **`true`** (Default) - Fields generate automatically when you study
- **`false`** - Only generate manually via button or right-click

**`allow_empty_fields`** - Only generate into empty fields:
- **`true`** (Default) - Skip fields that already have content
- **`false`** - Always generate, even if field has content

**`regenerate_notes_when_batching`** - Overwrite fields during batch operations:
- **`true`** - Replace existing field content
- **`false`** (Default) - Use `allow_empty_fields` logic to avoid overwrites

**UI Location:** Tools > Smart Notes > Advanced

### Output Format

**`chat_markdown_to_html`** - Convert markdown to HTML:
- **`true`** (Default) - Bold, italics, lists show in Anki
- **`false`** - Keep raw markdown text

**`tts_strip_html`** - Remove HTML from TTS:
- **`true`** (Default) - Clean audio without HTML tags
- **`false`** - Speak HTML tags as text (avoid this)

**UI Location:** Tools > Smart Notes > Advanced

### Debug Mode

**`debug`** - Enable detailed logging:
- **`true`** - Extra logging for troubleshooting
- **`false`** (Default) - Normal operation

Only enable if you're reporting a bug.

---

## Image Generation

**`image_provider`** - Currently only `replicate` (requires subscription)

**`image_model`** - Choose quality/speed:
- `flux-schnell` - Fast, good quality
- `flux-pro` - Highest quality, slower
- `stable-diffusion-3.5` - Lighter model

**Note:** Image generation requires an active Smart Notes subscription.

---

## Per-Field Customization

You can override global settings for specific fields. This is managed through the Smart Notes UI:

1. Tools > Smart Notes > Add Smart Field
2. Click "Advanced" to customize AI model, TTS voice, etc. for just that field

These overrides are stored in `prompts_map` (don't edit manually).

---

## Troubleshooting

### "Auth required" error
- Make sure you've signed up at [smart-notes.xyz](https://smart-notes.xyz)
- Check that you're logged in: Tools > Smart Notes > Account
- Restart Anki if you just signed up

### Generation is slow
- **Ollama:** Your computer might be too slow. Try a smaller model like `neural-chat`
- **OpenAI:** Large models like `gpt-5` take longer. Try `gpt-4o-mini`
- **TTS:** Premium providers are faster. Google TTS is slower but free

### "Invalid OpenAI API key" (Legacy)
- Smart Notes no longer supports personal OpenAI keys
- Use the Smart Notes subscription instead (includes better models)
- Contact [support@smart-notes.xyz](mailto:support@smart-notes.xyz) if you need help

### Ollama errors
- Make sure Ollama is running: `ollama serve`
- Check endpoint is correct: default is `http://localhost:11434`
- Verify model is downloaded: `ollama list`
- Try a different model: `ollama pull mistral`

---

## Support

- Visit [smart-notes.xyz](https://smart-notes.xyz)
- Email [support@smart-notes.xyz](mailto:support@smart-notes.xyz)
- GitHub issues: [github.com/piazzatron/anki-smart-notes](https://github.com/piazzatron/anki-smart-notes/issues)

---

## Advanced: Direct Config Editing

**Location:** `~/.local/share/Anki2/addons21/1531888719/meta.json` (Linux/Mac)  
or `%APPDATA%\Anki2\addons21\1531888719\meta.json` (Windows)

Only edit if you know what you're doing. Most changes should be made through Tools > Smart Notes UI.
