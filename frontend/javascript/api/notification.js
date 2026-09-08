import client from "./client.js";

export async function fetchNotification() {
  const { data } = await client.get("/notifications");
  return data;
}

export async function createNotification(notification) {
  const { data } = await client.post("/notifications", notification);
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
