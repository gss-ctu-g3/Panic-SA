//use same-origin when served through nginx on port 80
//fall back to localhost api when frontend is opened from another dev server
const API_BASE_URL =
  window.location.port === '' || window.location.port === '80'
    ? ''
    : 'http://localhost';

function formatApiError(data, status) {
  if (data?.message && typeof data.message === 'string') {
    return data.message;
  }

  const detail = data?.detail;

  if (typeof detail === 'string') {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail.map(function (item) {
      return item.msg || String(item);
    }).join(' ');
  }

  return `Request failed (${status})`;
}

function getAuthHeaders() {
  const headers = {
    'Content-Type': 'application/json',
  };

  const session = window.PanicAuth?.getSession?.();
  if (session?.token) {
    headers.Authorization = `Bearer ${session.token}`;
  }

  return headers;
}

async function apiRequest(method, path, body) {
  const options = {
    method,
    headers: getAuthHeaders(),
  };

  if (body !== undefined) {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, options);

  let data = null;
  try {
    data = await response.json();
  } catch (e) {
    data = null;
  }

  if (!response.ok) {
    throw new Error(formatApiError(data, response.status));
  }

  if (data?.status === 'failed') {
    throw new Error(data.message || 'Request failed.');
  }

  return data;
}

async function apiPost(path, body) {
  return apiRequest('POST', path, body);
}

async function apiGet(path) {
  return apiRequest('GET', path);
}

async function apiPut(path, body) {
  return apiRequest('PUT', path, body);
}

async function apiDelete(path) {
  return apiRequest('DELETE', path);
}

async function apiPatch(path, body) {
  return apiRequest('PATCH', path, body);
}

window.PanicApi = {
  API_BASE_URL,
  getAuthHeaders,
  apiPost,
  apiGet,
  apiPut,
  apiDelete,
  apiPatch,
};
