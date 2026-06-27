export function HeroBackground() {
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden>
      <div className="absolute -right-32 -top-32 h-[600px] w-[600px] rounded-full bg-gradient-to-br from-blue-500/20 to-teal-500/10 blur-3xl animate-pulse-glow" />
      <div className="absolute -bottom-48 -left-48 h-[500px] w-[500px] rounded-full bg-gradient-to-tr from-teal-500/15 to-blue-500/10 blur-3xl animate-pulse-glow animation-delay-200" />

      <svg
        className="absolute right-0 top-0 h-full w-1/2 opacity-[0.07]"
        viewBox="0 0 800 800"
        fill="none"
      >
        <defs>
          <pattern
            id="grid"
            width="40"
            height="40"
            patternUnits="userSpaceOnUse"
          >
            <path
              d="M 40 0 L 0 0 0 40"
              fill="none"
              stroke="currentColor"
              strokeWidth="0.5"
              className="text-navy-900"
            />
          </pattern>
        </defs>
        <rect width="800" height="800" fill="url(#grid)" />
      </svg>

      <svg
        className="absolute right-[5%] top-1/2 hidden h-[400px] w-[400px] -translate-y-1/2 lg:block animate-float"
        viewBox="0 0 400 400"
        fill="none"
      >
        <circle cx="200" cy="200" r="180" stroke="url(#ringGrad)" strokeWidth="0.5" opacity="0.4" />
        <circle cx="200" cy="200" r="140" stroke="url(#ringGrad)" strokeWidth="0.5" opacity="0.3" />
        <circle cx="200" cy="200" r="100" stroke="url(#ringGrad)" strokeWidth="0.5" opacity="0.2" />
        <circle cx="200" cy="200" r="8" fill="#14b8a6" opacity="0.6" />
        <circle cx="200" cy="60" r="4" fill="#0ea5e9" opacity="0.8" />
        <circle cx="340" cy="200" r="4" fill="#0ea5e9" opacity="0.6" />
        <circle cx="200" cy="340" r="4" fill="#14b8a6" opacity="0.6" />
        <circle cx="60" cy="200" r="4" fill="#0ea5e9" opacity="0.8" />
        <line x1="200" y1="200" x2="200" y2="60" stroke="#0ea5e9" strokeWidth="0.5" opacity="0.3" />
        <line x1="200" y1="200" x2="340" y2="200" stroke="#14b8a6" strokeWidth="0.5" opacity="0.3" />
        <line x1="200" y1="200" x2="200" y2="340" stroke="#0ea5e9" strokeWidth="0.5" opacity="0.3" />
        <line x1="200" y1="200" x2="60" y2="200" stroke="#14b8a6" strokeWidth="0.5" opacity="0.3" />
        <defs>
          <linearGradient id="ringGrad" x1="0" y1="0" x2="400" y2="400">
            <stop stopColor="#0ea5e9" />
            <stop offset="1" stopColor="#14b8a6" />
          </linearGradient>
        </defs>
      </svg>
    </div>
  );
}

export function PageHeroBackground() {
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden>
      <div className="absolute inset-0 bg-gradient-to-b from-blue-500/5 via-transparent to-transparent" />
      <div className="absolute right-0 top-0 h-96 w-96 rounded-full bg-teal-500/10 blur-3xl" />
    </div>
  );
}
