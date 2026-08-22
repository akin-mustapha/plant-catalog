import { escapeHtml } from "../../utils.js";
import { daysAgoShortLabel } from "../plant-detail/watering-history.js";

const STATUS_LABEL = {
  healthy: "Healthy",
  sick: "Sick",
  dead: "Dead",
};

export function statusClass(status) {
  return STATUS_LABEL[status] ? status : "dead";
}

function renderCard(plant) {
  const name = escapeHtml(plant.common_name || "Unnamed plant");
  const nickname = escapeHtml(plant.nick_name || "No nickname");
  const scientificName = escapeHtml(plant.scientific_name || "Unknown");
  const status = statusClass(plant.status);
  const statusLabel = STATUS_LABEL[status];
  const imageUrl = plant.image_url ? escapeHtml(plant.image_url) : "";
  const initial = escapeHtml((plant.common_name || "?").charAt(0).toUpperCase());
  const lastWateredLabel = daysAgoShortLabel(plant.last_watered);

  const media = imageUrl
    ? `<div class="plant-image-wrap"><img src="${imageUrl}" alt="${name}"></div>`
    : `<div class="plant-image-wrap"><div class="plant-image-initial">${initial}</div><div class="plant-image-note">no photo yet</div></div>`;

  return `
    <a class="plant-card" href="pages/plant.html?id=${encodeURIComponent(plant.plant_id)}">
      ${media}
      <div class="plant-card-body">
        <div class="plant-card-title-row">
          <h2>${name} <span class="plant-nick">&ldquo;${nickname}&rdquo;</span></h2>
          <span class="status-chip status-chip--${status}">${statusLabel}</span>
        </div>
        <div class="plant-sci">${scientificName}</div>
        ${lastWateredLabel ? `
        <div class="plant-card-watered">
          <span class="plant-card-watered-dot"></span>
          Last watered <strong>${escapeHtml(lastWateredLabel)}</strong>
        </div>` : ""}
      </div>
    </a>
  `;
}

export function renderSkeleton(count = 5) {
  const listContainer = document.querySelector("[data-plant-list]");
  if (!listContainer) return;

  const skeletonCard = `
    <div class="plant-card plant-card--skeleton">
      <div class="skel-block skeleton-thumb"></div>
      <div class="skeleton-lines">
        <div class="skel-line skeleton-line--wide"></div>
        <div class="skel-line skeleton-line--narrow"></div>
      </div>
    </div>
  `;

  listContainer.innerHTML = skeletonCard.repeat(count);
}

export function renderPlants(plants, activeFilter = "all") {
  const listContainer = document.querySelector("[data-plant-list]");
  if (!listContainer) return;

  if (!Array.isArray(plants) || plants.length === 0) {
    listContainer.innerHTML = `<div class="empty-state">No plants found yet.</div>`;
    return;
  }

  const filtered =
    activeFilter === "all"
      ? plants
      : plants.filter((plant) => statusClass(plant.status) === activeFilter);

  if (filtered.length === 0) {
    listContainer.innerHTML = `<div class="empty-state">No ${activeFilter} plants yet.</div>`;
    return;
  }

  listContainer.innerHTML = filtered.map(renderCard).join("");
}
