export function createMobilePerception({ video, endpoint, onResult, intervalMs = 1500 }) {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  let timer = null;

  async function capture() {
    if (!video.videoWidth || !video.videoHeight) return;
    canvas.width = Math.min(video.videoWidth, 1280);
    canvas.height = Math.round(canvas.width * video.videoHeight / video.videoWidth);
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.72));
    if (!blob) return;
    const form = new FormData();
    form.append('frame', blob, 'frame.jpg');
    const response = await fetch(endpoint, { method: 'POST', body: form });
    if (!response.ok) throw new Error(`Perception HTTP ${response.status}`);
    onResult(await response.json());
  }

  return {
    start() { if (!timer) timer = setInterval(() => capture().catch(console.error), intervalMs); },
    stop() { if (timer) clearInterval(timer); timer = null; },
    capture
  };
}
