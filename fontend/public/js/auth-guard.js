(function () {
  const currentPage = (window.location.pathname.split('/').pop() || 'index.html').replace('.html', '');

  if (currentPage === 'admin') {
    window.PanicAuth.requireAdmin();
  } else {
    window.PanicAuth.requireAuth();
  }
})();
