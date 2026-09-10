import { fetchPlantById } from "../../api/plant.js";
import { fetchActivitiesByPlantId, fetchActivityTypes } from "../../api/activity.js";
import { setStatus, showNotification, unwrap } from "../../utils.js";
import { renderPlantDetails, renderPlantDetailsSkeleton } from "./render.js";
import {
  wireDeleteButton,
  wireFertilizeButton,
  wireImageUpload,
  wireWaterButton,
} from "./events.js";
import { wireNotificationBell } from "../../notification-modal.js";

const pathParams = new URLSearchParams(window.location.search);
const plantId = pathParams.get("id");

wireNotificationBell(plantId);

function showPendingNotification() {
  const pending = sessionStorage.getItem("notification");
  if (!pending) return;
  sessionStorage.removeItem("notification");
  showNotification(pending);
}

async function loadPlantDetails(id) {
  try {
    renderPlantDetailsSkeleton();
    const response = await fetchPlantById(id);
    const plant = unwrap(response);
    if (!plant) {
      setStatus("Plant not found.", true);
      return;
    }

    const [rawActivities, activityTypes] = await Promise.all([
      fetchActivitiesByPlantId(id).catch(() => []),
      fetchActivityTypes().catch(() => []),
    ]);

    const typeById = new Map((activityTypes || []).map((type) => [type.activity_type_id, type.description]));
    const activities = (rawActivities || []).map((activity) => ({
      ...activity,
      __typeDescription: typeById.get(activity.activity_type_id) || null,
    }));

    renderPlantDetails(plant, activities);
    const hasNickname = plant.nick_name && plant.nick_name !== "No nickname";
    const plantLabel = hasNickname ? plant.nick_name : plant.common_name || "this plant";
    wireDeleteButton(id, plantLabel);
    wireImageUpload(id);

    const wateringType = (activityTypes || []).find((type) => type.description === "Watering");
    wireWaterButton(id, wateringType?.activity_type_id, plantLabel);

    const fertilizingType = (activityTypes || []).find((type) => type.description === "Fertilizing");
    wireFertilizeButton(id, fertilizingType?.activity_type_id, plantLabel);

    setStatus("");
    showPendingNotification();
  } catch (error) {
    setStatus(error.message || "Unable to load plant details.", true);
  }
}

if (plantId) {
  loadPlantDetails(plantId);
} else {
  setStatus("No plant ID provided in the URL.", true);
}
