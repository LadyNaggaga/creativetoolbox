// toolbox.io — tiny helper for figures
// 1) inlineSVG(url, slot)  -> fetches the SVG and replaces `slot` with parsed <svg>.
//    Returns the live <svg> element so callers can hook anime.js to it.
// 2) downloadPNG(svgEl, filename, scale=2) -> rasterizes the inlined SVG and downloads PNG.

(function () {
  async function inlineSVG(url, slot) {
    const res = await fetch(url);
    const txt = await res.text();
    const doc = new DOMParser().parseFromString(txt, 'image/svg+xml');
    const svg = doc.documentElement;
    svg.removeAttribute('width');
    svg.removeAttribute('height');
    svg.style.width = '100%';
    svg.style.height = 'auto';
    svg.style.display = 'block';
    slot.replaceWith(svg);
    return svg;
  }

  function downloadPNG(svgEl, filename, scale) {
    scale = scale || 2;
    const vb = svgEl.viewBox.baseVal;
    const w = vb && vb.width  ? vb.width  : svgEl.clientWidth  || 1200;
    const h = vb && vb.height ? vb.height : svgEl.clientHeight || 630;

    // clone, ensure xmlns, serialize
    const clone = svgEl.cloneNode(true);
    clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
    clone.setAttribute('width',  w);
    clone.setAttribute('height', h);
    const xml = new XMLSerializer().serializeToString(clone);
    const blob = new Blob([xml], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(blob);

    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement('canvas');
      canvas.width  = w * scale;
      canvas.height = h * scale;
      const ctx = canvas.getContext('2d');
      ctx.fillStyle = '#d6d6d4';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      URL.revokeObjectURL(url);
      canvas.toBlob((b) => {
        const a = document.createElement('a');
        a.href = URL.createObjectURL(b);
        a.download = filename;
        document.body.appendChild(a); a.click(); a.remove();
        setTimeout(() => URL.revokeObjectURL(a.href), 1000);
      }, 'image/png');
    };
    img.src = url;
  }

  window.toolboxFigure = { inlineSVG, downloadPNG };
})();
