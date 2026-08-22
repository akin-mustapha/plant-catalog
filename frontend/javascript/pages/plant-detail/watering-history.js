export function buildWateringHistory(activities, months = 6) {
  const wateredDates = new Set(
    (activities || []).map((activity) => new Date(activity.activity_date).toDateString())
  );

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const startDay = today.getDay();
  const daysSinceMonday = (startDay + 6) % 7;
  const thisMonday = new Date(today);
  thisMonday.setDate(today.getDate() - daysSinceMonday);

  const rangeStart = new Date(today);
  rangeStart.setMonth(rangeStart.getMonth() - months);
  const daysSinceMondayForStart = (rangeStart.getDay() + 6) % 7;
  const firstMonday = new Date(rangeStart);
  firstMonday.setDate(rangeStart.getDate() - daysSinceMondayForStart);

  const totalWeeks = Math.ceil((thisMonday - firstMonday) / (7 * 24 * 60 * 60 * 1000)) + 1;

  const weeks = [];
  let lastWateredDate = null;

  for (let w = 0; w < totalWeeks; w++) {
    const week = [];
    for (let d = 0; d < 7; d++) {
      const date = new Date(firstMonday);
      date.setDate(firstMonday.getDate() + w * 7 + d);

      if (date > today) {
        week.push(null);
        continue;
      }

      const watered = wateredDates.has(date.toDateString());
      week.push({ date, watered });
      if (watered && (!lastWateredDate || date > lastWateredDate)) {
        lastWateredDate = date;
      }
    }
    weeks.push(week);
  }

  return { weeks, lastWateredDate };
}

export function daysAgoLabel(date) {
  if (!date) return "No waterings logged yet";

  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const compared = new Date(date);
  compared.setHours(0, 0, 0, 0);

  const diffDays = Math.round((today - compared) / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return "Today";
  if (diffDays === 1) return "1 day ago";
  return `${diffDays} days ago`;
}

export function daysAgoShortLabel(date) {
  if (!date) return null;

  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const compared = new Date(date);
  compared.setHours(0, 0, 0, 0);

  const diffDays = Math.round((today - compared) / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return "Today";
  if (diffDays === 1) return "yesterday";
  if (diffDays < 7) return `${diffDays} days ago`;
  const weeks = Math.round(diffDays / 7);
  if (diffDays < 30) return `${weeks} week${weeks === 1 ? "" : "s"} ago`;
  const months = Math.round(diffDays / 30);
  return `${months} month${months === 1 ? "" : "s"} ago`;
}
