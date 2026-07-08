(function () {
  const historyBody = document.getElementById('history-body');
  const alertBox = document.getElementById('alert');
  const loader = document.querySelector('.loader');

  if (!historyBody) return;

  const session = window.PanicAuth?.getSession?.();
  if (!session?.userId) return;

  function showAlert(message) {
    if (!alertBox) return;
    alertBox.textContent = message;
    alertBox.style.display = 'block';
  }

  function hideAlert() {
    if (!alertBox) return;
    alertBox.style.display = 'none';
    alertBox.textContent = '';
  }

  function setLoading(isLoading) {
    if (!loader) return;
    loader.style.display = isLoading ? 'block' : 'none';
  }

  function formatDate(isoString) {
    const date = new Date(isoString);
    const year = date.getUTCFullYear();
    const month = String(date.getUTCMonth() + 1).padStart(2, '0');
    const day = String(date.getUTCDate()).padStart(2, '0');
    return year + '-' + month + '-' + day;
  }

  function formatTime(isoString) {
    const date = new Date(isoString);
    const hours = String(date.getUTCHours()).padStart(2, '0');
    const minutes = String(date.getUTCMinutes()).padStart(2, '0');
    return hours + ':' + minutes;
  }

  function renderAlerts(alerts) {
    historyBody.innerHTML = '';

    if (!alerts.length) {
      const emptyRow = document.createElement('tr');
      emptyRow.innerHTML = '<td colspan="5">No alert history yet.</td>';
      historyBody.appendChild(emptyRow);
      return;
    }

    alerts.forEach(function (alert) {
      const row = document.createElement('tr');

      row.innerHTML =
        '<td></td>' +
        '<td></td>' +
        '<td></td>' +
        '<td></td>' +
        '<td></td>';

      const cells = row.querySelectorAll('td');
      cells[0].setAttribute('data-label', 'Alert ID');
      cells[1].setAttribute('data-label', 'Date');
      cells[2].setAttribute('data-label', 'Time');
      cells[3].setAttribute('data-label', 'Status');
      cells[4].setAttribute('data-label', 'Reason');
      cells[0].textContent = alert.alert_id;
      cells[1].textContent = formatDate(alert.created_at);
      cells[2].textContent = formatTime(alert.created_at);
      cells[3].textContent = alert.status;
      cells[4].textContent = alert.cancel_reason || '-';

      historyBody.appendChild(row);
    });
  }

  async function loadAlerts() {
    hideAlert();
    setLoading(true);

    try {
      const data = await window.PanicApi.apiGet('/history/alerts/user/' + session.userId);
      renderAlerts(data.alerts || []);
    } catch (err) {
      showAlert(err.message || 'Could not load alert history.');
    } finally {
      setLoading(false);
    }
  }

  loadAlerts();
})();
