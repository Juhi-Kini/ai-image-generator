"""
AI Prompt Engineering Engine
Transforms simple user descriptions into optimized prompts for
AI image generators like DALL-E, Stable Diffusion, and Midjourney.
"""

import random

# ---------------------------------------------------------------------------
# Style Definitions
# ---------------------------------------------------------------------------

STYLES = {
    "photorealistic": {
        "label": "Photorealistic",
        "icon": "📷",
        "modifiers": [
            "photorealistic", "hyper-realistic", "ultra-detailed",
            "8K UHD", "DSLR quality", "sharp focus", "depth of field",
            "natural lighting", "ray tracing", "physically based rendering"
        ],
        "lighting": [
            "golden hour lighting", "soft natural light",
            "studio lighting", "dramatic shadows",
            "volumetric lighting", "rim lighting"
        ],
        "mood": [
            "cinematic", "atmospheric", "moody", "serene", "vivid"
        ],
        "suffix": "trending on 500px, award-winning photography"
    },
    "anime": {
        "label": "Anime / Manga",
        "icon": "🎌",
        "modifiers": [
            "anime style", "manga illustration", "cel-shaded",
            "vibrant colors", "detailed linework", "expressive eyes",
            "dynamic pose", "clean lines"
        ],
        "lighting": [
            "soft glow", "dramatic anime lighting", "backlighting",
            "neon highlights", "sparkle effects"
        ],
        "mood": [
            "epic", "emotional", "dynamic", "peaceful", "intense"
        ],
        "suffix": "trending on Pixiv, studio quality anime art"
    },
    "oil_painting": {
        "label": "Oil Painting",
        "icon": "🖼️",
        "modifiers": [
            "oil painting style", "thick brushstrokes", "textured canvas",
            "rich color palette", "impasto technique", "classical art",
            "museum quality", "fine art"
        ],
        "lighting": [
            "chiaroscuro lighting", "Rembrandt lighting",
            "warm candlelight", "diffused natural light",
            "dramatic contrast"
        ],
        "mood": [
            "romantic", "melancholic", "majestic", "contemplative", "grand"
        ],
        "suffix": "masterpiece, gallery exhibition quality"
    },
    "watercolor": {
        "label": "Watercolor",
        "icon": "🎨",
        "modifiers": [
            "watercolor painting", "soft washes", "wet-on-wet technique",
            "translucent layers", "delicate brushwork", "paper texture visible",
            "flowing pigments", "artistic splashes"
        ],
        "lighting": [
            "soft diffused light", "gentle highlights",
            "pastel tones", "luminous transparency"
        ],
        "mood": [
            "dreamy", "ethereal", "gentle", "whimsical", "nostalgic"
        ],
        "suffix": "fine art watercolor, exhibition quality"
    },
    "cyberpunk": {
        "label": "Cyberpunk",
        "icon": "🌃",
        "modifiers": [
            "cyberpunk aesthetic", "neon-lit", "futuristic",
            "high-tech low-life", "holographic elements", "chrome surfaces",
            "rain-soaked streets", "dystopian atmosphere"
        ],
        "lighting": [
            "neon lighting", "bioluminescence", "LED glow",
            "holographic reflections", "electric blue and magenta",
            "flickering signs"
        ],
        "mood": [
            "gritty", "noir", "electric", "rebellious", "mysterious"
        ],
        "suffix": "cyberpunk 2077 style, Blade Runner aesthetic, trending on ArtStation"
    },
    "fantasy": {
        "label": "Fantasy Art",
        "icon": "🐉",
        "modifiers": [
            "fantasy art", "epic fantasy illustration", "magical",
            "enchanted", "mythical creatures", "otherworldly",
            "detailed fantasy environment", "heroic proportions"
        ],
        "lighting": [
            "magical glow", "ethereal light", "mystical aura",
            "enchanted forest light", "divine radiance",
            "aurora borealis"
        ],
        "mood": [
            "epic", "mystical", "adventurous", "dark fantasy", "whimsical"
        ],
        "suffix": "fantasy concept art, trending on ArtStation, by Greg Rutkowski"
    },
    "minimalist": {
        "label": "Minimalist",
        "icon": "⬜",
        "modifiers": [
            "minimalist design", "clean composition", "simple shapes",
            "negative space", "flat design", "geometric",
            "limited color palette", "modern aesthetic"
        ],
        "lighting": [
            "flat lighting", "even illumination", "soft shadows",
            "clean highlights"
        ],
        "mood": [
            "calm", "zen", "modern", "elegant", "sophisticated"
        ],
        "suffix": "minimalist art, Dribbble trending, clean design"
    },
    "pixel_art": {
        "label": "Pixel Art",
        "icon": "👾",
        "modifiers": [
            "pixel art", "16-bit style", "retro game aesthetic",
            "sprite art", "dithering", "limited palette",
            "crisp pixels", "nostalgic gaming art"
        ],
        "lighting": [
            "flat shading", "simple highlights", "retro glow",
            "CRT screen effect"
        ],
        "mood": [
            "retro", "playful", "nostalgic", "adventurous", "charming"
        ],
        "suffix": "pixel art masterpiece, indie game quality"
    },
    "pop_art": {
        "label": "Pop Art",
        "icon": "🎪",
        "modifiers": [
            "pop art style", "bold outlines", "halftone dots",
            "vibrant primary colors", "Andy Warhol inspired",
            "Roy Lichtenstein style", "comic book aesthetic"
        ],
        "lighting": [
            "flat bold lighting", "high contrast",
            "saturated colors", "screen print effect"
        ],
        "mood": [
            "bold", "energetic", "ironic", "playful", "iconic"
        ],
        "suffix": "pop art masterpiece, gallery quality"
    },
    "sketch": {
        "label": "Pencil Sketch",
        "icon": "✏️",
        "modifiers": [
            "pencil sketch", "graphite drawing", "hand-drawn",
            "cross-hatching", "fine linework", "charcoal texture",
            "sketchbook style", "detailed shading"
        ],
        "lighting": [
            "dramatic shading", "subtle gradients",
            "high contrast black and white", "soft graphite tones"
        ],
        "mood": [
            "raw", "intimate", "classical", "studious", "expressive"
        ],
        "suffix": "professional illustration, concept art sketch"
    }
}

