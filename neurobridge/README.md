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
| `/services` | Offerings and starting prices |
| `/solutions` | Engagement pathways |
| `/about` | Founder, credentials, and career |
| `/capability-statement` | Printable capability statement |
| `/ventures` | Connectome.news and FOCUS |
| `/case-studies` | Redirects to `/ventures` |
| `/contact` | Email draft (mailto). Nothing is sent by the site |

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

## Contact

The contact form does not post to a server and it never shows a fake “received” state. Submitting it opens the visitor’s email app with a draft to `garrison839@gmail.com`. The message is delivered only when the visitor sends that email. With JavaScript disabled, the form still uses a `mailto:` submit.

To replace this with server-side delivery later, add a provider such as Resend and set:

- `CONTACT_TO` — destination inbox
- `RESEND_API_KEY` — or the provider’s equivalent secret

Do not show success unless the provider accepts the message. Do not deploy this site to production until Brandon approves the copy.

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
   - Confirm who controls the domain before attaching it. As of October 2026, `neurobridgehealth.com` was an expired Squarespace site and ownership was not confirmed.

### Option B — Deploy with Vercel CLI

```bash
npm install -g vercel
cd neurobridge
vercel
```

Follow the prompts. Use a preview deployment until Brandon approves the copy. Do not run `vercel --prod` before that.

### After deployment — test these URLs

Replace `YOUR-URL` with your Vercel domain:

- `https://YOUR-URL/`
- `https://YOUR-URL/about`
- `https://YOUR-URL/capability-statement`
- `https://YOUR-URL/services`
- `https://YOUR-URL/solutions`
- `https://YOUR-URL/ventures`
- `https://YOUR-URL/case-studies` (redirects to `/ventures`)
- `https://YOUR-URL/contact`

## Environment Variables

None are required. The contact path is a `mailto:` draft, described above. A future server-side form would need `CONTACT_TO` and a provider secret in Vercel → **Settings → Environment Variables**.
