# Accessibility — WCAG 2.1 AA Checklist

This is our contract. Every page must pass these checks before merge.

---

## 1. Perceivable

- [x] **1.1.1 Non‑text content** — every icon has `aria-hidden="true"` or an adjacent label.
- [x] **1.3.1 Info & relationships** — semantic landmarks (`<header>`, `<main>`, `<nav>`, `<aside>`, `<footer>`); tables use `<caption>` and `<th scope>`.
- [x] **1.4.3 Contrast (minimum)** — text ≥ 4.5:1; large text ≥ 3:1; UI components ≥ 3:1. Tokens verified in both light and dark.
- [x] **1.4.4 Resize text** — no fixed `px` font‑sizes on body copy; `rem` everywhere.
- [x] **1.4.11 Non‑text contrast** — focus rings and form borders meet 3:1.
- [x] **1.4.12 Text spacing** — no `line-height` overrides below 1.5 for body.

## 2. Operable

- [x] **2.1.1 Keyboard** — every interactive element reachable; no keyboard traps.
- [x] **2.1.2 No keyboard trap** — dialogs trap focus while open and restore on close.
- [x] **2.4.1 Bypass blocks** — "Skip to content" link as first focusable element.
- [x] **2.4.2 Page titled** — every route sets `<title>` via `react-helmet-async`.
- [x] **2.4.3 Focus order** — DOM order matches visual order.
- [x] **2.4.6 Headings & labels** — descriptive headings and labels.
- [x] **2.4.7 Focus visible** — 2 px ring on all focusable elements; never `outline:none` without a replacement.
- [x] **2.5.3 Label in name** — visible label is the accessible name.

## 3. Understandable

- [x] **3.1.1 Language of page** — `<html lang="bn|en">` set on boot.
- [x] **3.2.1 On focus** — focusing a control does not change context unexpectedly.
- [x] **3.2.2 On input** — form submission requires explicit user action.
- [x] **3.3.1 Error identification** — errors are announced (`aria-invalid="true"` + adjacent message).
- [x] **3.3.2 Labels or instructions** — every input has a `<label>` or `aria-label`.

## 4. Robust

- [x] **4.1.1 Parsing** — valid HTML (verified by `eslint-plugin-jsx-a11y`).
- [x] **4.1.2 Name, role, value** — custom widgets expose role/state to AT.
- [x] **4.1.3 Status messages** — toasts use `aria-live="polite"`.

---

## Reduced motion

A global `<MotionConfig reducedMotion="user">` (Framer Motion) honors the OS setting. CSS animations check `@media (prefers-reduced-motion: reduce)`.

## Skip link

Rendered as the first child of `<body>`; visible on focus; jumps to `<main id="main">`.

## Skip‑target verification

Run `npx axe http://localhost:5173` (when running) and ensure 0 critical issues.