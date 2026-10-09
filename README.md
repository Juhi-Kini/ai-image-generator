# 🎨 AI Text-to-Image Prompt Generator

An Applied Artificial Intelligence (AAI) mini web application that transforms simple text descriptions into optimized prompts for AI image generators like DALL·E, Stable Diffusion, and Midjourney.

## ✨ Features

- **10 Art Styles** — Photorealistic, Anime, Oil Painting, Watercolor, Cyberpunk, Fantasy, Minimalist, Pixel Art, Pop Art, Pencil Sketch
- **Negative Prompt Generation** — Auto-generates what to exclude
- **Multiple Aspect Ratios** — Square, Portrait, Landscape, Ultra Wide
- **Generate All Styles** — Compare all 10 styles at once
- **Prompt History Gallery** — Searchable, filterable, with favorites
- **One-Click Copy** — Copy prompts to clipboard instantly
- **Contextual Tips** — Style-specific improvement suggestions
- **Dark Theme UI** — Modern, beautiful interface

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Backend   | Python 3 + Flask |
| Database  | SQLite3 |
| Frontend  | HTML + Tailwind CSS + JavaScript |
| Prompt Engine | Rule-based prompt engineering |
| Image AI | Pollinations.ai (gen.pollinations.ai) |

## 🔑 Get a free API key (required for real images)

1. Sign up at https://enter.pollinations.ai/keys and create a key (starts with `sk_`).
2. Copy `.env.example` to `.env` and paste the key:
   ```
   POLLINATIONS_API_KEY=sk_your_key_here
   ```

## 🚀 How to Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the application
```bash
python app.py
```

### 3. Open in browser
```
http://127.0.0.1:5000
```

## 📁 Project Structure

```
ai-prompt-generator/
├── app.py              # Flask web application (routes & API)
├── prompt_engine.py    # AI prompt engineering logic
├── database.py         # SQLite database operations
├── requirements.txt    # Python dependencies
├── prompts.db          # SQLite database (auto-created)
├── templates/
│   ├── base.html       # Base layout template
│   ├── index.html      # Main generator page
│   ├── history.html    # Prompt history gallery
│   └── about.html      # About page (AAI concepts)
├── static/
│   ├── css/
│   │   └── style.css   # Custom styles
│   └── js/
│       └── app.js      # Frontend JavaScript
└── README.md
```

## 🧠 AAI Concepts Demonstrated

1. **Prompt Engineering** — Crafting optimized inputs for AI models
2. **Natural Language Processing** — Parsing and enhancing text
3. **Knowledge-Based Systems** — Curated domain knowledge for art styles
4. **Human-AI Interaction** — Intuitive UI design for AI tools
5. **Generative AI Workflows** — Understanding text-to-image pipelines


## Accounts and deployment notes

- Users can register at `/register` and log in at `/login`.
- Passwords are stored as Werkzeug password hashes, not plain text.
- Prompt history, favorites, statistics and deletion are scoped to the logged-in user.
- Set `POLLINATIONS_API_KEY` and a long random `FLASK_SECRET_KEY` in Render's Environment settings.
- For durable production storage, use a persistent disk for SQLite or migrate to a managed database. Render's ephemeral filesystem may reset on redeploy.
- Generated image files are currently written under `static/generated`; use persistent/private object storage and an authenticated image-serving route before treating image URLs as confidential.
