(function () {
  const API_BASE_URL = window.PanicApi?.API_BASE_URL ?? '';

  const POLL_INTERVAL_MS = 5 * 60 * 1000;

  const cardEl = document.getElementById('live-alert-card');
  const titleEl = document.getElementById('live-alert-title');
  const subtitleEl = document.getElementById('live-alert-subtitle');
  const nameEl = document.getElementById('live-alert-name');
  const statusEl = document.getElementById('live-alert-status');
  const updatedEl = document.getElementById('live-alert-updated');
  const mapFrameEl = document.getElementById('live-alert-map');
  const mapLinkEl = document.getElementById('live-alert-link');
  const mapPlaceholderEl = document.getElementById('live-alert-map-placeholder');
  const messageEl = document.getElementById('live-alert-message');
  const loader = document.querySelector('.loader');

  let pollIntervalId = null;
  let currentAlertId = '';
  let cachedUserName = '';

  // track last coords so the map iframe only reloads when location moves
  let lastLatitude = null;
  let lastLongitude = null;

  function getAlertIdFromPath() {
    const parts = window.location.pathname.split('/').filter(Boolean);
    return parts.length >= 3 ? parts[2] : '';
  }

  function setLoading(isLoading) {
    if (loader) {
      loader.classList.toggle('active', isLoading);
    }
  }

  function setStatusBadge(status, type) {
    if (!statusEl) return;
    statusEl.textContent = status;
    statusEl.className = 'live-alert-status-badge' + (type ? ' ' + type : '');
  }

  function setActiveCardState() {
    if (cardEl) {
      cardEl.classList.remove('is-ended');
    }
    if (titleEl) {
      titleEl.classList.add('is-active');
    }
    if (subtitleEl) {
      subtitleEl.classList.add('is-active');
    }
  }

  function setEndedCardState() {
    if (cardEl) {
      cardEl.classList.add('is-ended');
    }
    if (titleEl) {
      titleEl.classList.remove('is-active');
    }
    if (subtitleEl) {
      subtitleEl.classList.remove('is-active');
    }
  }

  function showMessage(message, type) {
    if (!messageEl) return;
    messageEl.textContent = message;
    messageEl.className = 'live-alert-message' + (type ? ' ' + type : '');
    messageEl.style.display = 'block';
  }

  function hideMessage() {
    if (!messageEl) return;
    messageEl.style.display = 'none';
    messageEl.textContent = '';
    messageEl.className = 'live-alert-message';
  }

  function formatDateTime(value) {
    if (!value) return 'Unknown';
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    return date.toLocaleString();
  }

  function stopPolling() {
    if (pollIntervalId !== null) {
      clearInterval(pollIntervalId);
      pollIntervalId = null;
    }
  }

  function buildMapEmbedUrl(latitude, longitude) {
    return (
      'https://maps.google.com/maps?q=' +
      latitude +
      ',' +
      longitude +
      '&z=15&output=embed'
    );
  }

  function hasValidCoords(alert) {
    return (
      alert.latitude != null &&
      alert.longitude != null &&
      !Number.isNaN(Number(alert.latitude)) &&
      !Number.isNaN(Number(alert.longitude))
    );
  }

  function hideMapElements() {
    if (mapFrameEl) {
      mapFrameEl.style.display = 'none';
    }
    if (mapLinkEl) {
      mapLinkEl.style.display = 'none';
    }
    if (mapPlaceholderEl) {
      mapPlaceholderEl.style.display = 'none';
    }
  }

  function updateMap(alert) {
    if (!hasValidCoords(alert)) {
      hideMapElements();
      if (mapPlaceholderEl) {
        mapPlaceholderEl.style.display = 'block';
      }
      return;
    }

    if (mapPlaceholderEl) {
      mapPlaceholderEl.style.display = 'none';
    }

    if (mapLinkEl && alert.location_link) {
      mapLinkEl.href = alert.location_link;
      mapLinkEl.textContent = 'Open in Google Maps';
      mapLinkEl.style.display = 'block';
    }

    if (mapFrameEl) {
      mapFrameEl.style.display = 'block';

      if (alert.latitude !== lastLatitude || alert.longitude !== lastLongitude) {
        mapFrameEl.src = buildMapEmbedUrl(alert.latitude, alert.longitude);
        lastLatitude = alert.latitude;
        lastLongitude = alert.longitude;
      }
    }
  }

  function renderAlert(alert) {
    setActiveCardState();

    if (nameEl) {
      const name = alert.user_full_name || 'Panic SA User';
      cachedUserName = name;
      nameEl.textContent = name;
    }

    setStatusBadge(alert.status || 'unknown', 'is-active');

    if (updatedEl) {
      updatedEl.textContent = formatDateTime(alert.updated_at);
    }

    updateMap(alert);

    if (subtitleEl) {
      subtitleEl.textContent = 'Live location updates every 5 minutes while the alert is active.';
    }
  }

  function renderEndedState() {
    setEndedCardState();

    if (titleEl) {
      titleEl.textContent = 'Alert Ended';
    }

    if (subtitleEl) {
      subtitleEl.textContent = 'This emergency alert is no longer active.';
    }

    if (nameEl) {
      nameEl.textContent = cachedUserName || 'Unknown';
    }

    setStatusBadge('cancelled', 'is-ended');

    if (updatedEl) {
      updatedEl.textContent = '—';
    }

    hideMapElements();
    setLoading(false);
    showMessage('The person who triggered this alert has cancelled the SOS.', 'ended');
    stopPolling();
  }

  async function loadAlert(alertId) {
    const response = await fetch(API_BASE_URL + '/alerts/' + alertId, {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    let data = null;
    try {
      data = await response.json();
    } catch (e) {
      data = null;
    }

    if (response.status === 410) {
      renderEndedState();
      return null;
    }

    if (!response.ok) {
      const message =
        data?.detail ||
        data?.message ||
        'Could not load this alert.';
      throw new Error(message);
    }

    if (data?.status === 'failed') {
      throw new Error(data.message || 'Could not load this alert.');
    }

    return data.alert;
  }

  async function refreshAlert(alertId) {
    try {
      const alert = await loadAlert(alertId);
      if (!alert) return;

      if (alert.status === 'cancelled') {
        renderEndedState();
        return;
      }

      hideMessage();
      renderAlert(alert);
    } catch (err) {
      showMessage(err.message || 'Could not refresh alert.', 'error');
    }
  }

  async function init() {
    const alertId = getAlertIdFromPath();

    if (!alertId) {
      showMessage('Invalid alert link.', 'error');
      return;
    }

    currentAlertId = alertId;

    setLoading(true);

    try {
      const alert = await loadAlert(alertId);
      if (!alert) return;

      renderAlert(alert);

      pollIntervalId = setInterval(function () {
        refreshAlert(alertId);
      }, POLL_INTERVAL_MS);
    } catch (err) {
      showMessage(err.message || 'Could not load this alert.', 'error');
    } finally {
      setLoading(false);
    }

    // refresh immediately when the user returns to this tab
    document.addEventListener('visibilitychange', function () {
      if (document.visibilityState === 'visible' && currentAlertId && pollIntervalId !== null) {
        refreshAlert(currentAlertId);
      }
    });
  }

  init();
})();
