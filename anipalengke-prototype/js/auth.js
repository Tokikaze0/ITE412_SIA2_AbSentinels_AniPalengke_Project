// Authentication flows for login and register pages
(function(){
  const { setCurrentUser, showToast } = window.AniP;
  const { findUserByEmail, addUser } = window.UsersStore;

  function roleToDashboard(role){
    switch(role){
      case 'farmer': return 'farmer-dashboard.html';
      case 'buyer': return 'buyer-dashboard.html';
      case 'admin': return 'admin-dashboard.html';
      default: return 'index.html';
    }
  }

  function initLogin(){
    const form = document.getElementById('login-form');
    if (!form) return;
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const email = form.email.value.trim();
      const password = form.password.value;
      const user = findUserByEmail(email);
      if (!user || user.password !== password) {
        showToast({ title: 'Login failed', message: 'Invalid email or password', type: 'error' });
        return;
      }
      setCurrentUser({ id: user.id, name: user.name, role: user.role, email: user.email });
      showToast({ title: 'Welcome', message: `Logged in as ${user.role}` });
      location.href = roleToDashboard(user.role);
    });
  }

  function initRegister(){
    const form = document.getElementById('register-form');
    if (!form) return;
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const name = form.name.value.trim();
      const email = form.email.value.trim();
      const password = form.password.value;
      const role = form.role.value;
      try {
        const user = addUser({ name, email, password, role });
        setCurrentUser({ id: user.id, name: user.name, role: user.role, email: user.email });
        showToast({ title: 'Registration successful', message: `Welcome, ${user.name}` });
        location.href = roleToDashboard(user.role);
      } catch(err){
        showToast({ title: 'Registration failed', message: err.message || 'Please try again', type: 'error' });
      }
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    initLogin();
    initRegister();
  });
})();
