(function () {
  const panicButton = document.getElementById('panic-button');
  const cancelButton = document.getElementById('cancel-button');
  const alertBox = document.getElementById('alert');
  const statusBox = document.getElementById('panic-status');
  const loader = document.querySelector('.loader');
  const cancelModal = document.getElementById('cancel-modal');
  const cancelReasonSelect = document.getElementById('cancel-reason');
  const cancelReasonDetail = document.getElementById('cancel-reason-detail');
  const cancelDetailLabel = document.getElementById('cancel-detail-label');
  const cancelModalError = document.getElementById('cancel-modal-error');
  const cancelConfirmButton = document.getElementById('cancel-confirm-button');
  const cancelDismissButton = document.getElementById('cancel-dismiss-button');

  if (!panicButton || !window.PanicApi) return;

  const ACTIVE_ALERT_KEY = 'panicsa_active_alert_id';
  const LOCATION_INTERVAL_MS = 5 * 60 * 1000;
  let locationIntervalId = null;

  function showAlert(message, type) {
    if (!alertBox) return;
    alertBox.textContent = message;
    alertBox.className = 'panic-alert' + (type ? ' ' + type : '');
    alertBox.style.display = 'block';
  }

  function hideAlert() {
    if (!alertBox) return;
    alertBox.style.display = 'none';
    alertBox.textContent = '';
    alertBox.className = 'panic-alert';
  }

  function setStatus(message) {
    if (!statusBox) return;
    statusBox.textContent = message || '';
  }

  function setLoading(isLoading) {
    if (loader) {
      loader.classList.toggle('active', isLoading);
    }
    panicButton.disabled = isLoading;
    if (cancelButton) {
      cancelButton.disabled = isLoading;
    }
  }

  function showCancelMode(alertId) {
    panicButton.style.display = 'none';
    if (cancelButton) {
      cancelButton.style.display = 'inline-block';
    }
    setStatus('Active alert ' + alertId + '. Location updates every 5 minutes.');
  }

  function showPanicMode() {
    panicButton.style.display = 'inline-block';
    if (cancelButton) {
      cancelButton.style.display = 'none';
    }
    setStatus('');
  }

  function clearLocationInterval() {
    if (locationIntervalId !== null) {
      clearInterval(locationIntervalId);
      locationIntervalId = null;
    }
  }

  function storeActiveAlertId(alertId) {
    sessionStorage.setItem(ACTIVE_ALERT_KEY, alertId);
  }

  function getStoredAlertId() {
    return sessionStorage.getItem(ACTIVE_ALERT_KEY);
  }

  function clearStoredAlertId() {
    sessionStorage.removeItem(ACTIVE_ALERT_KEY);
  }

  function getCurrentPosition() {
    return new Promise(function (resolve, reject) {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation is not supported on this device.'));
        return;
      }

      navigator.geolocation.getCurrentPosition(resolve, reject, {
        enableHighAccuracy: true,
        timeout: 15000,
        maximumAge: 0,
      });
    });
  }

  function getPositionErrorMessage(error) {
    if (!error) {
      return 'Could not read your location.';
    }

    if (error.code === 1) {
      return 'Location permission denied. Enable GPS to send an SOS alert.';
    }

    if (error.code === 2) {
      return 'Location unavailable. Try again in a moment.';
    }

    if (error.code === 3) {
      return 'Location request timed out. Try again.';
    }

    return error.message || 'Could not read your location.';
  }

  function isActiveAlertConflict(message) {
    return typeof message === 'string' &&
      message.toLowerCase().indexOf('already have an active alert') !== -1;
  }

  function showCancelModalError(message) {
    if (!cancelModalError) return;
    cancelModalError.textContent = message;
    cancelModalError.style.display = message ? 'block' : 'none';
  }

  function isCancelFormValid() {
    const reason = cancelReasonSelect?.value || '';
    if (!reason) {
      return false;
    }

    if (reason === 'Other') {
      return (cancelReasonDetail?.value.trim().length || 0) >= 5;
    }

    return true;
  }

  function updateCancelConfirmState() {
    if (!cancelConfirmButton) return;
    cancelConfirmButton.disabled = !isCancelFormValid();
  }

  function toggleOtherDetailField() {
    const isOther = cancelReasonSelect?.value === 'Other';

    if (cancelReasonDetail) {
      cancelReasonDetail.style.display = isOther ? 'block' : 'none';
      if (!isOther) {
        cancelReasonDetail.value = '';
      }
    }

    if (cancelDetailLabel) {
      cancelDetailLabel.style.display = isOther ? 'block' : 'none';
    }

    updateCancelConfirmState();
  }

  function resetCancelModalForm() {
    if (cancelReasonSelect) {
      cancelReasonSelect.value = '';
    }
    if (cancelReasonDetail) {
      cancelReasonDetail.value = '';
    }
    showCancelModalError('');
    toggleOtherDetailField();
  }

  function openCancelModal() {
    if (!cancelModal) return;
    resetCancelModalForm();
    cancelModal.style.display = 'flex';
    cancelModal.setAttribute('aria-hidden', 'false');
  }

  function closeCancelModal() {
    if (!cancelModal) return;
    cancelModal.style.display = 'none';
    cancelModal.setAttribute('aria-hidden', 'true');
    showCancelModalError('');
  }

  async function updateAlertLocation(alertId) {
    const position = await getCurrentPosition();
    const latitude = position.coords.latitude;
    const longitude = position.coords.longitude;

    await window.PanicApi.apiPatch('/alerts/' + alertId + '/location', {
      latitude: latitude,
      longitude: longitude,
    });
  }

  function startLocationUpdates(alertId) {
    clearLocationInterval();
    locationIntervalId = setInterval(function () {
      updateAlertLocation(alertId).catch(function (err) {
        showAlert(err.message || 'Could not refresh location.', 'error');
      });
    }, LOCATION_INTERVAL_MS);
  }

  async function resumeActiveAlert(showMessage) {
    try {
      const data = await window.PanicApi.apiGet('/alerts/active/me');
      const alert = data.alert;

      if (!alert?.alert_id) {
        clearStoredAlertId();
        showPanicMode();
        return null;
      }

      storeActiveAlertId(alert.alert_id);
      showCancelMode(alert.alert_id);
      startLocationUpdates(alert.alert_id);

      if (showMessage) {
        showAlert(
          'You already have an active SOS alert. Tap Cancel SOS when you are safe.',
          'success'
        );
      }

      return alert.alert_id;
    } catch (err) {
      clearStoredAlertId();
      showPanicMode();
      return null;
    }
  }

  async function triggerPanic() {
    hideAlert();
    setLoading(true);

    try {
      const position = await getCurrentPosition();
      const latitude = position.coords.latitude;
      const longitude = position.coords.longitude;

      const data = await window.PanicApi.apiPost('/alerts/panic', {
        latitude: latitude,
        longitude: longitude,
      });

      const alertId = data.alert?.alert_id;
      if (!alertId) {
        throw new Error('Alert was created but no alert id was returned.');
      }

      storeActiveAlertId(alertId);
      showCancelMode(alertId);
      startLocationUpdates(alertId);
      showAlert('Help is on the way. Your emergency contacts have been notified.', 'success');
    } catch (err) {
      if (isActiveAlertConflict(err.message)) {
        await resumeActiveAlert(true);
        return;
      }

      const message =
        err && err.code !== undefined
          ? getPositionErrorMessage(err)
          : (err.message || 'Could not send SOS alert.');
      showAlert(message, 'error');
    } finally {
      setLoading(false);
    }
  }

  async function cancelPanic() {
    const reason = cancelReasonSelect?.value || '';

    if (!isCancelFormValid()) {
      showCancelModalError('Please select a cancel reason before confirming.');
      return;
    }

    hideAlert();
    showCancelModalError('');
    setLoading(true);

    if (cancelConfirmButton) {
      cancelConfirmButton.disabled = true;
    }

    let alertId = getStoredAlertId();

    try {
      if (!alertId) {
        const data = await window.PanicApi.apiGet('/alerts/active/me');
        alertId = data.alert?.alert_id || null;
      }

      if (!alertId) {
        closeCancelModal();
        showPanicMode();
        return;
      }

      const payload = {
        cancel_reason: reason,
      };

      if (reason === 'Other') {
        payload.cancel_reason_detail = cancelReasonDetail.value.trim();
      }

      await window.PanicApi.apiPost('/alerts/' + alertId + '/cancel', payload);

      closeCancelModal();
      clearLocationInterval();
      clearStoredAlertId();
      showPanicMode();
      showAlert('SOS alert cancelled.', 'success');
    } catch (err) {
      showCancelModalError(err.message || 'Could not cancel SOS alert.');
    } finally {
      setLoading(false);
      updateCancelConfirmState();
    }
  }

  panicButton.addEventListener('click', triggerPanic);

  if (cancelButton) {
    cancelButton.addEventListener('click', openCancelModal);
  }

  if (cancelReasonSelect) {
    cancelReasonSelect.addEventListener('change', toggleOtherDetailField);
  }

  if (cancelReasonDetail) {
    cancelReasonDetail.addEventListener('input', updateCancelConfirmState);
  }

  if (cancelConfirmButton) {
    cancelConfirmButton.addEventListener('click', cancelPanic);
  }

  if (cancelDismissButton) {
    cancelDismissButton.addEventListener('click', closeCancelModal);
  }

  if (cancelModal) {
    cancelModal.addEventListener('click', function (event) {
      if (event.target === cancelModal) {
        closeCancelModal();
      }
    });
  }

  resumeActiveAlert(false);
})();
