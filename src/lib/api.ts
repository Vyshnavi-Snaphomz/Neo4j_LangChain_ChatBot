const normalizeBaseUrl = (baseUrl?: string) => {
  if (!baseUrl) return "";
  return baseUrl.endsWith("/") ? baseUrl.slice(0, -1) : baseUrl;
};

const buildUrl = (path: string) => (path.startsWith("/") ? path : `/${path}`);

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
  location?: string;
  budget?: number;
  income?: number;
  down_payment?: number;
  loan_term?: number;
  mortgage_rate?: number;
};

export type QuestionPayload = {
  question: string;
};

export async function searchProperties(payload: SearchPayload) {
  const res = await fetch(buildUrl("/api/search"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error("Unable to fetch listings right now.");
  }

  return res.json();
}

export async function rentVsBuy(payload: RentVsBuyPayload) {
  const res = await fetch(buildUrl("/rent-vs-buy"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error("Unable to fetch rent vs buy analysis right now.");
  }

  return res.json();
}

export async function askQuestion(payload: QuestionPayload) {
  const res = await fetch(buildUrl("/api/question"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error("Unable to fetch an answer right now.");
  }

  return res.json();
}
