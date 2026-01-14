const API_BASE_URL = "http://127.0.0.1:8000";

export async function searchProperties(payload: any) {
  const res = await fetch(`${API_BASE_URL}/api/search`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error("Failed to fetch properties");
  }

  return res.json();
}
