import { useState } from "react";

const MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"];
const DOW = ["S","M","T","W","T","F","S"];

export default function Calendar({ available, selected, onSelect }) {
  const today = new Date(); today.setHours(0,0,0,0);
  const [view, setView] = useState(() => ({ y: today.getFullYear(), m: today.getMonth() }));

  const first = new Date(view.y, view.m, 1);
  const daysInMonth = new Date(view.y, view.m + 1, 0).getDate();
  const leading = first.getDay();

  const cells = [];
  for (let i = 0; i < leading; i++) cells.push(null);
  for (let d = 1; d <= daysInMonth; d++) cells.push(d);

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
    <div className="select-none">
      <div className="flex items-center justify-between mb-3">
        <button type="button" onClick={() => shift(-1)} className="w-9 h-9 rounded-full hover:bg-ocean-100 text-ocean-700">←</button>
        <div className="font-semibold text-ocean-900">{MONTHS[view.m]} {view.y}</div>
        <button type="button" onClick={() => shift(1)} className="w-9 h-9 rounded-full hover:bg-ocean-100 text-ocean-700">→</button>
      </div>
      <div className="grid grid-cols-7 text-center text-xs text-ocean-500 mb-1">
        {DOW.map((d, i) => <div key={i} className="py-1">{d}</div>)}
      </div>
      <div className="grid grid-cols-7 gap-1">
        {cells.map((d, i) => {
          if (!d) return <div key={i} />;
          const key = iso(d);
          const dayDate = new Date(view.y, view.m, d);
          const isPast = dayDate < today;
          const has = !!available[key];
          const isSel = selected === key;
          const base = "aspect-square flex items-center justify-center rounded-full text-sm relative transition-colors";
          if (isSel) return <button type="button" key={i} className={`${base} bg-ocean-600 text-white font-semibold shadow`}
            onClick={() => onSelect(key)}>{d}</button>;
          if (has && !isPast) return <button type="button" key={i} className={`${base} hover:bg-ocean-100 text-ocean-900 font-medium`}
            onClick={() => onSelect(key)}>
            {d}
            <span className="absolute bottom-1 w-1 h-1 rounded-full bg-ocean-500" />
          </button>;
          return <div key={i} className={`${base} text-ocean-300`}>{d}</div>;
        })}
      </div>
      <div className="flex items-center gap-4 mt-3 text-xs text-ocean-600">
        <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-ocean-500" />available</span>
        <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-ocean-600" />selected</span>
      </div>
    </div>
  );
}