# ---------------------------------------------------------------------------
# Negative Prompts per Style
# ---------------------------------------------------------------------------

NEGATIVE_PROMPTS = {
    "default": [
        "blurry", "low quality", "low resolution", "watermark",
        "text", "signature", "username", "jpeg artifacts",
        "distorted", "disfigured", "deformed", "bad anatomy",
        "extra limbs", "mutated", "ugly", "duplicate",
        "poorly drawn", "out of frame", "cropped"
    ],
    "photorealistic": [
        "cartoon", "anime", "illustration", "painting",
        "drawing", "CGI", "3D render", "unrealistic"
    ],
    "anime": [
        "photorealistic", "3D", "western cartoon",
        "poorly drawn face", "bad proportions", "gross proportions"
    ],
    "oil_painting": [
        "digital art", "photo", "3D render", "anime",
        "flat colors", "vector art"
    ],
    "watercolor": [
        "digital art", "oil painting", "photo", "heavy outlines",
        "bold colors", "3D render"
    ],
    "cyberpunk": [
        "medieval", "nature", "pastoral", "rustic",
        "vintage", "old-fashioned", "bright daylight"
    ],
    "fantasy": [
        "modern", "sci-fi", "urban", "realistic photo",
        "mundane", "boring", "plain"
    ],
    "minimalist": [
        "cluttered", "complex", "detailed", "ornate",
        "busy background", "photorealistic", "noisy"
    ],
    "pixel_art": [
        "smooth", "high resolution", "photorealistic", "3D render",
        "anti-aliased", "blurry", "realistic"
    ],
    "pop_art": [
        "muted colors", "photorealistic", "pastel",
        "subtle", "monochrome", "watercolor"
    ],
    "sketch": [
        "color", "photorealistic", "digital painting",
        "3D render", "vibrant", "saturated"
    ]
}

# ---------------------------------------------------------------------------
# Quality Boosters
# ---------------------------------------------------------------------------

QUALITY_BOOSTERS = [
    "highly detailed", "intricate details", "sharp focus",
    "professional", "award-winning", "masterpiece"
]

# ---------------------------------------------------------------------------
# Aspect Ratio Tags
# ---------------------------------------------------------------------------

ASPECT_RATIOS = {
    "square": {"label": "Square (1:1)", "tag": "--ar 1:1"},
    "portrait": {"label": "Portrait (2:3)", "tag": "--ar 2:3"},
    "landscape": {"label": "Landscape (16:9)", "tag": "--ar 16:9"},
    "wide": {"label": "Ultra Wide (21:9)", "tag": "--ar 21:9"},
}


def get_styles():
    """Return all available styles with their labels and icons."""
    return {
        key: {"label": val["label"], "icon": val["icon"]}
        for key, val in STYLES.items()
    }


def get_aspect_ratios():
    """Return all available aspect ratios."""
    return ASPECT_RATIOS


