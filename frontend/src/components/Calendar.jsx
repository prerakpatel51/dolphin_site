import { useMemo, useState } from "react";

const MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"];
const DOW = ["S","M","T","W","T","F","S"];

export default function Calendar({ available, selected, onSelect }) {
  const today = new Date(); today.setHours(0,0,0,0);
  const [view, setView] = useState(() => ({ y: today.getFullYear(), m: today.getMonth() }));

  const cells = useMemo(() => {
    const first = new Date(view.y, view.m, 1);
    const daysInMonth = new Date(view.y, view.m + 1, 0).getDate();
    const nextCells = [];
    for (let i = 0; i < first.getDay(); i++) nextCells.push(null);
    for (let d = 1; d <= daysInMonth; d++) nextCells.push(d);
    while (nextCells.length % 7 !== 0) nextCells.push(null);
    return nextCells;
  }, [view.y, view.m]);

  function shift(n) {
    let m = view.m + n, y = view.y;
    if (m < 0) { m = 11; y--; }
    if (m > 11) { m = 0; y++; }
    setView({ y, m });
  }

  function iso(d) {
    return `${view.y}-${String(view.m + 1).padStart(2,"0")}-${String(d).padStart(2,"0")}`;
  }

  return (
    <div className="select-none rounded-2xl bg-white border border-ocean-100 p-2 sm:p-3 shadow-inner shadow-ocean-900/5">
      <div className="flex items-center justify-between mb-2 sm:mb-3">
        <button type="button" aria-label="Previous month" onClick={() => shift(-1)} className="w-8 h-8 sm:w-10 sm:h-10 rounded-full hover:bg-ocean-100 text-ocean-700 inline-flex items-center justify-center">
          <ArrowIcon direction="left" />
        </button>
        <div className="font-display text-lg sm:text-xl text-ocean-950">{MONTHS[view.m]} {view.y}</div>
        <button type="button" aria-label="Next month" onClick={() => shift(1)} className="w-8 h-8 sm:w-10 sm:h-10 rounded-full hover:bg-ocean-100 text-ocean-700 inline-flex items-center justify-center">
          <ArrowIcon />
        </button>
      </div>
      <div className="grid grid-cols-7 justify-center gap-1 text-center text-[10px] sm:text-[11px] font-semibold uppercase tracking-wider text-ocean-500 mb-1">
        {DOW.map((d, i) => <div key={i} className="w-8 sm:w-10 py-0.5 sm:py-1.5">{d}</div>)}
      </div>
      <div className="grid grid-cols-7 justify-center gap-1 sm:gap-1.5">
        {cells.map((d, i) => {
          if (!d) return <div key={i} className="w-8 h-8 sm:w-10 sm:h-10" />;
          const key = iso(d);
          const dayDate = new Date(view.y, view.m, d);
          const isPast = dayDate < today;
          const has = !!available[key];
          const isSel = selected === key;
          const base = "w-8 h-8 sm:w-10 sm:h-10 flex items-center justify-center rounded-full text-[13px] sm:text-sm relative transition-colors focus:outline-none focus:ring-2 focus:ring-ocean-400 focus:ring-offset-1";
          if (isSel) return <button type="button" key={i} aria-pressed="true" className={`${base} bg-ocean-600 text-white font-semibold shadow-lg shadow-ocean-600/25`}
            onClick={() => onSelect(key)}>{d}</button>;
          if (has && !isPast) return <button type="button" key={i} className={`${base} hover:bg-ocean-100 text-ocean-900 font-medium`}
            onClick={() => onSelect(key)}>
            {d}
            <span className="absolute bottom-1 sm:bottom-1.5 w-1 h-1 sm:w-1.5 sm:h-1.5 rounded-full bg-ocean-500" />
          </button>;
          return <div key={i} className={`${base} text-ocean-300`}>{d}</div>;
        })}
      </div>
      <div className="flex items-center gap-4 mt-2.5 sm:mt-4 text-xs text-ocean-600">
        <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-ocean-500" />Available</span>
        <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-ocean-600" />Selected</span>
      </div>
    </div>
  );
}

function ArrowIcon({ direction = "right" }) {
  return (
    <svg aria-hidden="true" viewBox="0 0 20 20" className={`h-5 w-5 ${direction === "left" ? "rotate-180" : ""}`} fill="none">
      <path d="M4 10h11M11 5l5 5-5 5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
