// Shared client-side app utilities for authentication and session management
(function(window){
  const STORAGE_USERS_KEY = 'appUsers';
  const STORAGE_SESSION_KEY = 'appSession';

  // Initialize demo users if not present
  function initUsers(){
    const raw = localStorage.getItem(STORAGE_USERS_KEY);
    if (raw) return;
    const demo = {
      'admin@example.com': { password: 'admin123', role: 'admin', name: 'Administrator' },
      'user@example.com': { password: 'user123', role: 'user', name: 'Normal User' }
    };
    localStorage.setItem(STORAGE_USERS_KEY, JSON.stringify(demo));
  }

  function getUsers(){
    initUsers();
    return JSON.parse(localStorage.getItem(STORAGE_USERS_KEY) || '{}');
  }

  function login(email, password){
    const users = getUsers();
    const u = users[email];
    if (!u) return { ok: false, message: 'User not found' };
    if (u.password !== password) return { ok: false, message: 'Invalid password' };
    const session = { email: email, role: u.role, name: u.name, loggedAt: new Date().toISOString() };
    localStorage.setItem(STORAGE_SESSION_KEY, JSON.stringify(session));
    return { ok: true, session };
  }

  function logout(){
    localStorage.removeItem(STORAGE_SESSION_KEY);
  }

  function getSession(){
    const raw = localStorage.getItem(STORAGE_SESSION_KEY);
    return raw ? JSON.parse(raw) : null;
  }

  function isAdmin(){
    const s = getSession();
    return s && s.role === 'admin';
  }

  // User management functions for admin
  function addUser(email, password, role = 'user', name = ''){
    if (!email) return { ok: false, message: 'Email required' };
    if (!password || password.length < 3) return { ok: false, message: 'Password must be at least 3 chars' };
    if (role !== 'admin' && role !== 'user') return { ok: false, message: 'Invalid role' };

    const users = getUsers();
    if (users[email]) return { ok: false, message: 'User already exists' };

    users[email] = { password, role, name: name || email.split('@')[0] };
    localStorage.setItem(STORAGE_USERS_KEY, JSON.stringify(users));
    return { ok: true };
  }

  function updateUser(email, changes = {}){
    const users = getUsers();
    const u = users[email];
    if (!u) return { ok: false, message: 'User not found' };
    if (changes.password) {
      if (changes.password.length < 3) return { ok: false, message: 'Password must be at least 3 chars' };
      u.password = changes.password;
    }
    if (changes.role) {
      if (changes.role !== 'admin' && changes.role !== 'user') return { ok: false, message: 'Invalid role' };
      u.role = changes.role;
    }
    if (typeof changes.name === 'string') u.name = changes.name;

    users[email] = u;
    localStorage.setItem(STORAGE_USERS_KEY, JSON.stringify(users));
    return { ok: true };
  }

  function deleteUser(email){
    const users = getUsers();
    if (!users[email]) return { ok: false, message: 'User not found' };
    delete users[email];
    localStorage.setItem(STORAGE_USERS_KEY, JSON.stringify(users));
    // If deleting current session user, also logout
    const session = getSession();
    if (session && session.email === email) logout();
    return { ok: true };
  }

  // If not logged in, redirect to login page. If logged in, returns session.
  function requireAuth(redirectTo = 'ui/login.html'){
    const s = getSession();
    if (!s) {
      // Use relative navigation; allow files opened locally
      window.location.href = redirectTo;
      return null;
    }
    return s;
  }

  // Expose on window
  window.app = window.app || {};
  Object.assign(window.app, {
    login, logout, getSession, isAdmin, requireAuth, getUsers,
    addUser, updateUser, deleteUser
  });

})(window);
