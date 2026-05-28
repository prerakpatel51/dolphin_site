export const MAX_REVIEW_PHOTOS = 5;
export const MAX_REVIEW_PHOTO_DIMENSION = 1600;
export const REVIEW_PHOTO_JPEG_QUALITY = 0.82;

export function formatPhotoSize(bytes) {
  if (!Number.isFinite(bytes) || bytes <= 0) return "0 KB";
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function imageFromFile(file) {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file);
    const image = new Image();
    image.onload = () => {
      URL.revokeObjectURL(url);
      resolve(image);
    };
    image.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error(`${file.name} could not be read as an image.`));
    };
    image.src = url;
  });
}

function canvasToBlob(canvas, quality) {
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob) resolve(blob);
      else reject(new Error("Image could not be compressed."));
    }, "image/jpeg", quality);
  });
}

function resizedDimensions(width, height) {
  const largest = Math.max(width, height);
  if (largest <= MAX_REVIEW_PHOTO_DIMENSION) return { width, height };
  const ratio = MAX_REVIEW_PHOTO_DIMENSION / largest;
  return {
    width: Math.max(1, Math.round(width * ratio)),
    height: Math.max(1, Math.round(height * ratio)),
  };
}

export async function prepareReviewPhotos(fileList) {
  const originalFiles = Array.from(fileList || []);
  const selectedFiles = originalFiles.slice(0, MAX_REVIEW_PHOTOS);
  const warnings = [];

  if (originalFiles.length > MAX_REVIEW_PHOTOS) {
    warnings.push(`Only the first ${MAX_REVIEW_PHOTOS} images will be uploaded.`);
  }

  const files = [];
  for (const file of selectedFiles) {
    if (!file.type.startsWith("image/")) {
      warnings.push(`${file.name} was skipped because it is not an image.`);
      continue;
    }

    const image = await imageFromFile(file);
    const next = resizedDimensions(image.naturalWidth, image.naturalHeight);
    const canvas = document.createElement("canvas");
    canvas.width = next.width;
    canvas.height = next.height;
    const context = canvas.getContext("2d", { alpha: false });
    context.fillStyle = "#ffffff";
    context.fillRect(0, 0, next.width, next.height);
    context.drawImage(image, 0, 0, next.width, next.height);

    const blob = await canvasToBlob(canvas, REVIEW_PHOTO_JPEG_QUALITY);
    const baseName = file.name.replace(/\.[^.]+$/, "") || "review-photo";
    const compressed = new File([blob], `${baseName}.jpg`, {
      type: "image/jpeg",
      lastModified: Date.now(),
    });

    files.push(compressed.size < file.size ? compressed : file);
  }

  return { files, warnings };
}
