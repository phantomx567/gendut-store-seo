(() => {
  const tools = document.getElementById('game-tools');
  const search = document.getElementById('game-search');
  const cards = [...document.querySelectorAll('[data-game]')];
  if (!tools || !search || !cards.length) return;
  const count = document.getElementById('game-count');
  const empty = document.getElementById('game-empty');
  const clear = document.getElementById('search-clear');
  const filters = [...document.querySelectorAll('[data-filter]')];
  let category = 'all';
  const normalize = value => value.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('id').trim();
  const update = () => {
    const term = normalize(search.value);
    let visible = 0;
    for (const card of cards) {
      const name = normalize(card.dataset.game);
      const aliases = name.includes('mobile legends') ? ' mlbb' : name.includes('honor of kings') ? ' hok' : name.includes('genshin') ? ' gi' : name.includes('free fire') ? ' ff' : '';
      const match = (category === 'all' || card.dataset.category === category) && (name + aliases).includes(term);
      card.hidden = !match;
      visible += Number(match);
    }
    count.textContent = `${visible} dari ${cards.length} pilihan ditampilkan.`;
    empty.hidden = visible > 0;
    clear.hidden = !search.value;
    filters.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.filter === category)));
  };
  tools.hidden = false;
  const filterGroup = document.getElementById('game-filters');
  if (filterGroup) filterGroup.hidden = false;
  count.hidden = false;
  search.addEventListener('input', update);
  filters.forEach(button => button.addEventListener('click', () => { category = button.dataset.filter; update(); }));
  clear.addEventListener('click', () => { search.value = ''; update(); search.focus(); });
  document.getElementById('reset-search').addEventListener('click', () => { search.value = ''; category = 'all'; update(); search.focus(); });
  update();
})();
