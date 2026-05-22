export function Stars({ value = 0, size = 18, className = "" }) {
  const v = Math.round(value);
  return (
    <span className={`inline-flex items-center ${className}`} aria-label={`${value} out of 5 stars`}>
      {[1,2,3,4,5].map(i => (
        <svg key={i} width={size} height={size} viewBox="0 0 20 20"
          fill={i <= v ? "#f59e0b" : "#e2e8f0"} stroke="#f59e0b" strokeWidth="0.5">
          <path d="M10 1.5l2.6 5.27 5.81.85-4.2 4.1.99 5.78L10 14.77l-5.2 2.73.99-5.78-4.2-4.1 5.81-.85L10 1.5z" />
        </svg>
      ))}
    </span>
  );
}

export function StarInput({ value, onChange, size = 32 }) {
  return (
    <div className="flex items-center gap-1" role="radiogroup">
      {[1,2,3,4,5].map(i => (
        <button key={i} type="button" onClick={() => onChange(i)} aria-label={`${i} stars`}
          className="transition-transform hover:scale-110 focus:outline-none focus:ring-2 focus:ring-amber-400 rounded">
          <svg width={size} height={size} viewBox="0 0 20 20"
            fill={i <= value ? "#f59e0b" : "transparent"} stroke="#f59e0b" strokeWidth="1.2">
            <path d="M10 1.5l2.6 5.27 5.81.85-4.2 4.1.99 5.78L10 14.77l-5.2 2.73.99-5.78-4.2-4.1 5.81-.85L10 1.5z" />
          </svg>
        </button>
      ))}
    </div>
  );
}
