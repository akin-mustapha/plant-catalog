import { fetchNotification, createNotification, updateNotification, resendConfirmation } from "./api/notification.js";
import { escapeHtml, showNotification } from "./utils.js";

const MAX_CONTACTS = 3;

const ICONS = {
  back: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M19 12H5M11 6l-6 6 6 6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
  close: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>`,
  check: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M5 12.5l4.5 4.5L19 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
  bell: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M6 9a6 6 0 1 1 12 0c0 3.4 1 5.3 1.8 6.3.4.5 0 1.2-.6 1.2H4.8c-.6 0-1-.7-.6-1.2C5 14.3 6 12.4 6 9Z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/><path d="M10 20a2 2 0 0 0 4 0" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>`,
};

function formatNextRun(nextRunDate) {
  if (!nextRunDate) return "";
  const date = new Date(nextRunDate);
  if (Number.isNaN(date.getTime())) return "";
  const weekday = date.toLocaleDateString(undefined, { weekday: "short" });
  const time = date.toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" });
  return `${weekday} ${time}`;
}

function contactRowHtml(email = "", index) {
  const removable = index > 0;
  return `
    <div class="reminder-contact-row" data-contact-row>
      <input
        type="email"
        class="reminder-contact-input"
        name="contact"
        placeholder="you@example.com"
        value="${escapeHtml(email)}"
        ${index === 0 ? "required" : ""}
      />
      ${removable ? `<button type="button" class="reminder-contact-remove" data-remove-contact aria-label="Remove contact">${ICONS.close}</button>` : ""}
    </div>
  `;
}

function contactStatusHtml(contacts = []) {
  if (!contacts.length) return "";
  return contacts
    .map((contact) => {
      const confirmed = contact.status === "confirmed" || contact.status === "CONFIRMED";
      return `
        <div class="reminder-contact-status-row">
          <span class="reminder-contact-email">${escapeHtml(contact.email)}</span>
          <span class="reminder-contact-badge reminder-contact-badge--${confirmed ? "confirmed" : "pending"}">
            ${confirmed ? "confirmed" : "pending"}
          </span>
        </div>
      `;
    })
    .join("");
}

function renderModalShell() {
  const overlay = document.createElement("div");
  overlay.className = "modal-overlay reminder-modal-overlay";
  overlay.innerHTML = `<div class="reminder-modal" role="dialog" aria-modal="true" aria-labelledby="reminder-modal-title"></div>`;
  return overlay;
}

