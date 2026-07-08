(function () {
  const STORAGE_KEY = 'panicsa_auth';
  const SESSION_MS = 7 * 24 * 60 * 60 * 1000;

  function saveSession(data) {
    const session = {
      token: data.token,
      userId: data.userId,
      username: data.username,
      tags: data.tags || [],
      expiresAt: Date.now() + SESSION_MS,
    };

    localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
    return session;
  }

  function getSession() {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;

    try {
      const session = JSON.parse(raw);
      if (!session?.token || !session?.expiresAt || Date.now() >= session.expiresAt) {
        localStorage.removeItem(STORAGE_KEY);
        return null;
      }
      return session;
    } catch (e) {
      localStorage.removeItem(STORAGE_KEY);
      return null;
    }
  }

  function isLoggedIn() {
    return getSession() !== null;
  }

  function isAdmin() {
    const session = getSession();
    return Array.isArray(session?.tags) && session.tags.includes('admin');
  }

  function logout() {
    localStorage.removeItem(STORAGE_KEY);
    window.location.href = 'login.html';
  }

  function requireAuth() {
    if (!isLoggedIn()) {
      window.location.href = 'login.html';
      return false;
    }
    return true;
  }

  function requireAdmin() {
    if (!requireAuth()) return false;
    if (!isAdmin()) {
      window.location.href = 'index.html';
      return false;
    }
    return true;
  }

  function applyAdminNav() {
    const adminLink = document.querySelector('.radial-nav__link[href="admin.html"]');
    if (adminLink && !isAdmin()) {
      adminLink.remove();
    }
  }

  window.PanicAuth = {
    saveSession,
    getSession,
    isLoggedIn,
    isAdmin,
    logout,
    requireAuth,
    requireAdmin,
    applyAdminNav,
  };
})();
