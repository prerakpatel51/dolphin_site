import { useEffect, useMemo, useState } from "react";

export default function ReviewPhotoGallery({ urls = [], className = "" }) {
  const photoUrls = useMemo(() => urls.filter(Boolean), [urls]);
  const [activeIndex, setActiveIndex] = useState(null);
  const activeUrl = activeIndex === null ? "" : photoUrls[activeIndex];

  useEffect(() => {
    if (activeIndex === null) return undefined;
    function handleKeyDown(event) {
      if (event.key === "Escape") setActiveIndex(null);
      if (event.key === "ArrowLeft") setActiveIndex(index => previousIndex(index, photoUrls.length));
      if (event.key === "ArrowRight") setActiveIndex(index => nextIndex(index, photoUrls.length));
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [activeIndex, photoUrls.length]);

  if (photoUrls.length === 0) return null;

  const visibleUrls = photoUrls.slice(0, 4);
  const extraCount = Math.max(0, photoUrls.length - visibleUrls.length);

  return (
    <>
      <div className={`overflow-hidden rounded-xl border border-ocean-100 bg-ocean-50 ${className}`}>
        {photoUrls.length === 1 ? (
          <PhotoButton url={photoUrls[0]} index={0} onOpen={setActiveIndex} className="aspect-[16/10] w-full" priority />
        ) : photoUrls.length === 2 ? (
          <div className="grid grid-cols-2 gap-1 sm:gap-1.5">
            {photoUrls.map((url, index) => (
              <PhotoButton key={`${url}-${index}`} url={url} index={index} onOpen={setActiveIndex} className="aspect-[4/3]" priority={index === 0} />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-3 gap-1 sm:gap-1.5">
            <PhotoButton
              url={photoUrls[0]}
              index={0}
              onOpen={setActiveIndex}
              className="col-span-3 aspect-[16/10] sm:col-span-2 sm:row-span-2 sm:aspect-auto sm:min-h-[220px]"
              priority
            />
            {visibleUrls.slice(1).map((url, offset) => {
              const index = offset + 1;
              const isLastVisible = index === visibleUrls.length - 1 && extraCount > 0;
              return (
                <PhotoButton
                  key={`${url}-${index}`}
                  url={url}
                  index={index}
                  onOpen={setActiveIndex}
                  className="aspect-square"
                  overlay={isLastVisible ? `+${extraCount} photos` : ""}
                />
              );
            })}
          </div>
        )}
      </div>

      {activeUrl && (
        <div className="fixed inset-0 z-50 bg-ocean-950/90 px-4 py-5 sm:p-8" role="dialog" aria-modal="true" aria-label="Review photo viewer">
          <button
            type="button"
            onClick={() => setActiveIndex(null)}
            className="absolute right-4 top-4 rounded-full bg-white/10 px-4 py-2 text-sm font-semibold text-white backdrop-blur hover:bg-white/20"
          >
            Close
          </button>
          <div className="mx-auto flex h-full max-w-6xl flex-col items-center justify-center gap-4">
            <div className="flex w-full items-center justify-between gap-3 text-white">
              <button type="button" onClick={() => setActiveIndex(index => previousIndex(index, photoUrls.length))} className="rounded-full bg-white/10 px-4 py-2 text-sm font-semibold hover:bg-white/20">
                Previous
              </button>
              <span className="text-sm text-ocean-100">{activeIndex + 1} / {photoUrls.length}</span>
              <button type="button" onClick={() => setActiveIndex(index => nextIndex(index, photoUrls.length))} className="rounded-full bg-white/10 px-4 py-2 text-sm font-semibold hover:bg-white/20">
                Next
              </button>
            </div>
            <img src={activeUrl} alt="" className="max-h-[78vh] w-auto max-w-full rounded-xl object-contain shadow-2xl shadow-black/30" />
          </div>
        </div>
      )}
    </>
  );
}

function PhotoButton({ url, index, onOpen, className = "", overlay = "", priority = false }) {
  return (
    <button type="button" onClick={() => onOpen(index)} className={`group relative block overflow-hidden bg-ocean-100 ${className}`} aria-label={`Open review photo ${index + 1}`}>
      <img
        src={url}
        alt=""
        className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
        loading={priority ? "eager" : "lazy"}
        decoding="async"
      />
      <span className="pointer-events-none absolute inset-0 bg-ocean-950/0 transition-colors group-hover:bg-ocean-950/10" />
      {overlay && (
        <span className="absolute inset-0 flex items-center justify-center bg-ocean-950/55 text-sm font-semibold text-white">
          {overlay}
        </span>
      )}
    </button>
  );
}

function previousIndex(index, length) {
  if (index === null || length <= 0) return null;
  return (index - 1 + length) % length;
}

function nextIndex(index, length) {
  if (index === null || length <= 0) return null;
  return (index + 1) % length;
}