function renderFormView({ mode, notification }) {
  const isEdit = mode === "edit";
  const name = notification?.name || "";
  const description = notification?.description || "";
  const frequencyType = notification?.schedule ? "schedule" : notification?.interval ? "interval" : "schedule";
  const schedule = notification?.schedule || "";
  const intervalValue = notification?.interval?.value || notification?.interval_value || "";
  const intervalUnit = notification?.interval?.unit || notification?.interval_unit || "days";
  const contacts = notification?.contacts || [];
  const contactEmails = contacts.length ? contacts.map((c) => c.email) : [""];

  const statusBadge = isEdit
    ? `<div class="reminder-status-badge"><span class="reminder-status-dot"></span>Active${
        notification?.next_run_date ? ` &middot; next run ${escapeHtml(formatNextRun(notification.next_run_date))}` : ""
      }</div>`
    : "";

  return `
    <div class="reminder-modal-header">
      ${isEdit
        ? `<button type="button" class="reminder-icon-btn" data-close>${ICONS.close}</button>`
        : `<button type="button" class="reminder-icon-btn" data-close>${ICONS.back}</button>`}
      <h3 id="reminder-modal-title" class="reminder-modal-title">Reminder settings</h3>
      <span class="reminder-icon-btn-spacer"></span>
    </div>

    ${statusBadge}

    ${!isEdit ? `<p class="reminder-modal-intro">No reminders yet. Set one up and we'll nudge you (and anyone else you list) when your plants need attention.</p>` : ""}

    <form data-reminder-form>
      <div class="reminder-field">
        <label for="reminder-name">Name</label>
        <input type="text" id="reminder-name" name="name" placeholder="e.g. Weekly watering reminder" value="${escapeHtml(name)}" required />
      </div>

      <div class="reminder-field">
        <label for="reminder-description">Description</label>
        <textarea id="reminder-description" name="description" rows="3" placeholder="What should this reminder say?">${escapeHtml(description)}</textarea>
      </div>

      <div class="reminder-section">
        <div class="reminder-section-label">Frequency</div>

        <label class="reminder-radio-row">
          <input type="radio" name="frequency_type" value="schedule" ${frequencyType === "schedule" ? "checked" : ""} data-frequency-radio />
          <span class="reminder-radio-dot"></span>
          <span class="reminder-radio-label">Schedule</span>
        </label>
        <label class="reminder-radio-row">
          <input type="radio" name="frequency_type" value="interval" ${frequencyType === "interval" ? "checked" : ""} data-frequency-radio />
          <span class="reminder-radio-dot"></span>
          <span class="reminder-radio-label">Interval</span>
        </label>

        <div class="reminder-frequency-detail" data-frequency-detail="schedule" ${frequencyType !== "schedule" ? "hidden" : ""}>
          <div class="reminder-field">
            <label for="reminder-cron">Cron expression</label>
            <input type="text" id="reminder-cron" name="schedule" placeholder="0 9 * * 1" value="${escapeHtml(schedule)}" />
          </div>
          <p class="reminder-hint">Five fields: minute hour day month weekday. e.g. 0 9 * * 1 = every Monday at 9am.</p>
        </div>

        <div class="reminder-frequency-detail" data-frequency-detail="interval" ${frequencyType !== "interval" ? "hidden" : ""}>
          <div class="reminder-interval-row">
            <div class="reminder-field reminder-field--interval-value">
              <label for="reminder-interval-value">Repeat every</label>
              <input type="number" id="reminder-interval-value" name="interval_value" min="1" value="${escapeHtml(String(intervalValue || ""))}" />
            </div>
            <div class="reminder-field reminder-field--interval-unit">
              <label for="reminder-interval-unit">&nbsp;</label>
              <select id="reminder-interval-unit" name="interval_unit">
                <option value="days" ${intervalUnit === "days" ? "selected" : ""}>days</option>
                <option value="weeks" ${intervalUnit === "weeks" ? "selected" : ""}>weeks</option>
                <option value="months" ${intervalUnit === "months" ? "selected" : ""}>months</option>
              </select>
            </div>
          </div>
          <p class="reminder-hint">Counted from the last time you marked the plant watered.</p>
        </div>
      </div>

      <div class="reminder-section">
        <div class="reminder-section-label">Contacts</div>
        <div data-contact-list>
          ${contactEmails.map((email, index) => contactRowHtml(email, index)).join("")}
        </div>
        <button type="button" class="reminder-add-contact" data-add-contact>+ Add another contact</button>
        <p class="reminder-hint">We'll email a confirmation link to each address. Up to ${MAX_CONTACTS}.</p>
      </div>

      <div class="reminder-modal-actions">
        <button type="submit" class="btn btn-dark reminder-submit-btn">${isEdit ? "Save changes" : "Save reminder"}</button>
        <button type="button" class="reminder-cancel-btn" data-close>Cancel</button>
      </div>
    </form>
  `;
}

function renderSavedView({ notification }) {
  const frequencyLabel = notification?.schedule
    ? "Custom schedule"
    : notification?.interval?.value
      ? `Every ${notification.interval.value} ${notification.interval.unit || "days"}`
      : "—";

  return `
    <div class="reminder-modal-header">
      <button type="button" class="reminder-icon-btn" data-close>${ICONS.close}</button>
      <h3 id="reminder-modal-title" class="reminder-modal-title">Reminder settings</h3>
      <span class="reminder-icon-btn-spacer"></span>
    </div>

    <div class="reminder-saved-banner">${ICONS.check}<span>Saved — check your email to confirm.</span></div>

    <div class="reminder-field">
      <label>Name</label>
      <input type="text" value="${escapeHtml(notification?.name || "")}" disabled />
    </div>

    <div class="reminder-field">
      <label>Description</label>
      <textarea rows="3" disabled>${escapeHtml(notification?.description || "")}</textarea>
    </div>

    <div class="reminder-summary-card">
      <div class="reminder-summary-row">
        <span class="reminder-summary-key">Frequency</span>
        <span class="reminder-summary-value">${escapeHtml(frequencyLabel)}</span>
      </div>
      <div class="reminder-summary-row reminder-summary-row--contacts">
        <span class="reminder-summary-key">Contacts</span>
        <div class="reminder-summary-contacts">${contactStatusHtml(notification?.contacts)}</div>
      </div>
    </div>

    <p class="reminder-hint">Reminders start once at least one address is confirmed. The link expires in 24 hours.</p>

    <div class="reminder-modal-actions">
      <button type="button" class="btn btn-dark reminder-submit-btn" data-close>Back to plants</button>
      <button type="button" class="reminder-cancel-btn" data-resend>Resend confirmation</button>
    </div>
  `;
}

function collectFormData(form) {
  const formData = new FormData(form);
  const frequencyType = formData.get("frequency_type");
  const contacts = Array.from(form.querySelectorAll("[name='contact']"))
    .map((input) => input.value.trim())
    .filter(Boolean);

  const payload = {
    name: (formData.get("name") || "").trim(),
    description: (formData.get("description") || "").trim(),
    contacts,
  };

  if (frequencyType === "interval") {
    payload.interval = {
      value: Number(formData.get("interval_value")) || 1,
      unit: formData.get("interval_unit") || "days",
    };
    payload.schedule = null;
  } else {
    payload.schedule = (formData.get("schedule") || "").trim();
    payload.interval = null;
  }

  return payload;
}

function wireFrequencyToggle(root) {
  const radios = root.querySelectorAll("[data-frequency-radio]");
  radios.forEach((radio) => {
    radio.addEventListener("change", () => {
      root.querySelectorAll("[data-frequency-detail]").forEach((detail) => {
        detail.hidden = detail.dataset.frequencyDetail !== radio.value;
      });
    });
  });
}

function wireContactList(root) {
  const list = root.querySelector("[data-contact-list]");
  const addButton = root.querySelector("[data-add-contact]");
  if (!list || !addButton) return;

  function updateAddButtonState() {
    const count = list.querySelectorAll("[data-contact-row]").length;
    addButton.hidden = count >= MAX_CONTACTS;
  }

  list.addEventListener("click", (event) => {
    const removeButton = event.target.closest("[data-remove-contact]");
    if (!removeButton) return;
    removeButton.closest("[data-contact-row]")?.remove();
    updateAddButtonState();
  });

  addButton.addEventListener("click", () => {
    const count = list.querySelectorAll("[data-contact-row]").length;
    if (count >= MAX_CONTACTS) return;
    list.insertAdjacentHTML("beforeend", contactRowHtml("", count));
    updateAddButtonState();
  });

  updateAddButtonState();
}

export async function openNotificationModal() {
  const overlay = renderModalShell();
  const modalEl = overlay.querySelector(".reminder-modal");

  function close() {
    document.removeEventListener("keydown", onKeydown);
    overlay.remove();
  }

  function onKeydown(event) {
    if (event.key === "Escape") close();
  }

  function wireCloseButtons() {
    modalEl.querySelectorAll("[data-close]").forEach((btn) => btn.addEventListener("click", close));
  }

  function showSavedView(notification) {
    modalEl.innerHTML = renderSavedView({ notification });
    wireCloseButtons();
    modalEl.querySelector("[data-resend]")?.addEventListener("click", async () => {
      try {
        const firstContact = notification?.contacts?.[0]?.email;
        if (firstContact) await resendConfirmation(notification.notification_id, firstContact);
        showNotification("Confirmation email resent.");
      } catch (error) {
        showNotification(error.message || "Unable to resend confirmation.", true);
      }
    });
  }

  function showFormView({ mode, notification }) {
    modalEl.innerHTML = renderFormView({ mode, notification });
    wireCloseButtons();
    wireFrequencyToggle(modalEl);
    wireContactList(modalEl);

    const form = modalEl.querySelector("[data-reminder-form]");
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const submitButton = form.querySelector(".reminder-submit-btn");
      const originalText = submitButton.textContent;
      submitButton.disabled = true;
      submitButton.textContent = mode === "edit" ? "Saving..." : "Submitting...";

      try {
        const payload = collectFormData(form);
        const saved = mode === "edit"
          ? await updateNotification(notification.notification_id, payload)
          : await createNotification(payload);
        showSavedView(saved);
      } catch (error) {
        showNotification(error.message || "Unable to save reminder.", true);
        submitButton.disabled = false;
        submitButton.textContent = originalText;
      }
    });
  }

  overlay.addEventListener("click", (event) => {
    if (event.target === overlay) close();
  });
  document.addEventListener("keydown", onKeydown);
  document.body.appendChild(overlay);

  modalEl.innerHTML = `
    <div class="reminder-modal-header">
      <span class="reminder-icon-btn-spacer"></span>
      <h3 id="reminder-modal-title" class="reminder-modal-title">Reminder settings</h3>
      <span class="reminder-icon-btn-spacer"></span>
    </div>
    <div class="reminder-loading">Loading&hellip;</div>
  `;

  try {
    const notification = await fetchNotification();
    if (notification && notification.notification_id) {
      showFormView({ mode: "edit", notification });
    } else {
      showFormView({ mode: "create", notification: null });
    }
  } catch (error) {
    if (error.status === 404) {
      showFormView({ mode: "create", notification: null });
    } else {
      showFormView({ mode: "create", notification: null });
      showNotification("Couldn't reach the reminder service — you can still set one up.", true);
    }
  }
}

export function wireNotificationBell() {
  const bellButton = document.querySelector("[data-notification-bell]");
  if (!bellButton) return;
  bellButton.innerHTML = ICONS.bell;
  bellButton.addEventListener("click", () => openNotificationModal());
}
