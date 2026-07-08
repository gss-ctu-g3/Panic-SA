(function () {
  const addButton = document.getElementById('add-button');
  const addContactForm = document.getElementById('add-contact');
  const contactsBody = document.getElementById('contacts-body');
  const alertBox = document.getElementById('alert');
  const loader = document.querySelector('.loader');
  const contactIdInput = document.getElementById('contact-id');
  const nameInput = document.getElementById('name');
  const phoneInput = document.getElementById('phonenumber');
  const emailInput = document.getElementById('email');
  const relationshipInput = document.getElementById('relationship');

  if (!addContactForm || !contactsBody) return;

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

  function normalizePhone(value) {
    const cleaned = value.trim().replace(/[\s\-()]/g, '');

    if (/^0\d{9}$/.test(cleaned)) {
      return '+27' + cleaned.slice(1);
    }

    if (/^27\d{9}$/.test(cleaned)) {
      return '+' + cleaned;
    }

    if (/^\+27\d{9}$/.test(cleaned)) {
      return cleaned;
    }

    throw new Error(
      'Invalid phone number. Use a 10-digit SA number starting with 0, or +27 international format.'
    );
  }

  function formatPhoneForDisplay(value) {
    if (typeof value === 'string' && value.startsWith('+27') && value.length === 12) {
      return '0' + value.slice(3);
    }
    return value;
  }

  function resetForm() {
    contactIdInput.value = '';
    addContactForm.reset();
    addContactForm.classList.remove('show-form');
  }

  function getFormPayload() {
    const name = nameInput.value.trim();
    const email = emailInput.value.trim();
    const relationship = relationshipInput.value.trim();
    const phone = normalizePhone(phoneInput.value);

    if (!name || !email || !relationship) {
      throw new Error('Please fill in all contact fields.');
    }

    return {
      name,
      phone,
      email_address: email,
      relationship,
    };
  }

  function renderContacts(contacts) {
    contactsBody.innerHTML = '';

    if (!contacts.length) {
      const emptyRow = document.createElement('tr');
      emptyRow.className = 'empty-row';
      emptyRow.innerHTML = '<td colspan="5">No emergency contacts yet.</td>';
      contactsBody.appendChild(emptyRow);
      return;
    }

    contacts.forEach(function (contact) {
      const row = document.createElement('tr');

      row.innerHTML =
        '<td></td>' +
        '<td></td>' +
        '<td></td>' +
        '<td></td>' +
        '<td>' +
        '<button type="button" class="edit-button" data-id="' + contact.id + '">Edit Contact</button> ' +
        '<button type="button" class="Delete-button" data-id="' + contact.id + '">Delete Contact</button>' +
        '</td>';

      const cells = row.querySelectorAll('td');
      cells[0].setAttribute('data-label', 'Name');
      cells[1].setAttribute('data-label', 'Phone');
      cells[2].setAttribute('data-label', 'Email');
      cells[3].setAttribute('data-label', 'Relationship');
      cells[4].setAttribute('data-label', 'Actions');
      cells[0].textContent = contact.name;
      cells[1].textContent = formatPhoneForDisplay(contact.phone);
      cells[2].textContent = contact.email_address;
      cells[3].textContent = contact.relationship;

      contactsBody.appendChild(row);
    });
  }

  async function loadContacts() {
    hideAlert();
    setLoading(true);

    try {
      const data = await window.PanicApi.apiGet('/contacts/user/' + session.userId);
      renderContacts(data.contacts || []);
    } catch (err) {
      showAlert(err.message || 'Could not load contacts.');
    } finally {
      setLoading(false);
    }
  }

  function fillFormForEdit(contact) {
    contactIdInput.value = contact.id;
    nameInput.value = contact.name;
    phoneInput.value = formatPhoneForDisplay(contact.phone);
    emailInput.value = contact.email_address;
    relationshipInput.value = contact.relationship;
    addContactForm.classList.add('show-form');
    hideAlert();
  }

  if (addButton) {
    addButton.addEventListener('click', function () {
      hideAlert();
      if (addContactForm.classList.contains('show-form') && !contactIdInput.value) {
        addContactForm.classList.remove('show-form');
        return;
      }

      contactIdInput.value = '';
      addContactForm.reset();
      addContactForm.classList.toggle('show-form');
    });
  }

  addContactForm.addEventListener('submit', async function (e) {
    e.preventDefault();
    hideAlert();

    let payload;
    try {
      payload = getFormPayload();
    } catch (err) {
      showAlert(err.message);
      return;
    }

    const contactId = contactIdInput.value.trim();
    setLoading(true);

    try {
      if (contactId) {
        await window.PanicApi.apiPut('/contacts/' + contactId, payload);
      } else {
        await window.PanicApi.apiPost('/contacts', payload);
      }

      resetForm();
      await loadContacts();
    } catch (err) {
      showAlert(err.message || 'Could not save contact.');
    } finally {
      setLoading(false);
    }
  });

  contactsBody.addEventListener('click', async function (e) {
    const editButton = e.target.closest('.edit-button');
    const deleteButton = e.target.closest('.Delete-button');

    if (editButton) {
      hideAlert();
      setLoading(true);

      try {
        const data = await window.PanicApi.apiGet('/contacts/' + editButton.dataset.id);
        fillFormForEdit(data.contact);
      } catch (err) {
        showAlert(err.message || 'Could not load contact.');
      } finally {
        setLoading(false);
      }
      return;
    }

    if (deleteButton) {
      const contactId = deleteButton.dataset.id;
      const confirmed = window.confirm('Delete this emergency contact?');
      if (!confirmed) return;

      hideAlert();
      setLoading(true);

      try {
        await window.PanicApi.apiDelete('/contacts/' + contactId);
        await loadContacts();
      } catch (err) {
        showAlert(err.message || 'Could not delete contact.');
      } finally {
        setLoading(false);
      }
    }
  });

  loadContacts();
})();
