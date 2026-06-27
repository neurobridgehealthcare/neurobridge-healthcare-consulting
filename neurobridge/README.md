# NeuroBridge Healthcare Consulting

A modern, premium marketing website for NeuroBridge Healthcare Consulting — a healthcare operations and neurophysiology development firm.

## Tech Stack

- **Next.js 15** (App Router)
- **React 19**
- **Tailwind CSS 4**
- **TypeScript**
- **Lucide React** icons

## Getting Started

```bash
cd neurobridge
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Pages

| Route | Description |
|-------|-------------|
| `/` | Home |
| `/services` | Service catalog |
| `/solutions` | Tailored solution pathways |
| `/about` | Founder & firm information |
| `/capability-statement` | PDF-style capability statement |
| `/case-studies` | Development initiatives |
| `/contact` | Schedule consultation form |

## Project Structure

```
neurobridge/
├── src/
│   ├── app/              # Next.js App Router pages
│   ├── components/
│   │   ├── about/        # About page components
│   │   ├── capability/   # Capability statement components
│   │   ├── home/         # Homepage sections
│   │   ├── layout/       # Header, Footer
│   │   └── ui/           # Reusable UI components
│   └── lib/
│       ├── data.ts       # Site content & configuration
│       └── utils.ts      # Utility helpers
├── public/
└── package.json
```

## Build

Production build:

```bash
npm run clean   # optional — clears stale Next.js cache
npm run build
npm start
```

Open [http://localhost:3000](http://localhost:3000).

## Troubleshooting

### Blank page or Internal Server Error

This usually means the Next.js cache (`.next/`) is stale — often after running `npm run build` while `npm run dev` is still running.

**Fix:**

```bash
# Stop the dev server (Ctrl+C), then:
npm run clean
npm run dev
```

If issues persist:

```bash
npm run clean
rm -rf node_modules
npm install
npm run dev
```

## Deploy to Vercel

Vercel is the recommended host for this Next.js site. It provides a free public URL (e.g. `https://neurobridge.vercel.app`).

### Option A — Deploy from GitHub (recommended)

1. **Push the project to GitHub**
   - Create a new repository
   - Push the `edgeone-orb` repo (or only the `neurobridge/` folder as its own repo)

2. **Import into Vercel**
   - Go to [https://vercel.com/new](https://vercel.com/new)
   - Import your GitHub repository
   - If the repo root contains other projects, set **Root Directory** to `neurobridge`

3. **Configure the project**
   - **Framework Preset:** Next.js (auto-detected)
   - **Build Command:** `npm run build`
   - **Output Directory:** `.next` (default)
   - **Install Command:** `npm install`

4. **Deploy**
   - Click **Deploy**
   - Vercel builds and assigns a public URL

5. **Custom domain (optional)**
   - In Vercel project settings → **Domains**, add your domain (e.g. `neurobridgehealth.com`)

### Option B — Deploy with Vercel CLI

```bash
npm install -g vercel
cd neurobridge
vercel
```

Follow the prompts. Run `vercel --prod` for production deployment.

### After deployment — test these URLs

Replace `YOUR-URL` with your Vercel domain:

- `https://YOUR-URL/`
- `https://YOUR-URL/about`
- `https://YOUR-URL/capability-statement`
- `https://YOUR-URL/services`
- `https://YOUR-URL/solutions`
- `https://YOUR-URL/case-studies`
- `https://YOUR-URL/contact`

## Environment Variables

No environment variables are required for the current static marketing site. If you add form submission (e.g. Resend, Formspree), configure secrets in Vercel → **Settings → Environment Variables**.
