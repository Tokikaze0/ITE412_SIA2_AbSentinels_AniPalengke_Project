// Notifications: save + show toasts
(function(){
  const { readJson, writeJson, generateId, getCurrentUser, showToast, formatDate } = window.AniP;

  function seedNotifications(){ if (!readJson('notifications', null)) writeJson('notifications', []); }
  function getNotifications(){ return readJson('notifications', []); }
  function setNotifications(list){ writeJson('notifications', list); }

  function notify({ title, message, type='success', userId=null, role=null }){
    const list = getNotifications();
    const n = { id: generateId('ntf'), title, message, type, userId, role, createdAt: Date.now() };
    list.unshift(n);
    setNotifications(list);
    const current = getCurrentUser();
    if (!current) return;
    if ((userId && current.id === userId) || (role && current.role === role) || (!userId && !role)) {
      showToast({ title, message, type });
    }
  }

  function getForUser(user){
    const list = getNotifications();
    return list.filter(n => (!n.userId && !n.role) || n.userId === user.id || n.role === user.role);
  }

  function renderNotificationsTable(targetSelector, user, isAdmin){
    const el = document.querySelector(targetSelector);
    if (!el) return;
    const rows = (isAdmin ? getNotifications() : getForUser(user)).map(n => `
      <tr>
        <td>${n.id}</td>
        <td>${n.title}</td>
        <td>${n.message}</td>
        <td>${n.role || '—'}</td>
        <td>${n.userId || '—'}</td>
        <td>${formatDate(n.createdAt)}</td>
      </tr>
    `).join('');
    el.innerHTML = rows || `<tr><td colspan="6" class="muted">No notifications yet</td></tr>`;
  }

  window.Notifications = { seedNotifications, notify, getNotifications, getForUser, renderNotificationsTable };
  document.addEventListener('DOMContentLoaded', seedNotifications);
})();
