/**
 * AI Prompt Generator — Frontend Logic
 * Handles image generation, prompt display, clipboard, and UI interactions.
 */

// ── State ───────────────────────────────────────────────────────────────

let selectedStyle = 'photorealistic';
let selectedAR = 'square';

// ── Style & Aspect Ratio Selection ──────────────────────────────────────

function selectStyle(style) {
    selectedStyle = style;
    document.querySelectorAll('#style-grid .style-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.style === style);
    });
}

function selectAR(ar) {
    selectedAR = ar;
    document.querySelectorAll('#ar-grid .ar-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.ar === ar);
    });
}

// ── Generate Single Image ───────────────────────────────────────────────

async function generatePrompt() {
    const input = document.getElementById('user-input').value.trim();
    if (!input) {
        showToast('Please describe your image idea first!', 'error');
        return;
    }

    setLoading(true);

    try {
        const res = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_input: input,
                style: selectedStyle,
                aspect_ratio: selectedAR
            })
        });

        const data = await res.json();

        if (data.error) {
            showToast(data.error, 'error');
            return;
        }

        renderResult(data);
    } catch (err) {
        showToast('Something went wrong. Please try again.', 'error');
        console.error(err);
    } finally {
        setLoading(false);
    }
}

// ── Generate All Styles ─────────────────────────────────────────────────

async function generateAll() {
    const input = document.getElementById('user-input').value.trim();
    if (!input) {
        showToast('Please describe your image idea first!', 'error');
        return;
    }

    setLoading(true);

    try {
        const res = await fetch('/api/generate-all', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_input: input,
                aspect_ratio: selectedAR
            })
        });

        const data = await res.json();

        if (data.error) {
            showToast(data.error, 'error');
            return;
        }

        renderAllResults(data);
    } catch (err) {
        showToast('Something went wrong. Please try again.', 'error');
        console.error(err);
    } finally {
        setLoading(false);
    }
}

// ── Render Results ──────────────────────────────────────────────────────

function renderResult(data) {
    const container = document.getElementById('results-container');
    const imageSrc = data.local_image || data.image_url || '';

    const html = `
        <div class="result-card card p-6 mb-6">
            <div class="flex items-center justify-between mb-4">
                <div>
                    <span class="badge bg-accent-purple/20 text-accent-purple">${escapeHtml(data.style)}</span>
                    <span class="badge bg-accent-cyan/20 text-accent-cyan ml-2">${escapeHtml(data.aspect_ratio)}</span>
                </div>
                <span class="text-xs text-gray-500">Just now</span>
            </div>

            ${!imageSrc && data.image_error ? `
            <div class="mb-5 p-4 rounded-xl border border-red-500/40 bg-red-500/10 text-red-300 text-sm">
                ⚠️ Image could not be generated: ${escapeHtml(data.image_error)}
            </div>` : ''}

            <!-- Generated Image -->
            ${imageSrc ? `
            <div class="mb-5">
                <div class="rounded-xl overflow-hidden border border-dark-600 bg-dark-900">
                    <img
                        src="${escapeHtml(imageSrc)}"
                        alt="AI Generated Image"
                        class="w-full max-h-[600px] object-contain mx-auto"
                        loading="lazy"
                        onerror="this.parentElement.innerHTML='<div class=\\'text-center py-12 text-gray-500\\'>Image failed to load. Try generating again.</div>'"
                    >
                </div>
                <div class="flex gap-2 mt-3">
                    <a href="${escapeHtml(imageSrc)}" download="ai-generated-image.png"
                       class="btn-copy inline-flex items-center gap-1">
                        ⬇️ Download Image
                    </a>
                    <a href="${escapeHtml(imageSrc)}" target="_blank"
                       class="btn-copy inline-flex items-center gap-1">
                        🔗 Open Full Size
                    </a>
                </div>
            </div>
            ` : ''}

            <!-- Enhanced Prompt -->
            <details class="mb-4" open>
                <summary class="text-sm font-semibold text-green-400 cursor-pointer mb-2">
                    ✅ Enhanced Prompt (click to copy)
                </summary>
                <div class="flex items-end justify-between gap-2 mb-1">
                    <span class="text-xs text-gray-500">Used to generate the image above</span>
                    <button class="btn-copy text-xs" onclick="copyToClipboard(this, 'prompt-${data.id}')">
                        📋 Copy Prompt
                    </button>
                </div>
                <div class="prompt-output" id="prompt-${data.id}">${escapeHtml(data.prompt)}</div>
            </details>

            <!-- Negative Prompt -->
            <details class="mb-4">
                <summary class="text-sm font-semibold text-red-400 cursor-pointer mb-2">
                    🚫 Negative Prompt
                </summary>
                <div class="flex items-end justify-between gap-2 mb-1">
                    <span class="text-xs text-gray-500">Excludes unwanted elements</span>
                    <button class="btn-copy text-xs" onclick="copyToClipboard(this, 'neg-${data.id}')">
                        📋 Copy
                    </button>
                </div>
                <div class="negative-section font-mono text-sm text-red-300" id="neg-${data.id}">${escapeHtml(data.negative_prompt)}</div>
            </details>

            <!-- Tips -->
            <details>
                <summary class="text-sm font-semibold text-yellow-400 cursor-pointer mb-2">
                    💡 Tips to improve results
                </summary>
                <div class="space-y-2 mt-2">
                    ${data.tips.map(tip => `<div class="tip-card">${escapeHtml(tip)}</div>`).join('')}
                </div>
            </details>
        </div>
    `;

    container.innerHTML = html + container.innerHTML;
    if (imageSrc) { showToast('Image generated successfully!', 'success'); } else { showToast(data.image_error || 'Image failed', 'error'); }
}

