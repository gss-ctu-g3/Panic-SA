(function () {
  const NAV_ITEMS = [
    { href: 'index.html', label: 'SOS', page: 'index' },
    { href: 'contacts.html', label: 'Contacts', page: 'contacts' },
    { href: 'history.html', label: 'History', page: 'history' },
    { href: 'admin.html', label: 'Admin', page: 'admin', adminOnly: true },
    { action: 'logout', label: 'Logout' },
  ];

  function getCurrentPage() {
    const path = window.location.pathname.split('/').pop() || 'index.html';
    if (path === '' || path === '/') return 'index';
    return path.replace('.html', '');
  }

  function buildNav() {
    const currentPage = getCurrentPage();
    const nav = document.createElement('nav');
    nav.className = 'radial-nav';
    nav.setAttribute('aria-label', 'Primary');

    const backdrop = document.createElement('button');
    backdrop.className = 'radial-nav__backdrop';
    backdrop.setAttribute('aria-label', 'Close menu');
    backdrop.type = 'button';

    const toggle = document.createElement('button');
    toggle.className = 'radial-nav__toggle';
    toggle.id = 'radial-nav-toggle';
    toggle.type = 'button';
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-controls', 'radial-nav-orbit');
    toggle.setAttribute('aria-label', 'Open navigation menu');
    toggle.textContent = 'Menu';

    const orbit = document.createElement('div');
    orbit.className = 'radial-nav__orbit';
    orbit.id = 'radial-nav-orbit';

    function closeMenu() {
      toggle.setAttribute('aria-expanded', 'false');
      toggle.setAttribute('aria-label', 'Open navigation menu');
      orbit.classList.remove('is-open');
      backdrop.classList.remove('is-open');
    }

    function openMenu() {
      toggle.setAttribute('aria-expanded', 'true');
      toggle.setAttribute('aria-label', 'Close navigation menu');
      orbit.classList.add('is-open');
      backdrop.classList.add('is-open');
    }

    NAV_ITEMS.forEach(function (item) {
      if (item.adminOnly && !(window.PanicAuth && window.PanicAuth.isAdmin())) {
        return;
      }

      if (item.action === 'logout') {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'radial-nav__link radial-nav__link--logout';
        button.textContent = item.label;
        button.setAttribute('aria-label', item.label);
        button.addEventListener('click', function () {
          closeMenu();
          if (window.PanicAuth && window.PanicAuth.logout) {
            window.PanicAuth.logout();
          }
        });
        orbit.appendChild(button);
        return;
      }

      const link = document.createElement('a');
      link.href = item.href;
      link.className = 'radial-nav__link';
      link.textContent = item.label;
      link.setAttribute('aria-label', item.label);
      if (item.page === currentPage) {
        link.classList.add('is-active');
        link.setAttribute('aria-current', 'page');
      }
      orbit.appendChild(link);
    });

    nav.appendChild(backdrop);
    nav.appendChild(toggle);
    nav.appendChild(orbit);
    document.body.appendChild(nav);

    function toggleMenu() {
      const isOpen = toggle.getAttribute('aria-expanded') === 'true';
      if (isOpen) {
        closeMenu();
      } else {
        openMenu();
      }
    }

    toggle.addEventListener('click', toggleMenu);
    backdrop.addEventListener('click', closeMenu);

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeMenu();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', buildNav);
  } else {
    buildNav();
  }
})();
