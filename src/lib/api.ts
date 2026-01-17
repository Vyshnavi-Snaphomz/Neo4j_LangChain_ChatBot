// ✅ CONFIRMED BACKEND CONTRACT (IMMUTABLE)
// Backend Base URL: http://127.0.0.1:8001
const API_BASE = "http://127.0.0.1:8001";

export type SearchPayload = {
  query: string;
  state?: string | null;
  city?: string | null;
  zip_code?: string | null;
  min_price?: number | null;
  max_price?: number | null;
  beds?: number | null;
  baths?: number | null;
  school_rating_min?: number | null;
  use_cache?: boolean | null;
};

export type RentVsBuyPayload = {
  location?: string;      // Full state name (e.g., "California")
  budget?: number;        // Included as per user requirement (Backend might ignore or use)
  income?: number;        // Annual income
  down_payment?: number;  // Optional, defaults to backend value
  loan_term?: number;     // Optional, defaults to 30
  mortgage_rate?: number; // Optional, defaults to backend value
};

export type QuestionPayload = {
  question: string;
};

export async function searchProperties(payload: SearchPayload) {
  const res = await fetch(`${API_BASE}/api/search`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json"
    },
    body: JSON.stringify({
      query: payload.query
    }),
  });

  if (!res.ok) {
    throw new Error("Backend request failed");
  }

  return res.json();
}

export async function rentVsBuy(payload: RentVsBuyPayload) {
  // Log the request for debugging
  console.log('[API] Rent vs Buy Request:', JSON.stringify(payload, null, 2));

  const res = await fetch(`${API_BASE}/rent-vs-buy`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json"
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errorText = await res.text();
    console.error('[API] Rent vs Buy Error:', res.status, errorText);
    if (res.status === 422) {
      throw new Error("Missing required details to calculate rent vs buy. Please provide state, budget, and monthly income.");
    }
    throw new Error("Service temporarily unavailable. Please try again.");
  }

  return res.json();
}

export async function askQuestion(payload: QuestionPayload) {
  // Use /question endpoint (not /api/question)
  const res = await fetch(`${API_BASE}/question`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json"
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errorText = await res.text();
    console.error('[API] Question Error:', res.status, errorText);
    throw new Error("Service temporarily unavailable. Please try again.");
  }

  return res.json();
}