function renderAllResults(results) {
    const container = document.getElementById('results-container');

    let cardsHtml = `
        <div class="mb-6">
            <h2 class="text-xl font-bold text-gray-200">🎯 All Styles Comparison — ${results.length} Images</h2>
            <p class="text-gray-400 text-sm mt-1">Same concept rendered across every art style</p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
    `;

    results.forEach(data => {
        const imageSrc = data.local_image || data.image_url || '';
        cardsHtml += `
            <div class="result-card card p-4">
                <div class="flex items-center justify-between mb-3">
                    <span class="badge bg-accent-purple/20 text-accent-purple">${escapeHtml(data.style)}</span>
                    <div class="flex gap-1">
                        ${imageSrc ? `
                        <a href="${escapeHtml(imageSrc)}" download class="btn-copy text-xs px-2 py-1">⬇️</a>
                        ` : ''}
                        <button class="btn-copy text-xs px-2 py-1" onclick="copyToClipboard(this, 'prompt-all-${data.id}')">📋</button>
                    </div>
                </div>
                ${imageSrc ? `
                <div class="rounded-lg overflow-hidden border border-dark-600 mb-3 bg-dark-900">
                    <img src="${escapeHtml(imageSrc)}" alt="${escapeHtml(data.style)}"
                         class="w-full h-64 object-cover"
                         loading="lazy"
                         onerror="this.parentElement.innerHTML='<div class=\\'text-center py-8 text-gray-500 text-sm\\'>Failed to load</div>'"
                    >
                </div>
                ` : `<div class="text-xs text-red-300 mb-3">⚠️ ${escapeHtml(data.image_error || 'No image')}</div>`}
                <div class="prompt-output text-xs" id="prompt-all-${data.id}" style="max-height:80px;overflow:auto">${escapeHtml(data.prompt)}</div>
            </div>
        `;
    });

    cardsHtml += `</div>`;
    container.innerHTML = cardsHtml;
    const ok = results.filter(r => r.local_image).length;
    showToast(`${ok}/${results.length} images generated`, ok ? 'success' : 'error');
}

// ── Utilities ───────────────────────────────────────────────────────────

function copyToClipboard(btn, elementId) {
    const text = document.getElementById(elementId).textContent;
    navigator.clipboard.writeText(text).then(() => {
        btn.classList.add('copied');
        const originalText = btn.innerHTML;
        btn.innerHTML = '✅ Copied!';
        setTimeout(() => {
            btn.classList.remove('copied');
            btn.innerHTML = originalText;
        }, 2000);
    }).catch(err => {
        showToast('Failed to copy', 'error');
    });
}

function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function setLoading(isLoading) {
    const loading = document.getElementById('loading');
    const btnGen = document.getElementById('btn-gen');
    const btnGenAll = document.getElementById('btn-gen-all');

    if (isLoading) {
        loading.classList.remove('hidden');
        btnGen.disabled = true;
        btnGenAll.disabled = true;
        btnGen.innerHTML = '<span class="spinner inline-block mr-2" style="width:18px;height:18px"></span> Generating...';
        btnGenAll.disabled = true;
    } else {
        loading.classList.add('hidden');
        btnGen.disabled = false;
        btnGenAll.disabled = false;
        btnGen.innerHTML = '🖼️ Generate Image';
    }
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ── Keyboard Shortcut ───────────────────────────────────────────────────

document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
        e.preventDefault();
        generatePrompt();
    }
});
