// Users data store and seeding
(function(){
  const { readJson, writeJson, generateId } = window.AniP;

  function seedUsers() {
    const existing = readJson('users', null);
    if (existing) return;
    const users = [
      { id: generateId('usr'), name: 'Juan Dela Cruz', email: 'juan@example.com', password: 'password', role: 'farmer' },
      { id: generateId('usr'), name: 'Maria Santos', email: 'maria@example.com', password: 'password', role: 'buyer' },
      { id: generateId('usr'), name: 'Admin User', email: 'admin@example.com', password: 'password', role: 'admin' }
    ];
    writeJson('users', users);
  }

  function getUsers(){ return readJson('users', []); }
  function findUserByEmail(email){ return getUsers().find(u => u.email.toLowerCase() === String(email).toLowerCase()); }
  function addUser({ name, email, password, role }){
    const users = getUsers();
    if (users.some(u => u.email.toLowerCase() === email.toLowerCase())) {
      throw new Error('Email already registered');
    }
    const user = { id: generateId('usr'), name, email, password, role };
    users.push(user);
    writeJson('users', users);
    return user;
  }

  window.UsersStore = { seedUsers, getUsers, findUserByEmail, addUser };

  document.addEventListener('DOMContentLoaded', seedUsers);
})();