def generate_prompt(user_input: str, style: str, aspect_ratio: str = "square") -> dict:
    """
    Generate an optimized AI image prompt from a simple user description.

    Args:
        user_input: The user's plain English description.
        style: The art style key (e.g., 'photorealistic', 'anime').
        aspect_ratio: The aspect ratio key (e.g., 'square', 'portrait').

    Returns:
        A dict with 'prompt', 'negative_prompt', 'style', 'aspect_ratio', and 'tips'.
    """
    user_input = user_input.strip()
    if not user_input:
        return {"error": "Please provide a description."}

    style_data = STYLES.get(style)
    if not style_data:
        return {"error": f"Unknown style: {style}"}

    ar_data = ASPECT_RATIOS.get(aspect_ratio, ASPECT_RATIOS["square"])

    # --- Build the enhanced prompt ---
    # Pick a subset of modifiers for variety
    selected_modifiers = random.sample(
        style_data["modifiers"], min(5, len(style_data["modifiers"]))
    )
    selected_lighting = random.sample(
        style_data["lighting"], min(2, len(style_data["lighting"]))
    )
    selected_mood = random.choice(style_data["mood"])
    selected_quality = random.sample(QUALITY_BOOSTERS, min(3, len(QUALITY_BOOSTERS)))

    # Compose the prompt
    parts = [
        user_input.rstrip(".").rstrip(","),
        ", ".join(selected_modifiers),
        ", ".join(selected_lighting),
        selected_mood,
        ", ".join(selected_quality),
        style_data["suffix"],
        ar_data["tag"]
    ]
    enhanced_prompt = ", ".join(parts)

    # --- Build negative prompt ---
    neg_parts = list(NEGATIVE_PROMPTS["default"])
    style_neg = NEGATIVE_PROMPTS.get(style, [])
    neg_parts.extend(style_neg)
    # Deduplicate while preserving order
    seen = set()
    unique_neg = []
    for item in neg_parts:
        if item.lower() not in seen:
            seen.add(item.lower())
            unique_neg.append(item)
    negative_prompt = ", ".join(unique_neg)

    # --- Generate tips ---
    tips = _generate_tips(style)

    return {
        "prompt": enhanced_prompt,
        "negative_prompt": negative_prompt,
        "style": style_data["label"],
        "style_key": style,
        "aspect_ratio": ar_data["label"],
        "tips": tips
    }


def generate_all_styles(user_input: str, aspect_ratio: str = "square") -> list:
    """Generate prompts for ALL styles at once for comparison."""
    results = []
    for style_key in STYLES:
        result = generate_prompt(user_input, style_key, aspect_ratio)
        if "error" not in result:
            results.append(result)
    return results


def _generate_tips(style: str) -> list:
    """Generate contextual tips based on the selected style."""
    tips_map = {
        "photorealistic": [
            "💡 Specify camera details like 'Canon EOS R5, 85mm lens' for more realism",
            "💡 Add time of day: 'during golden hour' or 'at blue hour'",
            "💡 Mention specific materials: 'marble texture', 'glass reflections'"
        ],
        "anime": [
            "💡 Mention a specific anime studio style: 'Studio Ghibli style' or 'Makoto Shinkai style'",
            "💡 Add emotion descriptors: 'blushing', 'determined expression'",
            "💡 Specify background details: 'cherry blossom trees', 'sunset sky'"
        ],
        "oil_painting": [
            "💡 Reference a master: 'in the style of Monet' or 'Vermeer-inspired'",
            "💡 Describe the canvas: 'on textured linen canvas'",
            "💡 Add era: 'Renaissance style' or 'Impressionist technique'"
        ],
        "watercolor": [
            "💡 Mention paper type: 'on cold-pressed watercolor paper'",
            "💡 Add flow effects: 'paint bleeding at edges', 'wet splashes'",
            "💡 Use soft color terms: 'pastel tones', 'muted palette'"
        ],
        "cyberpunk": [
            "💡 Add specific tech: 'holographic displays', 'neural implants'",
            "💡 Set the scene: 'rain-soaked Tokyo alley' or 'mega-corporation tower'",
            "💡 Mention specific neon colors: 'magenta and cyan neon'"
        ],
        "fantasy": [
            "💡 Add magical elements: 'glowing runes', 'enchanted crystals'",
            "💡 Specify the fantasy race or creature type explicitly",
            "💡 Set the world: 'medieval kingdom', 'floating islands', 'underwater realm'"
        ],
        "minimalist": [
            "💡 Specify exact colors: 'using only black, white, and red'",
            "💡 Mention geometric shapes: 'circles and triangles only'",
            "💡 Add design context: 'poster design', 'logo concept', 'icon set'"
        ],
        "pixel_art": [
            "💡 Specify resolution: '32x32 sprite' or '64x64 character'",
            "💡 Mention game style: 'SNES-era RPG' or 'Game Boy palette'",
            "💡 Add animation hint: 'idle animation frame', 'walk cycle'"
        ],
        "pop_art": [
            "💡 Mention repetition: 'grid of 4 variations in different colors'",
            "💡 Add comic elements: 'speech bubble', 'Ben-Day dots'",
            "💡 Reference the era: '1960s pop culture', 'modern pop art'"
        ],
        "sketch": [
            "💡 Specify medium: 'HB pencil', '6B graphite', 'charcoal on paper'",
            "💡 Add technique: 'cross-hatching', 'contour drawing', 'gesture sketch'",
            "💡 Mention sketchbook context: 'artist's sketchbook page'"
        ]
    }
    return tips_map.get(style, ["💡 Be as specific as possible for better results"])
