"""
AI Text-to-Image Prompt Generator
Flask Web Application

A mini web application that transforms simple text descriptions
into optimized prompts for AI image generators and generates
actual images using the Pollinations.ai free API.
"""

from flask import Flask, render_template, request, jsonify, send_file
from prompt_engine import generate_prompt, generate_all_styles, get_styles, get_aspect_ratios
from database import init_db, save_prompt, get_all_prompts, get_prompts_by_style, \
    toggle_favorite, delete_prompt, search_prompts, get_stats, get_favorite_prompts
import urllib.parse
import requests
import os
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_env_file():
    """Tiny .env loader (no extra dependency). Lines look like KEY=value."""
    path = os.path.join(BASE_DIR, ".env")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_env_file()

# Free key from https://enter.pollinations.ai  (put it in .env)
POLLINATIONS_API_KEY = os.environ.get("POLLINATIONS_API_KEY", "").strip()
IMAGE_MODEL = os.environ.get("IMAGE_MODEL", "").strip()  # empty = Pollinations default

# Directory to store generated images
IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "generated")
os.makedirs(IMAGES_DIR, exist_ok=True)

# Initialize database on startup
init_db()

# Aspect ratio pixel dimensions for image generation
AR_DIMENSIONS = {
    "square":    (1024, 1024),
    "portrait":  (768, 1024),
    "landscape": (1024, 768),
    "wide":      (1280, 720),
}


# ── Page Routes ──────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Main page - prompt generator."""
    styles = get_styles()
    aspect_ratios = get_aspect_ratios()
    return render_template("index.html", styles=styles, aspect_ratios=aspect_ratios)


@app.route("/history")
def history():
    """Prompt history gallery page."""
    styles = get_styles()
    return render_template("history.html", styles=styles)


@app.route("/about")
def about():
    """About page explaining the AAI concepts used."""
    return render_template("about.html")


# ── API Routes ───────────────────────────────────────────────────────────

@app.route("/api/generate", methods=["POST"])
def api_generate():
    """Generate an optimized prompt AND an AI image from user input."""
    data = request.get_json()
    user_input = data.get("user_input", "").strip()
    style = data.get("style", "photorealistic")
    aspect_ratio = data.get("aspect_ratio", "square")
    generate_image = data.get("generate_image", True)

    if not user_input:
        return jsonify({"error": "Please provide a description."}), 400

    result = generate_prompt(user_input, style, aspect_ratio)

    if "error" in result:
        return jsonify(result), 400

    # Generate image using Pollinations.ai
    image_url = None
    local_image_path = None
    if generate_image:
        local_image_path, err = _generate_image(result["prompt"], aspect_ratio)
        result["local_image"] = local_image_path
        result["image_url"] = local_image_path
        result["image_error"] = err

    # Save to database
    prompt_id = save_prompt(
        user_input=user_input,
        style=result["style_key"],
        style_label=result["style"],
        aspect_ratio=result["aspect_ratio"],
        generated_prompt=result["prompt"],
        negative_prompt=result["negative_prompt"],
        image_url=local_image_path
    )
    result["id"] = prompt_id

    return jsonify(result)


@app.route("/api/generate-all", methods=["POST"])
def api_generate_all():
    """Generate prompts for all styles with images."""
    data = request.get_json()
    user_input = data.get("user_input", "").strip()
    aspect_ratio = data.get("aspect_ratio", "square")

    if not user_input:
        return jsonify({"error": "Please provide a description."}), 400

    results = generate_all_styles(user_input, aspect_ratio)

    # Generate images (3 at a time) and save all to database
    with ThreadPoolExecutor(max_workers=3) as pool:
        outcomes = list(pool.map(
            lambda r: _generate_image(r["prompt"], aspect_ratio), results
        ))

    for result, (local_path, err) in zip(results, outcomes):
        result["local_image"] = local_path
        result["image_url"] = local_path
        result["image_error"] = err

        prompt_id = save_prompt(
            user_input=user_input,
            style=result["style_key"],
            style_label=result["style"],
            aspect_ratio=result["aspect_ratio"],
            generated_prompt=result["prompt"],
            negative_prompt=result["negative_prompt"],
            image_url=local_path
        )
        result["id"] = prompt_id

    return jsonify(results)


@app.route("/api/history")
def api_history():
    """Get prompt history with optional filters."""
    style = request.args.get("style", "")
    search = request.args.get("search", "")
    favorites_only = request.args.get("favorites", "false") == "true"

    if favorites_only:
        prompts = get_favorite_prompts()
    elif search:
        prompts = search_prompts(search)
    elif style:
        prompts = get_prompts_by_style(style)
    else:
        prompts = get_all_prompts()

    return jsonify(prompts)


@app.route("/api/favorite/<int:prompt_id>", methods=["POST"])
def api_toggle_favorite(prompt_id):
    """Toggle favorite status for a prompt."""
    result = toggle_favorite(prompt_id)
    if result is None:
        return jsonify({"error": "Prompt not found."}), 404
    return jsonify(result)


@app.route("/api/delete/<int:prompt_id>", methods=["DELETE"])
def api_delete(prompt_id):
    """Delete a prompt."""
    success = delete_prompt(prompt_id)
    if not success:
        return jsonify({"error": "Prompt not found."}), 404
    return jsonify({"success": True})


@app.route("/api/stats")
def api_stats():
    """Get prompt generation statistics."""
    return jsonify(get_stats())


# ── Image Generation ─────────────────────────────────────────────────────

def _generate_image(prompt, aspect_ratio):
    """
    Generate a real image with Pollinations (gen.pollinations.ai) and save it
    to static/generated/.  Returns (local_url, error_message).
    Exactly one of them is None.
    """
    if not POLLINATIONS_API_KEY:
        return None, ("No API key set. Get a free key at https://enter.pollinations.ai/keys "
                      "and put POLLINATIONS_API_KEY=your_key in a .env file, then restart.")

    width, height = AR_DIMENSIONS.get(aspect_ratio, (1024, 1024))
    url = f"https://gen.pollinations.ai/image/{urllib.parse.quote(prompt, safe='')}"
    params = {
        "width": width,
        "height": height,
        "seed": int(time.time() * 1000) % 999999,
    }
    if IMAGE_MODEL:
        params["model"] = IMAGE_MODEL
    headers = {"Authorization": f"Bearer {POLLINATIONS_API_KEY}"}

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=120)
    except requests.RequestException as e:
        print(f"[IMG] Network error: {e}")
        return None, f"Could not reach the image service: {e}"

    ctype = resp.headers.get("content-type", "")
    if resp.status_code != 200 or not ctype.startswith("image"):
        print(f"[IMG] {resp.status_code}: {resp.text[:300]}")
        hints = {
            401: "API key is missing or invalid.",
            402: "Your Pollinations balance/quota is used up.",
            429: "Too many requests - wait a bit and try again.",
        }
        return None, hints.get(resp.status_code, f"Image service error ({resp.status_code}).")

    ext = "svg" if "svg" in ctype else ("jpg" if "jpeg" in ctype else "png")
    filename = f"img_{uuid.uuid4().hex[:12]}.{ext}"
    with open(os.path.join(IMAGES_DIR, filename), "wb") as f:
        f.write(resp.content)
    return f"/static/generated/{filename}", None


# ── Run ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n[*] AI Prompt Generator is running!")
    print("    Open http://127.0.0.1:5000 in your browser\n")
    app.run(debug=True, port=5000)
