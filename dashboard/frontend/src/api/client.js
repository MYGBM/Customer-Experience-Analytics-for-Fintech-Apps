const API_BASE = "http://localhost:8000";

export async function fetchBanks() {
  const res = await fetch(`${API_BASE}/api/banks`);
  return res.json();
}

export async function fetchSummary(bank) {
  const url =
    bank && bank !== "All"
      ? `${API_BASE}/api/summary?bank=${encodeURIComponent(bank)}`
      : `${API_BASE}/api/summary`;
  const res = await fetch(url);
  return res.json();
}

export async function fetchThemes(bank) {
  const url =
    bank && bank !== "All"
      ? `${API_BASE}/api/themes?bank=${encodeURIComponent(bank)}`
      : `${API_BASE}/api/themes`;
  const res = await fetch(url);
  return res.json();
}

export async function fetchSentiment(bank) {
  const url =
    bank && bank !== "All"
      ? `${API_BASE}/api/sentiment?bank=${encodeURIComponent(bank)}`
      : `${API_BASE}/api/sentiment`;
  const res = await fetch(url);
  return res.json();
}

export async function fetchReviews(
  bank,
  theme,
  sentiment,
  page = 1,
  limit = 10,
) {
  const params = new URLSearchParams();
  if (bank && bank !== "All") params.set("bank", bank);
  if (theme) params.set("theme", theme);
  if (sentiment) params.set("sentiment", sentiment);
  params.set("page", page);
  params.set("limit", limit);
  const res = await fetch(`${API_BASE}/api/reviews?${params.toString()}`);
  return res.json();
}

export async function fetchThemeSentiment(bank) {
  const url =
    bank && bank !== "All"
      ? `${API_BASE}/api/theme-sentiment?bank=${encodeURIComponent(bank)}`
      : `${API_BASE}/api/theme-sentiment`;
  const res = await fetch(url);
  return res.json();
}
