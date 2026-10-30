(() => {
  const STORAGE_KEY = 'learnhub.studyTasks.v1';
  const form = document.getElementById('study-task-form');
  const list = document.getElementById('study-task-list');
  const count = document.getElementById('task-count');
  if (!form || !list || !count) return;

  let tasks = [];
  try { tasks = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'); }
  catch (_) { tasks = []; }

  const save = () => localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
  const render = () => {
    list.replaceChildren();
    count.textContent = `${tasks.length} ${tasks.length === 1 ? 'task' : 'tasks'}`;
    if (!tasks.length) {
      const empty = document.createElement('p'); empty.className = 'muted';
      empty.textContent = 'No tasks yet. Add one small learning goal to get started.';
      list.appendChild(empty); return;
    }
    tasks.sort((a, b) => a.date.localeCompare(b.date));
    tasks.forEach(task => {
      const row = document.createElement('article'); row.className = `task-item${task.done ? ' task-done' : ''}`;
      const check = document.createElement('input'); check.type = 'checkbox'; check.checked = task.done;
      check.setAttribute('aria-label', `Mark ${task.title} complete`);
      check.addEventListener('change', () => { task.done = check.checked; save(); render(); });
      const details = document.createElement('div'); details.className = 'task-details';
      const title = document.createElement('strong'); title.textContent = task.title;
      const meta = document.createElement('span'); meta.textContent = `${task.date} · ${task.minutes} min`;
      details.append(title, meta);
      const remove = document.createElement('button'); remove.type = 'button'; remove.className = 'task-remove';
      remove.textContent = 'Remove'; remove.addEventListener('click', () => { tasks = tasks.filter(t => t.id !== task.id); save(); render(); });
      row.append(check, details, remove); list.appendChild(row);
    });
  };

  form.addEventListener('submit', event => {
    event.preventDefault();
    const title = document.getElementById('task-title').value.trim();
    const date = document.getElementById('task-date').value;
    const minutes = Number(document.getElementById('task-minutes').value);
    if (!title || !date || !Number.isInteger(minutes) || minutes < 5 || minutes > 600) return;
    tasks.push({ id: `${Date.now()}-${Math.random().toString(16).slice(2)}`, title, date, minutes, done: false });
    save(); form.reset(); document.getElementById('task-minutes').value = 30; render();
  });
  render();
})();
