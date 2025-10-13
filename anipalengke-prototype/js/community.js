// Community posts and comments
(function(){
  const { readJson, writeJson, generateId, getCurrentUser, formatDate } = window.AniP;
  const { notify } = window.Notifications;

  function seedPosts(){
    if (readJson('posts', null)) return;
    const posts = [
      { id: generateId('pst'), authorId: null, authorName: 'Agri Extension', role: 'admin', content: 'Welcome to AniPalengke! Share best practices and market insights here.', createdAt: Date.now()- 86400000, comments: [] }
    ];
    writeJson('posts', posts);
  }
  function getPosts(){ return readJson('posts', []); }
  function setPosts(list){ writeJson('posts', list); }

  function addPost({ content }){
    const user = getCurrentUser();
    const posts = getPosts();
    const post = { id: generateId('pst'), authorId: user.id, authorName: user.name, role: user.role, content, createdAt: Date.now(), comments: [] };
    posts.unshift(post);
    setPosts(posts);
    notify({ title: 'New community post', message: `${user.name}: ${content.slice(0,60)}${content.length>60?'…':''}`, type: 'info' });
    return post;
  }

  function addComment(postId, text){
    const user = getCurrentUser();
    const posts = getPosts();
    const idx = posts.findIndex(p => p.id === postId);
    if (idx === -1) return;
    const comment = { id: generateId('cmt'), authorId: user.id, authorName: user.name, role: user.role, text, createdAt: Date.now() };
    posts[idx].comments.push(comment);
    setPosts(posts);
    return comment;
  }

  function deletePost(postId){
    const user = getCurrentUser();
    if (user.role !== 'admin') return;
    const posts = getPosts().filter(p => p.id !== postId);
    setPosts(posts);
  }

  function renderFeed(targetSelector){
    const el = document.querySelector(targetSelector);
    if (!el) return;
    const posts = getPosts();
    el.innerHTML = posts.map(p => `
      <article class="post-card">
        <div class="card-content">
          <div class="card-title">${p.authorName} · <span class="tag">${p.role}</span></div>
          <div class="muted" style="font-size:12px;">${formatDate(p.createdAt)}</div>
          <p>${p.content}</p>
        </div>
        <div class="card-actions">
          ${window.AniP.getCurrentUser()?.role === 'admin' ? `<button class="btn btn-danger" data-delete="${p.id}">Delete</button>` : ''}
          <button class="btn btn-secondary" data-comment="${p.id}">Comment</button>
        </div>
        <div class="card-body">
          ${(p.comments||[]).map(c => `<div class="section"><strong>${c.authorName}</strong> <span class="muted">${formatDate(c.createdAt)}</span><div>${c.text}</div></div>`).join('') || '<div class="muted">No comments yet</div>'}
        </div>
      </article>
    `).join('');

    // attach events
    el.querySelectorAll('[data-delete]').forEach(btn => btn.addEventListener('click', () => {
      deletePost(btn.getAttribute('data-delete'));
      renderFeed(targetSelector);
    }));
    el.querySelectorAll('[data-comment]').forEach(btn => btn.addEventListener('click', () => {
      const postId = btn.getAttribute('data-comment');
      const div = document.createElement('div');
      div.innerHTML = `
        <form class="form" id="comment-form">
          <div class="form-row">
            <label class="label" for="comment">Your comment</label>
            <textarea class="textarea" id="comment" required></textarea>
          </div>
          <div class="modal-footer" style="padding:0; border-top:none;">
            <button class="btn btn-secondary" type="button" id="cancel">Cancel</button>
            <button class="btn btn-primary" type="submit">Post comment</button>
          </div>
        </form>`;
      window.AniP.openModal({ title: 'Add comment', content: div });
      div.querySelector('#cancel').addEventListener('click', window.AniP.closeModal);
      div.querySelector('#comment-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const text = div.querySelector('#comment').value.trim();
        if (!text) return;
        addComment(postId, text);
        window.AniP.closeModal();
        renderFeed(targetSelector);
      });
    }));
  }

  window.Community = { seedPosts, getPosts, addPost, addComment, deletePost, renderFeed };
  document.addEventListener('DOMContentLoaded', seedPosts);
})();
