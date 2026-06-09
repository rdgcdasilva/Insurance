# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Is

A static, single-file academic portfolio website for Prof. Dr. Rodrigo Cunha da Silva. The entire site lives in `index.html` — no build step, no dependencies, no backend. It is hosted via GitHub Pages at `https://rdgcdasilva.github.io/Insurance/`.

`Insurance-main.zip` contains a legacy `Insurance.csv` dataset unrelated to the portfolio.

## Development

Open `index.html` directly in a browser — no server required. For local development with live reload, any static file server works:

```bash
python3 -m http.server 8080
# or
npx serve .
```

There are no npm packages, no build process, and no environment variables.

## Architecture

Everything is in a single `index.html` file (~1220 lines), structured as three co-located layers:

- **CSS** (lines ~10–477): Embedded `<style>` block. Uses CSS custom properties as design tokens (`--primary: #5a3e8c`, `--secondary: #2a7a8c`, `--gold: #c8922a`). Layout uses CSS Grid and Flexbox. Responsive breakpoint at 900px. Fonts: Playfair Display, Inter, JetBrains Mono (loaded from Google Fonts).
- **HTML** (lines ~479–1183): Semantic sections — `#hero`, `#about`, `#career`, `#research`, `#publications`, `#teaching`, `#webapps`, `#contact`. Navigation anchors map directly to these IDs.
- **JavaScript** (lines ~1184–1217): Minimal vanilla JS — Intersection Observer for scroll-triggered `.fade-in` animations, active nav-link highlighting on scroll, and a simulated contact form submission (no actual backend call).

## Linked External Apps

Two interactive apps are referenced from the portfolio but live in separate paths on the same GitHub Pages domain:

- **HospMap** (org-level hospitality diagnosis): `hospitality-app/mapeamento-hospitalidade.html` — not present in this repo
- **Avaliação de Hospitalidade** (individual assessment): `hospitality-app/avaliacao-hospitalidade.html` — not present in this repo

When adding or editing content that references these apps, the URLs point to `https://rdgcdasilva.github.io/Insurance/...`.

## Conventions

- All styling changes go in the embedded `<style>` block; do not add external CSS files.
- JavaScript stays in the single embedded `<script>` block at the bottom of the file.
- Content is in Brazilian Portuguese. Maintain that language for all user-visible text.
- Section order in the HTML matches the navigation order — keep them in sync.
