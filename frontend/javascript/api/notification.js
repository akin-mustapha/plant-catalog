import client from "./client.js";

export async function fetchNotification(plantId) {
  const { data } = await client.get(`/plants/${plantId}/notifications`);
  return data;
}

export async function createNotification(plantId, notification) {
  const { data } = await client.post(`/plants/${plantId}/notifications`, notification);
  return data;
}

export async function updateNotification(notificationId, notification) {
  const { data } = await client.put(`/notifications/${notificationId}`, notification);
  return data;
}

export async function resendConfirmation(notificationId, email) {
  const { data } = await client.post(`/notifications/${notificationId}/resend-confirmation`, { email });
  return data;
}
