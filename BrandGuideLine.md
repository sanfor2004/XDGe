# Zenith-Tier Brand Guidelines: XDGe (Nano Banana Cyberpunk)

This document establishes the official design system and visual branding rules for the **XDGe — Enterprise-Grade Web Directory Scanner & Dorking Engine**.

---

## 1. Cognitive Persona
- **Target Audience:** Security engineers, penetration testers, security researchers, and developers.
- **Mental Model Targets:** High performance, multi-threaded efficiency, and stealth directory enumeration.
- **Interactive Experience:** High readability, fast terminal logging, high contrast, clean metadata layouts, and informative data summaries.

---

## 2. Aesthetic North Star
- **Vibe:** "Nano Banana Cyberpunk"
- **Characteristics:** Futuristic cybernetic detailing, deep glassmorphic structures, circuit-board vectors, and glowing neon accents.
- **Tone:** Technical, premium, mysterious yet clean, high-performance.

---

## 3. Atomic Tokens

### Colors (HSL-based)
- **Primary Accent (Neon Banana):** `hsl(54, 100%, 50%)` — `#FFEA00` (electric yellow glow)
- **Secondary Accent (Cyber Gold):** `hsl(43, 100%, 48%)` — `#FFB300` (warm gold highlights)
- **Surface Dark (Obsidian Base):** `hsl(220, 15%, 8%)` — `#0D1117` (deep dark grey/black)
- **Surface Elevation (Matte Carbon):** `hsl(215, 14%, 12%)` — `#161B22` (midground card color)
- **Semantic Success:** `hsl(140, 70%, 45%)` — `#2ECC71`
- **Semantic Warning:** `hsl(35, 90%, 50%)` — `#F39C12`
- **Semantic Error:** `hsl(360, 80%, 55%)` — `#E74C3C`

### Typography (Sleek Coding & Display Scales)
- **Display Header:** *Sora* / *Bricolage Grotesque* (Bold, high-impact titles)
- **Body & Labels:** *Geist Variable* / *Inter* (High legibility at small scale)
- **Monospace (Data):** *JetBrains Mono* / *Fira Code* (For URLs, IP addresses, terminal output)

### Dimensional Depth
- **Glassmorphic Base:** `backdrop-filter: blur(20px) saturate(180%); background: rgba(22, 27, 34, 0.7);`
- **Organic Layered Shadows:**
  - 1px thin border: `rgba(255, 234, 0, 0.15)`
  - Card shadow: `0 4px 30px rgba(0, 0, 0, 0.4)`

---

## 4. Signifier Library
- **Scans / Progress:** Rotating circular loaders, pulsing yellow dots.
- **URLs / Links:** Underline on hover with transition, standard system accent color change.
- **Interaction Elements:** All buttons must have a `150ms` transition transition from outline to filled `hsl(54, 100%, 50%)` with dark text.

---

## 5. Motion Lexical
- **Easing Curve:** `cubic-bezier(0.4, 0, 0.2, 1)` (Cinematic & standard fluid transition)
- **Micro-interaction duration:** `150ms`
- **Standard Entrance transition:** `300ms`
