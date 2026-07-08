(function () {
  const alertsBody = document.getElementById('admin-alerts-body');
  const alertBox = document.getElementById('alert');
  const loader = document.querySelector('.loader');
  const statusFilter = document.getElementById('status-filter');
  const totalAlertsEl = document.querySelector('.total-alerts');
  const todayAlertsEl = document.querySelector('.today-alerts');
  const activeAlertsEl = document.querySelector('.active-alerts');

  if (!alertsBody) return;

  const REFRESH_INTERVAL_MS = 60 * 1000;
  let isInitialLoad = true;

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

  function formatTimestamp(isoString) {
    return formatTime(isoString) + '  ' + formatDate(isoString);
  }

  function getStatusFilter() {
    if (!statusFilter) return 'all';
    return statusFilter.value || 'all';
  }

  function buildAlertsPath() {
    const status = getStatusFilter();
    if (status === 'all') {
      return '/admin/alerts';
    }
    return '/admin/alerts?status=' + encodeURIComponent(status);
  }

  function renderAlerts(alerts) {
    alertsBody.innerHTML = '';

    if (!alerts.length) {
      const emptyRow = document.createElement('tr');
      emptyRow.innerHTML = '<td colspan="7">No alerts found.</td>';
      alertsBody.appendChild(emptyRow);
      return;
    }

    alerts.forEach(function (alert) {
      const row = document.createElement('tr');

      row.innerHTML =
        '<td></td>' +
        '<td></td>' +
        '<td></td>' +
        '<td></td>' +
        '<td></td>' +
        '<td></td>' +
        '<td></td>';

      const cells = row.querySelectorAll('td');
      cells[0].setAttribute('data-label', 'Alert ID');
      cells[1].setAttribute('data-label', 'User ID');
      cells[2].setAttribute('data-label', 'Latitude');
      cells[3].setAttribute('data-label', 'Longitude');
      cells[4].setAttribute('data-label', 'Status');
      cells[5].setAttribute('data-label', 'Timestamp');
      cells[6].setAttribute('data-label', 'Map');
      cells[0].textContent = alert.alert_id;
      cells[1].textContent = alert.linked_user_id;
      cells[2].textContent = alert.latitude;
      cells[3].textContent = alert.longitude;
      cells[4].textContent = alert.status;
      cells[5].textContent = formatTimestamp(alert.created_at);

      const mapUrl =
        alert.location_link ||
        'https://www.google.com/maps?q=' + alert.latitude + ',' + alert.longitude;
      const mapLink = document.createElement('a');
      mapLink.href = mapUrl;
      mapLink.target = '_blank';
      mapLink.rel = 'noopener noreferrer';
      mapLink.textContent = 'Open Map';
      cells[6].appendChild(mapLink);

      alertsBody.appendChild(row);
    });
  }

  function renderStats(stats) {
    if (totalAlertsEl) {
      totalAlertsEl.textContent = stats.total_alerts ?? 0;
    }
    if (todayAlertsEl) {
      todayAlertsEl.textContent = stats.today_alerts ?? 0;
    }
    if (activeAlertsEl) {
      activeAlertsEl.textContent = stats.active_alerts ?? 0;
    }
  }

  async function loadDashboard() {
    hideAlert();

    if (isInitialLoad) {
      setLoading(true);
    }

    try {
      const [statsData, alertsData] = await Promise.all([
        window.PanicApi.apiGet('/admin/stats'),
        window.PanicApi.apiGet(buildAlertsPath()),
      ]);

      renderStats(statsData.stats || {});
      renderAlerts(alertsData.alerts || []);
    } catch (err) {
      showAlert(err.message || 'Could not load admin dashboard.');
    } finally {
      if (isInitialLoad) {
        setLoading(false);
        isInitialLoad = false;
      }
    }
  }

  if (statusFilter) {
    statusFilter.addEventListener('change', function () {
      loadDashboard();
    });
  }

  loadDashboard();
  setInterval(loadDashboard, REFRESH_INTERVAL_MS);
})();
