# Frontend

Decisions below are ruled (2026-08-25). Screens are being designed in Claude Design first; this file is the reference for what gets built once that's ready.

## Progress (2026-08-26)

Basic scaffold done at `Frontend/` (Vite + React, confirmed against npm/context7 as latest stable, not snapshot, as of 2026-08-26):

- `react`/`react-dom` 19.2.8, `vite` 8.2.2, `@vitejs/plugin-react` 6.1.0 — requires Node `^20.19.0 || >=22.12.0` (local Node 22.20.0 OK).
- `tailwindcss`/`@tailwindcss/vite` 4.3.3 — v4 uses the Vite plugin + `@import "tailwindcss"` in `src/index.css`, no `tailwind.config.js`.
- Installed but not yet wired into screens: `react-router-dom` 7.18.2, `react-hook-form` 7.86.0, `@tanstack/react-query` 5.102.5, `react-hot-toast` 2.6.0, `axios` 1.20.0, `amazon-cognito-identity-js` 6.3.20, `jszip` 3.10.1, `motion` 13.1.1.
- `src/main.jsx` wraps the app in `QueryClientProvider` + `Toaster`. `src/App.jsx` has a `BrowserRouter` with a single placeholder route. Empty `src/pages/`, `src/components/`, `src/context/`, `src/lib/` created for upcoming work.
- Default Vite template content (demo assets, counter, docs links) removed. `npm run build` verified working.
- Not yet done: auth screens, axios interceptor, route guards, event/gallery screens, the "Frontend app" Jenkins job (build + sync + invalidate).

`Frontend/Infra/` Terraform written (2026-08-26), matching `Infrastructure/`'s shape: own root (`providers.tf`/`variables.tf`/`imports.tf`), one module (`modules/site/`), `cicd/Jenkinsfile`.

