Drop marketing-site images here using the exact filenames below — each one is already wired up in the corresponding page and falls back to a placeholder box until the file exists, so nothing else needs to change.

Landing (`src/pages/marketing/Landing.jsx`) — hero collage, `.jpg`:
- `site-hero-1.jpg` — candid group shot at an event
- `site-hero-2.jpg` — guest holding up a phone
- `site-hero-3.jpg` — two friends laughing
- `site-hero-4.jpg` — table toast, candid

About (`src/pages/marketing/About.jsx`) — `.jpg`:
- `site-about-wide.jpg` — wide candid shot, guests photographing each other
- `site-aud-wedding.jpg`, `site-aud-conf.jpg`, `site-aud-reunion.jpg`, `site-aud-any.jpg` — "Who it's for" cards

How it works (`src/pages/marketing/HowItWorks.jsx`) — tech stack logos, `.png`:
- `stack-aws-lambda.png`, `stack-aws-step-functions.png`, `stack-amazon-rekognition.png`, `stack-amazon-s3.png`, `stack-amazon-dynamodb.png`, `stack-dynamodb-streams.png`, `stack-amazon-api-gateway.png`, `stack-amazon-cloudfront.png`, `stack-aws-waf.png`, `stack-amazon-eventbridge.png`, `stack-python.png`, `stack-aws-lambda-powertools.png`, `stack-boto3.png`, `stack-terraform.png`, `stack-jenkins.png`

This folder is served as-is by Vite (files under `public/` are copied verbatim to the build output root), so a page just references `images/marketing/<filename>` (relative, no leading slash — this repo uses relative paths everywhere so it stays host/subpath-agnostic for anyone replicating it) — no import needed.
