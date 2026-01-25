// Capitalizes the first letter of a string.
export function capitalizeFirstLetter(val) {
  if (!val) return '';
  return String(val).charAt(0).toUpperCase() + String(val).slice(1);
}

 // Return a color based on the fake news probability score.
export function getScoreColor(score) {
  if (score < 0.3) return '#4caf50'; // green
  if (score < 0.7) return '#ff9800'; // orange
  return '#ff5555'; // red
}

// Calculate background color intensity for highlighted words.
export function valueToBackground(value) {
  if (!value) return 'transparent';
  
  const intensity = Math.min(Math.abs(value), 1);
  return value < 0 
    ? `rgba(210, 0, 0, ${intensity})` //red
    : `rgba(0, 210, 0, ${intensity})`; //green
}

// Auto-resizes a textarea based on content height.
export function autoResize(event) {
  const el = event.target;
  el.style.height = 'auto';
  el.style.height = el.scrollHeight + 'px';
}