- **Own state, shared state bucket:** `backend "s3"` points at the same `glimpses-terraform-state` bucket as `Infrastructure/`, but a different key (`glimpses/frontend/terraform.tfstate`) — a real separate state, no new bucket needed.
- **`modules/site/`** = one S3 bucket (`glimpses-frontend`, private, `block_public_*` all true — no S3 "static website hosting" toggle) + one CloudFront distribution reading it via **OAC**, the same private-bucket-behind-OAC pattern as the existing `photos` bucket/distribution, not the public S3-website-endpoint pattern FRONTEND.md's wording could also be read as — chosen for consistency with what's already built and because it's strictly more secure (no public bucket at all).
- **Cache split**, done via `ordered_cache_behavior { path_pattern = "assets/*" }` (Vite's hashed JS/CSS output dir) with a 1-year TTL, vs. `default_cache_behavior` (everything else, including `index.html`) with TTLs forced to 0 — un-cached, so a deploy is visible immediately.
- **SPA routing fix:** `custom_error_response` maps both 403 and 404 → `/index.html` with response code 200, so client-side routes work on refresh/deep link.
- **Jenkins job ("Frontend infra"):** `Frontend/Infra/cicd/Jenkinsfile` — plain `init`/`validate`/`apply` in `Frontend/Infra` (no `-target`, since this is its own root, not a module inside the shared `Infrastructure` state).
- Verified: `terraform fmt` clean, `terraform validate` passes.

## Stack

- **React + Vite** (CRA is deprecated, not used; no Next.js — there's no server, S3 is a static file host).
- **Tailwind CSS** for styling.
- **react-router-dom** for client-side routing.
- **react-hook-form** for forms (login/signup/create-event/etc.).
- **React Query** for data fetching, specifically for the poll-until-done endpoints (`jobs/{jobId}/status`, `downloads/{downloadId}/status`) via `refetchInterval`.
- **react-hot-toast** for notifications.
- **Custom inline SVGs** for icons, matching the Claude Design mockups — **Font Awesome only as a fallback** for any icon the mockups don't cover.
- **axios**, with an interceptor that attaches the Cognito ID token to every request and refreshes + retries on `401`.
- **amazon-cognito-identity-js** (or equivalent open-source SRP-capable Cognito client) for auth — no Cognito Hosted UI, screens are custom.
- **React Context** for cross-screen app state (current event, upload/zip progress that must survive navigation, multi-select mode) — chosen over Redux/Zustand since state needs here are shallow and don't need a dedicated store library.
- **`motion`** (the Framer Motion successor) for the photo-viewer's full-screen drag-to-dismiss sheet — spring-based, pointer-capture drag, matches the `apple-design` skill's fluid-interface principles (velocity handoff, momentum projection, rubber-banding) more directly than hand-rolled pointer events.
- Client-side zip library (e.g. JSZip, open-source) for the multi-photo upload fallback — see Upload flow below.
- All libraries: open-source only.

## Hosting & infra

- S3 bucket (static website hosting) as origin, fronted by a **second, independent CloudFront distribution** — not the existing photos distribution (`Infrastructure/modules/cloudfront`), which is scoped to `photos/`/`thumbnails/`/`qrcodes/` via OAC and has a different cache lifecycle (cache-forever images vs. `index.html`, which must never be stale after a deploy).
- New distribution needs: custom error response (403/404 → `/index.html`, HTTP 200) for SPA client-side routing to work on refresh/deep link, and split cache behavior (hashed JS/CSS bundles cached long/immutable, `index.html` never cached).
- Combining into one multi-origin distribution was considered and rejected — CORS to API Gateway is unavoidable either way (different domain regardless), so the only thing a single distribution would save is one domain, not worth mixing two different cache lifecycles into one resource.
- Terraform for all frontend infra (S3 bucket, this CloudFront distribution, and any future frontend-only modules) lives under **`Frontend/Infra/`**, as its **own independent Terraform root and state** — deliberately separate from `Infrastructure/`'s single shared state (which every backend module currently applies into via `terraform apply -target=module.X`), so a frontend deploy can never touch backend state.
- Two new Jenkins jobs:
  - **Frontend infra** — `dir('Frontend/Infra')`, own `init`/`plan`/`apply` (not `-target` against the `Infrastructure` root, since it's a separate state).
  - **Frontend app** — pulls `terraform output` from the `cognito`, `api_gateway`, and frontend-infra states, writes `.env.production`, runs `npm run build`, syncs the build output to the S3 bucket, invalidates the CloudFront distribution.

## Config delivery

Cognito User Pool ID, App Client ID, and the API Gateway invoke URL are baked in at **build time** via Vite env vars (`.env.production`, generated by the Jenkins job from `terraform output`) — not fetched at runtime from a `config.json`. None of these are secrets (the Cognito app client has `generate_secret = false`), and these values change rarely, so a rebuild-on-change is an acceptable cost for the simpler setup.

## Auth (Cognito)

Confirmed against `Infrastructure/modules/cognito/cognito.tf`:

- Custom screens only (no Hosted UI): **login, signup, email-verification-code, forgot-password/reset**.
- Login is by **email** (`username_attributes = ["email"]`).
- Signup fields: email, password (8+ chars, upper+lower+number required, symbols not required), and `name` (required standard attribute — not optional).
- Signup requires email verification via a code before sign-in works (`auto_verified_attributes = ["email"]`, `CONFIRM_WITH_CODE`).
- MFA is off — no MFA screen needed.
- Auth flows enabled: SRP and plain password (`ALLOW_USER_SRP_AUTH`, `ALLOW_USER_PASSWORD_AUTH`); refresh tokens valid 30 days.
- App client has **no secret** — safe for a browser app, and means pool/client IDs are non-sensitive config (see Config delivery above).
- Every API call attaches `Authorization: Bearer <idToken>` — must be the **ID token**, not the access token (the authorizer checks the `aud` claim, which only the ID token carries). The axios interceptor handles attaching it and refreshing on `401`.
- **Token storage: localStorage, not an httpOnly cookie.** An httpOnly cookie can only be set by a `Set-Cookie` response header from a server — the browser talks directly to Cognito via SRP in this design, with no auth-proxy Lambda in between that could set one, and API Gateway's authorizer reads the token from the `Authorization` header, not a cookie. Adding real httpOnly-cookie support would mean a new auth-proxy Lambda plus CSRF mitigation (cookies auto-attach; bearer headers don't) — out of scope for now. Mitigate the real risk (XSS) directly instead: no `dangerouslySetInnerHTML`/`eval`, minimal dependencies, CSP header on the frontend CloudFront distribution.

## Upload flow

- `POST /events/{eventId}/upload-url` (`Backend/upload_status/src/Manager/manager.py`) mints exactly **one** presigned PUT URL per job, always targeting a single `original.zip` object — there is no per-file or multi-file upload path in the backend; Step Functions' `Extract` step unzips it server-side afterward.
- For a "pick multiple photos" UX, the frontend must zip client-side before the PUT (open-source lib, e.g. JSZip). A "bring your own zip" path also works without any client-side zip library.
- **Batch cap: 500 photos** on the multi-select-then-client-zip path (JSZip). **No cap** on the "bring your own zip" path, since the frontend never touches the individual files there — it's a single file PUT regardless of what's inside.

## Marketing site

A public marketing site (`Glimpses Site.dc.html` in the design project — Landing/About/How-it-works pages, sticky glass header, Log in/Sign up entry points into the app) is **in scope** for this build, alongside the app itself.

## Known backend constraint to design around

Every Lambda failure (any raised `ValueError` — not-found, not-authorized, bad state, or an actual bug) surfaces as a generic `502` with an unhelpful body (`Infrastructure`/Lambdas don't register a Powertools exception handler yet). The frontend cannot distinguish these cases by status code today — screens need a generic error state, not per-case messaging, until the backend adds proper exception handling.
