(function () {
  const form = document.getElementById('loginForm');
  const alertBox = document.getElementById('alert');

  if (!form) return;

  //if already logged in just go to the app
  if (window.PanicAuth?.isLoggedIn()) {
    window.location.href = 'index.html';
    return;
  }

  function showError(message) {
    alertBox.textContent = message;
    alertBox.style.display = 'block';
  }

  form.addEventListener('submit', async function (e) {
    e.preventDefault();

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;

    alertBox.style.display = 'none';

    try {
      const data = await window.PanicApi.apiPost('/auth/login', {
        username,
        password,
      });

      window.PanicAuth.saveSession(data);
      window.location.href = 'index.html';
    } catch (err) {
      showError(err.message || 'Login failed. Please try again.');
    }
  });
})();
