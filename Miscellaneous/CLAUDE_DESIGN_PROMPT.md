# Prompt: Generate Claude Design Context Brief

**How to use:** Paste this whole prompt into Claude Code (paths are pre-filled for the Glimpses project). It will read the docs, ask clarifying questions, and output a single `claude-design-context.md` file. Upload/paste *that* file into Claude Design (claude.ai/design) as the opening message of a new project.

---

## PROMPT (send as-is)

You are helping me prepare a design brief to hand off to **Claude Design**, a separate visual-design tool. Do not design anything yourself — your job is to gather context and produce one clean markdown file.

**Step 1 — Read the product docs.**
Recursively read every `.md` file under: `/Users/hridaymulchandani/Desktop/Projects/Resume_Projects_Dump_Imp_Stuff/Glimpses` (product spec: `LOCKED_PRODUCT.md`, `PRODUCT_WALKTHROUGH.md`, etc.).
Locate `FRONTEND.md` inside `/Users/hridaymulchandani/Desktop/Resume_Projects/Glimpses/Miscellaneous/` and treat it as the authoritative source for already-made frontend engineering decisions — extract anything relevant to layout, components, tech choices, naming conventions, visual direction. These are constraints, not suggestions.

**Step 2 — Build the full page inventory.**
From the docs, list every page/screen the product actually needs. Do not start from a generic app-template checklist (file browser, folders, billing, search, etc.) — Glimpses is a face-recognition photo-retrieval product, not general file storage, and several "obvious" pages are explicitly ruled out by the product spec. Build the inventory bottom-up from `LOCKED_PRODUCT.md` / `PRODUCT_WALKTHROUGH.md`, and separately list anything the spec explicitly says is *not* built, so it doesn't get designed by accident.

**Step 3 — Map pages to endpoints.**
Read the API routes in `/Users/hridaymulchandani/Desktop/Resume_Projects/Glimpses/Miscellaneous/BACKEND.md` and produce a page → endpoint(s) table of what data/actions each screen needs.

**Step 4 — Apply the `apple-design` skill.**
Load `/Users/hridaymulchandani/.claude/skills/apple-design`. Summarize its principles (typography, spacing, motion, iconography, color usage, component style) in your own words so they're embedded in the brief. This skill should govern every visual recommendation in the output — note explicitly that Claude Design should apply these principles throughout, not just reference them once.

**Step 5 — Ask clarifying questions before finalizing.**
Stop and ask before writing the final file (don't guess or default silently):
1. Overall aesthetic — minimalist, content-dense, playful, neutral/corporate?
2. Light mode, dark mode, or both (system-aware)?
3. Primary/accent color — do you have one, or should Claude Design propose one?
4. Typography — system font (SF Pro-style) or something else?
5. Reference products — closest to Google Photos, Apple Photos/shared albums, Dropbox, something else, or a mix? Anything to specifically avoid copying?
6. Any existing logo/brand assets to incorporate?
7. Mobile-first or desktop-first priority (the product itself is mobile-web-first per `P-92` — confirm this should also drive the design brief)?
8. Anything in the Step 2 page inventory that's explicitly out of scope for the first design pass?
9. Any known gaps between the backend/product docs (e.g. missing endpoints) that should be flagged to you before design starts, rather than silently designed around?

**Step 6 — Output.**
Write a single file, `claude-design-context.md`, containing, in order:
1. **Product summary** — one paragraph on what we're building and who it's for.
2. **Full page inventory** — every page, one line each on purpose (plus a short "explicitly not built" list).
3. **Page → endpoint mapping table.**
4. **Design decisions already locked in** (from `FRONTEND.md`).
5. **Design principles** (summarized `apple-design` skill).
6. **My answers** to the Step 5 questions.
7. **Final brief paragraph** — written specifically as the first message to be pasted into Claude Design, instructing it to design a fully responsive website (desktop + mobile browser, Chrome/Safari) covering every page listed, following the design principles and locked-in decisions above.

---

### Notes for you (Claude Code)

- Paths above are pre-filled for the Glimpses project — the product-spec docs live in a separate directory from the engineering repo (`Desktop/Projects/Resume_Projects_Dump_Imp_Stuff/Glimpses`), by design; don't treat that as a stale path without checking.
- Double-check `FRONTEND.md` actually lives where stated before reading it.
- Output exactly one file: `claude-design-context.md`.
- For claude.ai/design, use Opus, and paste the contents of that file as the opening message.
