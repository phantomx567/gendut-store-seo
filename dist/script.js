(() => {
  const checks = Array.from(document.querySelectorAll('.checks input[type="checkbox"]'));
  const progress = document.getElementById('check-progress');
  const reset = document.getElementById('reset-checklist');
  if (!checks.length || !progress || !reset) return;
  const update = () => {
    const count = checks.filter(check => check.checked).length;
    progress.textContent = count === checks.length
      ? '4 dari 4 hal sudah kamu periksa. Baca detail produk sekali lagi sebelum membeli.'
      : `${count} dari ${checks.length} hal sudah kamu periksa.`;
  };
  progress.hidden = false;
  reset.hidden = false;
  checks.forEach(check => check.addEventListener('change', update));
  reset.addEventListener('click', () => {
    checks.forEach(check => { check.checked = false; });
    update();
  });
  update();
})();
