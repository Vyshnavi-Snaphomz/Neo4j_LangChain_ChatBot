import { useState, useCallback, useRef, useEffect } from "react";

import HeroSection from "@/components/HeroSection";
import SearchSection from "@/components/SearchBar";
import Sidebar from "@/components/Sidebar";
import ImageLightbox from "@/components/ImageLightbox";
import LoadingState from "@/components/LoadingState";

import { searchProperties, rentVsBuy, askQuestion } from "@/lib/api";
import {
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  XAxis,
  YAxis,
} from "recharts";

import {
  SearchResult,
  Property,
  RentVsBuyResult,
  RentVsBuyResponse,
} from "@/data/mockData";

const PROPERTY_KEYWORDS = [
  "show",
  "find",
  "list",
  "houses",
  "homes",
  "properties",
  "apartments",
];

const RENT_BUY_KEYWORDS = [
  "rent vs buy",
  "rent or buy",
  "should i rent",
  "should i buy",
  "buy or rent",
  "is it better to rent",
];

const GENERAL_INFO_KEYWORDS = [
  "market",
  "trending",
  "trend",
  "expensive",
  "safe",
  "safety",
  "crime",
  "schools",
  "rates",
  "interest",
  "forecast",
  "inventory",
  "appreciation",
  "affordability",
  "taxes",
  "insurance",
];

type UnknownRecord = Record<string, unknown>;

const isRecord = (value: unknown): value is UnknownRecord =>
  typeof value === "object" && value !== null;

const getString = (value: unknown): string | undefined =>
  typeof value === "string" ? value : undefined;

const formatPrice = (value: unknown): string | undefined => {
  if (value === null || value === undefined) return undefined;
  if (typeof value === "number" && Number.isFinite(value)) {
    return `$${value.toLocaleString("en-US")}`;
  }
  if (typeof value === "string") {
    const trimmed = value.trim();
    if (!trimmed) return undefined;
    if (trimmed.includes("$")) return trimmed;
    const numeric = Number(trimmed.replace(/[^0-9.]/g, ""));
    if (Number.isFinite(numeric) && /\d/.test(trimmed)) {
      return `$${numeric.toLocaleString("en-US")}`;
    }
    return trimmed;
  }
  return undefined;
};

const formatAddress = (item: unknown): string | undefined => {
  if (!isRecord(item)) return undefined;
  const addressUnparsed = getString(item.addressUnparsedAddress);
  if (addressUnparsed) return addressUnparsed;
  const addressString = getString(item.address);
  if (addressString) return addressString;

  const addressObj = isRecord(item.address) ? item.address : null;
  if (addressObj) {
    const parts = [
      getString(addressObj.street),
      getString(addressObj.city),
      getString(addressObj.state),
      getString(addressObj.postal_code ?? addressObj.postalCode ?? addressObj.zip),
    ].filter(Boolean) as string[];
    if (parts.length) return parts.join(", ");
  }

  const parts = [getString(item.city), getString(item.state)].filter(
    Boolean
  ) as string[];

  return parts.length ? parts.join(", ") : undefined;
};

const parseNumber = (value: unknown): number | undefined => {
  const numeric = typeof value === "number" ? value : Number(value);
  return Number.isFinite(numeric) ? numeric : undefined;
};

const formatBedsBaths = (beds?: number, baths?: number) => {
  const parts: string[] = [];
  if (beds !== undefined) parts.push(`${beds} beds`);
  if (baths !== undefined) parts.push(`${baths} baths`);
  return parts.join(" / ");
};

const formatCurrency = (value: number | string | undefined) => {
  if (value === null || value === undefined) return undefined;
  if (typeof value === "number" && Number.isFinite(value)) {
    return `$${value.toLocaleString("en-US")}`;
  }
  if (typeof value === "string") {
    const trimmed = value.trim();
    if (!trimmed) return undefined;
    if (trimmed.includes("$")) return trimmed;
    const numeric = Number(trimmed.replace(/[^0-9.]/g, ""));
    if (Number.isFinite(numeric) && /\d/.test(trimmed)) {
      return `$${numeric.toLocaleString("en-US")}`;
    }
    return trimmed;
  }
  return undefined;
};

const formatPercent = (value: number | string | undefined) => {
  if (value === null || value === undefined) return undefined;
  if (typeof value === "number" && Number.isFinite(value)) {
    const normalized = value <= 1 ? value * 100 : value;
    return `${Math.round(normalized)}%`;
  }
  if (typeof value === "string") return value;
  return undefined;
};

const formatLabel = (value: string) =>
  value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (match) => match.toUpperCase());

const hasBudgetPattern = (query: string) => {
  const normalized = query.toLowerCase();
  const hasCurrency = /\$/.test(query);
  const hasUnit = /\b\d+(?:\.\d+)?\s?(k|m)\b/.test(normalized);
  const hasComma = /\d{1,3}(,\d{3})+/.test(query);
  const hasLargeNumber = /\b\d{6,}\b/.test(query);
  const hasBudgetWord =
    /\b(budget|price|cost|afford|down payment|mortgage)\b/i.test(normalized);
  const hasNumber = /\b\d{3,}\b/.test(query);

  return (
    hasCurrency ||
    hasUnit ||
    hasComma ||
    hasLargeNumber ||
    (hasBudgetWord && hasNumber)
  );
};

const isRentVsBuyQuery = (query: string) => {
  const normalized = query.toLowerCase();
  const hasKeyword = RENT_BUY_KEYWORDS.some((keyword) =>
    normalized.includes(keyword)
  );
  return hasKeyword || hasBudgetPattern(query);
};

const hasGeneralInfoCue = (query: string) => {
  const normalized = query.toLowerCase();
  return GENERAL_INFO_KEYWORDS.some((keyword) => normalized.includes(keyword));
};

const isLocationListingRequest = (query: string) => {
  const trimmed = query.trim();
  if (!trimmed) return false;

  const looksLikeQuestion =
    /\?/.test(trimmed) ||
    /^(who|what|when|where|why|how|is|are|do|does|can|should|would)\b/i.test(
      trimmed
    );

  if (looksLikeQuestion) return false;

  const hasZip = /\b\d{5}(?:-\d{4})?\b/.test(trimmed);
  const hasCityState =
    /\b[a-zA-Z]+(?:\s+[a-zA-Z]+)*,\s*[A-Z]{2}\b/.test(trimmed);
  const hasLocationPhrase =
    /\b(in|near|around|at)\s+[a-zA-Z\s,]{2,}/i.test(trimmed);
  const wordCount = trimmed.split(/\s+/).length;
  const shortLocation = wordCount <= 4 && /[a-zA-Z]/.test(trimmed);

  return hasZip || hasCityState || hasLocationPhrase || shortLocation;
};

const hasPropertyKeyword = (query: string) =>
  PROPERTY_KEYWORDS.some((keyword) =>
    new RegExp(`\\b${keyword}\\b`, "i").test(query)
  );

const detectIntent = (query: string) => {
  if (isRentVsBuyQuery(query)) return "rent-vs-buy" as const;

  if (hasPropertyKeyword(query)) return "property" as const;
  if (hasGeneralInfoCue(query)) return "general" as const;
  if (isLocationListingRequest(query)) return "property" as const;
  return "general" as const;
};

const isNumericOnlyQuery = (query: string) =>
  /^[\s$]*[\d,.]+\s?(k|m)?\s*$/i.test(query.trim());

const parseMoneyValue = (query: string): number | null => {
  const match = query.match(/\$?([\d,]+)\s?(k|m)?/i);
  if (!match) return null;

  let value = Number(match[1].replace(/,/g, ""));
  const unit = match[2]?.toLowerCase();

  if (unit === "k") value *= 1000;
  if (unit === "m") value *= 1000000;

  return Number.isFinite(value) ? value : null;
};

const extractBudget = (query: string): number | null => {
  const normalized = query.toLowerCase();
  const hasBudgetCue =
    /\$/.test(query) ||
    /\b(k|m)\b/i.test(query) ||
    /\b(budget|price|cost|with|under|over|around)\b/i.test(normalized);
  const incomeOnly = /\bincome\b/i.test(normalized) && !hasBudgetCue;
  if (incomeOnly) return null;

  return parseMoneyValue(query);
};

const extractLocation = (query: string): string | null => {
  const match = query.match(/\b(?:in|at|near|around)\s+([a-zA-Z\s,]+)/i);
  const cleanup = (value: string) =>
    value
      .replace(
        /\b(with|for|budget|under|over|around|income|down payment|mortgage|loan|rate)\b.*$/i,
        ""
      )
      .trim();
  const isTrivial = (value: string) => {
    const normalized = value.toLowerCase().trim();
    return (
      !normalized ||
      ["my", "me", "i", "mine"].includes(normalized) ||
      /\b(income|budget|rent|buy)\b/i.test(normalized)
    );
  };

  if (match) {
    const location = cleanup(match[1]);
    return location && !isTrivial(location) ? location : null;
  }

  const cutoffMatch = query.match(
    /^(.*?)(?:\band\b|\bwith\b|\bincome\b|\bbudget\b|\bdown payment\b|\bmortgage\b|\bloan\b|\brate\b)/i
  );
  const candidate = cleanup(cutoffMatch ? cutoffMatch[1] : query).trim();
  if (!candidate || !/[a-zA-Z]/.test(candidate)) return null;
  if (isTrivial(candidate)) return null;
  if (/\brent\b|\bbuy\b/i.test(candidate)) return null;
  return candidate.length > 80 ? null : candidate;
};

const isLikelyLocationReply = (query: string) => {
  const normalized = query.toLowerCase().trim();
  if (/\b(in|at|near|around)\b/.test(normalized)) return true;
  if (/\d/.test(normalized)) return false;
  if (/\b(income|budget|mortgage|loan|rate|down payment)\b/.test(normalized))
    return false;
  if (/\b(rent|buy)\b/.test(normalized)) return false;
  return normalized.split(/\s+/).length <= 3;
};

const extractIncome = (query: string): number | null => {
  const normalized = query.toLowerCase();
  if (!normalized.includes("income")) return null;
  const match =
    query.match(/\bincome\b[^0-9$%]*\$?([\d,]+)\s?(k|m)?/i) ??
    query.match(/\bmonthly income\b[^0-9$%]*\$?([\d,]+)\s?(k|m)?/i);
  if (!match) return null;
  const value = parseMoneyValue(match[0]);
  return Number.isFinite(value ?? NaN) ? value : null;
};

const extractDownPayment = (query: string): number | null => {
  if (!/down payment/i.test(query)) return null;
  const percentMatch = query.match(/(\d{1,2}(?:\.\d+)?)\s*%/);
  if (percentMatch) {
    const percentValue = Number(percentMatch[1]);
    return Number.isFinite(percentValue) ? percentValue : null;
  }
  return parseMoneyValue(query);
};

const extractLoanTerm = (query: string): number | null => {
  if (!/loan term|mortgage term|year mortgage|years/i.test(query)) return null;
  const match = query.match(/(\d{1,2})\s*(year|yr|years)/i);
  if (!match) return null;
  const value = Number(match[1]);
  return Number.isFinite(value) ? value : null;
};

const extractMortgageRate = (query: string): number | null => {
  if (!/rate|interest/i.test(query)) return null;
  const match = query.match(/(\d{1,2}(?:\.\d+)?)\s*%/);
  if (!match) return null;
  const value = Number(match[1]);
  return Number.isFinite(value) ? value : null;
};

const buildGeneralSummary = (query: string) => {
  const clean = query.trim();
  return [
    `Here is a quick take on "${clean}".`,
    "Markets are hyper-local, so prices, rents, and competition can shift block by block. Recent rate moves, inventory, and seasonality usually drive the short-term swings.",
    "If you want listings, share a city or zip and any must-haves like beds, budget, or commute time.",
  ].join("\n\n");
};

const extractAnswerText = (data: unknown): string | null => {
  if (!isRecord(data)) return null;
  const direct = getString(data.answer) ?? getString(data.message);
  if (direct) return direct;
  if (isRecord(data.result)) {
    const nested = getString(data.result.answer) ?? getString(data.result.message);
    if (nested) return nested;
  }
  return null;
};

type PropertyExtras = {
  photos?: string[];
  livingArea?: number;
  score?: number;
  description?: string;
  url?: string;
};

type LightboxProperty = Property & {
  images?: string[];
};

type RentVsBuyDraft = {
  query: string;
  location?: string;
  budget?: number;
  income?: number;
  down_payment?: number;
  loan_term?: number;
  mortgage_rate?: number;
};

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  type: "text" | "property" | "rent-vs-buy";
  text?: string;
  result?: SearchResult | RentVsBuyResult;
};

type ChatThread = {
  id: string;
  title: string;
  timestamp: Date;
  messages: ChatMessage[];
};

const extractPhotos = (item: unknown): string[] => {
  const record = isRecord(item) ? item : {};
  const list = Array.isArray(record.photos)
    ? record.photos
    : (() => {
        const rawListing = isRecord(record._raw_listing)
          ? record._raw_listing
          : null;
        const media = rawListing && isRecord(rawListing.media) ? rawListing.media : null;
        return Array.isArray(media?.photosList) ? media?.photosList : [];
      })();

  if (Array.isArray(list)) {
    return list
      .map((photo) => {
        if (typeof photo === "string") return photo;
        if (!isRecord(photo)) return undefined;
        return (
          getString(photo.highRes) ||
          getString(photo.midRes) ||
          getString(photo.url)
        );
      })
      .filter(Boolean) as string[];
  }

  const imageUrl = getString(record.image_url);
  return imageUrl ? [imageUrl] : [];
};

const mapApiResponseToSearchResult = (
  query: string,
  data: unknown
): SearchResult => {
  const record = isRecord(data) ? data : {};
  const parseJsonArray = (value: unknown): unknown[] => {
    if (typeof value !== "string") return [];
    try {
      const parsed = JSON.parse(value);
      if (Array.isArray(parsed)) return parsed;
      if (isRecord(parsed)) {
        return (
          (Array.isArray(parsed.properties) && parsed.properties) ||
          (Array.isArray(parsed.results) && parsed.results) ||
          (Array.isArray(parsed.listings) && parsed.listings) ||
          []
        );
      }
    } catch {
      return [];
    }
    return [];
  };
  const extractArray = (value: unknown): unknown[] => {
    if (Array.isArray(value)) return value;
    if (isRecord(value)) {
      const nested =
        (Array.isArray(value.items) && value.items) ||
        (Array.isArray(value.properties) && value.properties) ||
        (Array.isArray(value.results) && value.results) ||
        (Array.isArray(value.listings) && value.listings) ||
        (Array.isArray(value.records) && value.records) ||
        (Array.isArray(value.data) && value.data);
      if (nested) return nested;
      const parsed = parseJsonArray(value.properties) || parseJsonArray(value.data);
      if (parsed.length) return parsed;
      if (isRecord(value.data)) {
        const nestedData =
          (Array.isArray(value.data.items) && value.data.items) ||
          (Array.isArray(value.data.properties) && value.data.properties) ||
          (Array.isArray(value.data.results) && value.data.results) ||
          (Array.isArray(value.data.listings) && value.data.listings) ||
          (Array.isArray(value.data.records) && value.data.records);
        return nestedData ?? [];
      }
      return [];
    }
    return [];
  };

  const propertyCandidates = [
    extractArray(Array.isArray(data) ? data : undefined),
    extractArray(record.properties),
    extractArray(record.results),
    extractArray(record.listings),
    extractArray(record.records),
    extractArray(record.data),
    extractArray(isRecord(record.data) ? record.data.properties : undefined),
    extractArray(isRecord(record.data) ? record.data.results : undefined),
    extractArray(isRecord(record.data) ? record.data.listings : undefined),
    parseJsonArray(record.properties),
    parseJsonArray(record.data),
  ];

  const rawProperties =
    propertyCandidates.find((items) => items.length > 0) ?? [];

  const mappedProperties: Property[] = rawProperties.map(
    (item: unknown, index: number) => {
      const itemRecord = isRecord(item) ? item : {};
      const photos = extractPhotos(itemRecord);
      const location = isRecord(itemRecord.location) ? itemRecord.location : null;
      return {
        id: String(
          itemRecord.id ??
            itemRecord.listing_id ??
            itemRecord.property_id ??
            itemRecord._id ??
            `${query}-${index}`
        ),
        image: photos[0] ?? getString(itemRecord.image_url) ?? "",
        source:
          getString(itemRecord.source) ??
          getString(itemRecord.provider) ??
          getString(itemRecord.site) ??
          "Listing",
        sourceColor: getString(itemRecord.sourceColor) ??
          getString(itemRecord.source_color) ??
          "#0f172a",
        price: formatPrice(itemRecord.list_price ?? itemRecord.price),
        address:
          formatAddress(itemRecord) ??
          getString(itemRecord.full_address) ??
          getString(location?.address),
        beds: parseNumber(
          itemRecord.propertyBedroomTotal ?? itemRecord.beds ?? itemRecord.bedrooms
        ),
        baths: parseNumber(
          itemRecord.propertyBathroomTotal ?? itemRecord.baths ?? itemRecord.bathrooms
        ),
        photos,
        livingArea: parseNumber(itemRecord.living_area ?? itemRecord.propertyLivingArea),
        score: typeof itemRecord.score === "number" ? itemRecord.score : undefined,
        description:
          getString(itemRecord.publicRemark) ??
          getString(itemRecord.remarks) ??
          getString(itemRecord.description),
        url: getString(itemRecord.url),
      };
    }
  );

  const limitedProperties = mappedProperties.slice(0, 10);

  const timestampRaw = record.timestamp;
  const timestampValue =
    typeof timestampRaw === "string" || typeof timestampRaw === "number"
      ? new Date(timestampRaw)
      : new Date();
  const timestamp = Number.isNaN(timestampValue.getTime())
    ? new Date()
    : timestampValue;

  return {
    type: "search",
    query: getString(record.query) ?? query,
    sourcesCount:
      (typeof record.sourcesCount === "number" ? record.sourcesCount : undefined) ??
      (typeof record.sources_count === "number" ? record.sources_count : undefined) ??
      limitedProperties.length,
    followUps: [],
    properties: limitedProperties,
    summary:
      getString(record.summary) ??
      getString(record.answer) ??
      getString(record.message) ??
      "",
    timestamp,
  };
};

const truncateText = (value: string, maxLength = 160) => {
  if (value.length <= maxLength) return value;
  return `${value.slice(0, maxLength).trim()}...`;
};

const Index = () => {
  const [threads, setThreads] = useState<ChatThread[]>([]);
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [rentVsBuyDraft, setRentVsBuyDraft] = useState<RentVsBuyDraft | null>(
    null
  );
  const [rentVsBuyMissing, setRentVsBuyMissing] = useState<string[]>([]);
  const [lastRentVsBuyPrompt, setLastRentVsBuyPrompt] = useState<string | null>(
    null
  );
  const [lightboxProperty, setLightboxProperty] = useState<LightboxProperty | null>(
    null
  );
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const activeThreadIdRef = useRef<string | null>(null);

  const activeThread = threads.find((thread) => thread.id === activeThreadId);
  const messages = activeThread?.messages ?? [];

  useEffect(() => {
    activeThreadIdRef.current = activeThreadId;
  }, [activeThreadId]);

  const appendMessage = useCallback((message: ChatMessage) => {
    setThreads((prev) => {
      const currentThreadId = activeThreadIdRef.current;
      if (!currentThreadId) {
        const newThreadId = `${Date.now()}-thread`;
        const title =
          message.role === "user" && message.text ? message.text : "New chat";
        const nextThread: ChatThread = {
          id: newThreadId,
          title,
          timestamp: new Date(),
          messages: [message],
        };
        activeThreadIdRef.current = newThreadId;
        setActiveThreadId(newThreadId);
        return [...prev, nextThread];
      }

      return prev.map((thread) => {
        if (thread.id !== currentThreadId) return thread;
        const nextTitle =
          thread.title === "New chat" && message.role === "user" && message.text
            ? message.text
            : thread.title;
        return {
          ...thread,
          title: nextTitle,
          timestamp: new Date(),
          messages: [...thread.messages, message],
        };
      });
    });
  }, []);

  const buildRentVsBuyDraft = (
    query: string,
    existingDraft: RentVsBuyDraft | null,
    missingFields: string[]
  ): RentVsBuyDraft => {
    const baseQuery = existingDraft?.query ?? query;
    const numericValue = isNumericOnlyQuery(query) ? parseMoneyValue(query) : null;
    const incomeFromQuery = extractIncome(query);
    const budgetFromQuery = extractBudget(query);
    const locationFromQuery = extractLocation(query);
    const downPaymentFromQuery = extractDownPayment(query);
    const loanTermFromQuery = extractLoanTerm(query);
    const mortgageRateFromQuery = extractMortgageRate(query);
    const locationFromBase = extractLocation(baseQuery);

    let location = existingDraft?.location ?? locationFromBase ?? undefined;
    if (locationFromQuery && isLikelyLocationReply(query)) {
      location = locationFromQuery;
    }

    let income = existingDraft?.income ?? undefined;
    let budget = existingDraft?.budget ?? undefined;
    let downPayment = existingDraft?.down_payment ?? undefined;
    let loanTerm = existingDraft?.loan_term ?? undefined;
    let mortgageRate = existingDraft?.mortgage_rate ?? undefined;

    if (incomeFromQuery !== null) income = incomeFromQuery;
    if (budgetFromQuery !== null) budget = budgetFromQuery;
    if (downPaymentFromQuery !== null) downPayment = downPaymentFromQuery;
    if (loanTermFromQuery !== null) loanTerm = loanTermFromQuery;
    if (mortgageRateFromQuery !== null) mortgageRate = mortgageRateFromQuery;

    if (numericValue !== null) {
      if (missingFields.includes("income") && income === undefined) {
        income = numericValue;
      } else if (missingFields.includes("budget") && budget === undefined) {
        budget = numericValue;
      } else if (income === undefined && budget !== undefined) {
        income = numericValue;
      } else if (budget === undefined && income !== undefined) {
        budget = numericValue;
      } else if (income === undefined) {
        income = numericValue;
      }
    }

    return {
      query: baseQuery,
      location,
      budget,
      income,
      down_payment: downPayment,
      loan_term: loanTerm,
      mortgage_rate: mortgageRate,
    };
  };

  const handleSearch = useCallback(
    async (query: string) => {
      const trimmed = query.trim();
      if (!trimmed) return;

      appendMessage({
        id: `${Date.now()}-user`,
        role: "user",
        type: "text",
        text: trimmed,
      });

      setIsSearching(true);

      const detectedIntent = detectIntent(trimmed);
      const isFollowUpLocation =
        !!rentVsBuyDraft &&
        !rentVsBuyDraft.location &&
        isLikelyLocationReply(trimmed) &&
        !hasPropertyKeyword(trimmed);
      const isRentVsBuyFollowUp =
        !!rentVsBuyDraft &&
        !hasPropertyKeyword(trimmed) &&
        (isNumericOnlyQuery(trimmed) ||
          /\bincome\b|\bbudget\b/i.test(trimmed));
      const resolvedIntent =
        rentVsBuyDraft &&
        (detectedIntent === "rent-vs-buy" ||
          isFollowUpLocation ||
          isRentVsBuyFollowUp)
          ? "rent-vs-buy"
          : detectedIntent;

      try {
        if (resolvedIntent === "rent-vs-buy") {
          const updatedDraft = buildRentVsBuyDraft(
            trimmed,
            rentVsBuyDraft,
            rentVsBuyMissing
          );
          setRentVsBuyDraft(updatedDraft);

          const missingFields: string[] = [];
          if (!updatedDraft.location) missingFields.push("location");
          if (updatedDraft.budget === undefined) missingFields.push("budget");
          if (updatedDraft.income === undefined) missingFields.push("income");

          setRentVsBuyMissing(missingFields);

          if (missingFields.length > 0) {
            const readableMissing = missingFields
              .map((item) => formatLabel(String(item)))
              .join(" and ");
            const messageText = `To compare rent vs buy, I still need your ${readableMissing}.`;
            const promptKey = [...missingFields].sort().join("|");

            if (promptKey !== lastRentVsBuyPrompt) {
              appendMessage({
                id: `${Date.now()}-assistant`,
                role: "assistant",
                type: "text",
                text: messageText,
              });
              setLastRentVsBuyPrompt(promptKey);
            }
            return;
          }

          const response = await rentVsBuy({
            location: updatedDraft.location,
            budget: updatedDraft.budget,
            income: updatedDraft.income,
            down_payment: updatedDraft.down_payment,
            loan_term: updatedDraft.loan_term,
            mortgage_rate: updatedDraft.mortgage_rate,
          });
          const result: RentVsBuyResult = {
            type: "rent-vs-buy",
            query: trimmed,
            timestamp: new Date(),
            response,
            inputs: {
              location: updatedDraft.location,
              budget: updatedDraft.budget,
              income: updatedDraft.income,
              down_payment: updatedDraft.down_payment,
              loan_term: updatedDraft.loan_term,
              mortgage_rate: updatedDraft.mortgage_rate,
            },
          };

          setRentVsBuyDraft(null);
          setRentVsBuyMissing([]);
          setLastRentVsBuyPrompt(null);

          appendMessage({
            id: `${Date.now()}-assistant`,
            role: "assistant",
            type: "rent-vs-buy",
            result,
          });

          return;
        }

        if (resolvedIntent === "property") {
          if (rentVsBuyDraft) {
            setRentVsBuyDraft(null);
            setRentVsBuyMissing([]);
            setLastRentVsBuyPrompt(null);
          }
          const apiResponse = await searchProperties({
            query: trimmed,
            state: null,
            city: null,
            zip_code: null,
            min_price: null,
            max_price: null,
            beds: null,
            baths: null,
            school_rating_min: null,
            use_cache: true,
          });
          const result = mapApiResponseToSearchResult(trimmed, apiResponse);
          const introText = `Here are 10 homes in ${result.query}.`;

          appendMessage({
            id: `${Date.now()}-assistant`,
            role: "assistant",
            type: "property",
            text: introText,
            result,
          });
          return;
        }

        if (rentVsBuyDraft) {
          setRentVsBuyDraft(null);
          setRentVsBuyMissing([]);
          setLastRentVsBuyPrompt(null);
        }

        const response = await askQuestion({ question: trimmed });
        const answerText = extractAnswerText(response) ?? buildGeneralSummary(trimmed);

        appendMessage({
          id: `${Date.now()}-assistant`,
          role: "assistant",
          type: "text",
          text: answerText,
        });
      } catch (error) {
        const fallbackMessage =
          resolvedIntent === "rent-vs-buy"
            ? "I am having trouble reaching the rent vs buy service right now. Please try again in a moment."
            : resolvedIntent === "property"
            ? "I am having trouble reaching the listings service right now. Please try again in a moment."
            : "I am having trouble responding right now. Please try again in a moment.";
        appendMessage({
          id: `${Date.now()}-assistant`,
          role: "assistant",
          type: "text",
          text: fallbackMessage,
        });
      } finally {
        setIsSearching(false);
      }
    },
    [appendMessage, rentVsBuyDraft, rentVsBuyMissing, lastRentVsBuyPrompt]
  );

  const renderParagraphs = (text: string) =>
    text
      .split(/\n\s*\n/)
      .map((paragraph, index) => (
        <p key={`${paragraph}-${index}`} className="text-sm leading-relaxed">
          {paragraph}
        </p>
      ));

  const renderRentVsBuySummary = (result: RentVsBuyResult) => {
    const response: RentVsBuyResponse = result.response ?? {};
    const inputs = result.inputs ?? {};
    const location =
      typeof response.location === "string" && response.location.trim()
        ? response.location
        : "Unknown";

    const equityProjection = Array.isArray(response.equity_projection)
      ? response.equity_projection
      : [];

    const affordabilityScore = formatPercent(response.affordability_score);
    const recommendation =
      typeof response.recommendation === "string"
        ? response.recommendation
        : undefined;
    const recommendationLower = recommendation?.toLowerCase();
    const recommendationVerb =
      recommendationLower === "buy"
        ? "buying"
        : recommendationLower === "rent"
        ? "renting"
        : undefined;
    const affordabilityText =
      response.affordable === undefined
        ? undefined
        : response.affordable
        ? "affordable"
        : "not affordable";
    const budgetText = inputs.budget ? formatCurrency(inputs.budget) : undefined;
    const incomeText = inputs.income ? formatCurrency(inputs.income) : undefined;
    const inputLine = [budgetText && `budget of ${budgetText}`, incomeText && `monthly income of ${incomeText}`]
      .filter(Boolean)
      .join(" and ");
    const buyCost =
      formatCurrency(response.total_monthly_cost_buying) ??
      formatCurrency(response.monthly_mortgage);
    const rentCost =
      formatCurrency(response.total_monthly_cost_renting) ??
      formatCurrency(response.average_rent);
    const costLine =
      buyCost && rentCost
        ? `Buying runs about ${buyCost} per month, while renting is around ${rentCost}.`
        : buyCost
        ? `Estimated monthly buying cost is around ${buyCost}.`
        : rentCost
        ? `Estimated monthly rent is around ${rentCost}.`
        : null;

    const summaryLines = [
      recommendationVerb
        ? `Based on ${inputLine ? `your ${inputLine}` : "current pricing"} in ${location}, ${recommendationVerb} makes more financial sense right now.`
        : `Here is a quick rent vs buy read for ${location}.`,
      costLine,
      affordabilityText || affordabilityScore
        ? `Affordability looks ${affordabilityText ?? "unclear"}${affordabilityScore ? ` (score ${affordabilityScore})` : ""}.`
        : null,
      recommendation
        ? `Recommendation: ${recommendation}.`
        : null,
    ].filter(Boolean);

    const summaryText = summaryLines.length
      ? summaryLines.join(" ")
      : "Here is a quick rent vs buy summary based on the latest data.";

    const cardFields = [
      {
        label: "Average home price",
        value: formatCurrency(response.average_home_price) ?? "-",
      },
      {
        label: "Monthly mortgage",
        value: formatCurrency(response.monthly_mortgage) ?? "-",
      },
      {
        label: "Rent cost",
        value:
          formatCurrency(response.average_rent) ??
          formatCurrency(response.total_monthly_cost_renting) ??
          "-",
      },
      {
        label: "Affordability",
        value:
          response.affordable === undefined
            ? "-"
            : response.affordable
            ? "Yes"
            : "No",
      },
      {
        label: "Recommendation",
        value: recommendation ?? "-",
      },
    ];

    const comparisonData = [
      {
        label: "Buying",
        cost:
          response.total_monthly_cost_buying ??
          response.monthly_mortgage ??
          0,
      },
      {
        label: "Renting",
        cost:
          response.total_monthly_cost_renting ??
          response.average_rent ??
          0,
      },
    ];

    const equityData = equityProjection.map((entry) => ({
      year: entry.year ?? "-",
      equity: typeof entry.equity === "number" ? entry.equity : 0,
    }));

    return (
      <div className="space-y-4">
        <div className="max-w-3xl rounded-2xl border bg-card px-4 py-3 text-sm">
          {renderParagraphs(summaryText)}
        </div>
        <div className="rounded-2xl border bg-card p-5 space-y-4 max-w-3xl">
          <div className="space-y-1">
            <p className="text-xs uppercase tracking-wide text-muted-foreground">
              Rent vs Buy Summary
            </p>
            <h2 className="text-xl font-semibold">{location}</h2>
          </div>
          <div className="space-y-2">
            {cardFields.map((item) => (
              <div key={item.label} className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">{item.label}</span>
                <span className="font-semibold">{item.value}</span>
              </div>
            ))}
          </div>

          <div className="space-y-2">
            <p className="text-sm font-semibold">Monthly cost comparison</p>
            <ChartContainer
              className="h-48 w-full"
              config={{
                cost: { label: "Monthly cost", color: "hsl(var(--primary))" },
              }}
            >
              <BarChart data={comparisonData}>
                <CartesianGrid vertical={false} />
                <XAxis dataKey="label" tickLine={false} axisLine={false} />
                <YAxis
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(value) =>
                    typeof value === "number"
                      ? `$${Math.round(value / 1000)}k`
                      : `${value}`
                  }
                />
                <ChartTooltip
                  content={
                    <ChartTooltipContent
                      formatter={(value) =>
                        typeof value === "number"
                          ? formatCurrency(value) ?? value.toString()
                          : value
                      }
                    />
                  }
                />
                <Bar dataKey="cost" fill="var(--color-cost)" radius={8} />
              </BarChart>
            </ChartContainer>
          </div>
          {equityProjection.length > 0 && (
            <details className="rounded-xl border bg-muted/40 px-4 py-3">
              <summary className="cursor-pointer text-sm font-semibold">
                Equity projection
              </summary>
              <div className="mt-3 space-y-3">
                <ChartContainer
                  className="h-52 w-full"
                  config={{
                    equity: { label: "Equity", color: "hsl(var(--foreground))" },
                  }}
                >
                  <LineChart data={equityData}>
                    <CartesianGrid vertical={false} />
                    <XAxis dataKey="year" tickLine={false} axisLine={false} />
                    <YAxis
                      tickLine={false}
                      axisLine={false}
                      tickFormatter={(value) =>
                        typeof value === "number"
                          ? `$${Math.round(value / 1000)}k`
                          : `${value}`
                      }
                    />
                    <ChartTooltip
                      content={
                        <ChartTooltipContent
                          formatter={(value) =>
                            typeof value === "number"
                              ? formatCurrency(value) ?? value.toString()
                              : value
                          }
                        />
                      }
                    />
                    <ChartLegend content={<ChartLegendContent />} />
                    <Line
                      type="monotone"
                      dataKey="equity"
                      stroke="var(--color-equity)"
                      strokeWidth={3}
                      dot={false}
                    />
                  </LineChart>
                </ChartContainer>
                <ul className="space-y-1 text-sm text-muted-foreground">
                  {equityProjection.map((entry, index) => (
                    <li key={`${entry.year ?? "year"}-${index}`}>
                      Year {entry.year ?? "-"}: {formatCurrency(entry.equity) ?? entry.equity ?? "-"}
                    </li>
                  ))}
                </ul>
              </div>
            </details>
          )}
        </div>
      </div>
    );
  };

  const renderPropertyCards = (result: SearchResult) => {
    if (result.properties.length === 0) {
      return (
        <div className="rounded-2xl border bg-card p-4 text-sm text-muted-foreground">
          I could not find any listings that match that request yet. Try a different city, zip, or property type.
        </div>
      );
    }

    return (
      <div className="space-y-6">
        {result.properties.slice(0, 10).map((property, index) => {
          const details = property as Property & PropertyExtras;
          const photos = Array.isArray(details.photos) ? details.photos : [];
          const stripImages = photos
            .map((photo) => {
              if (typeof photo === "string") return photo;
              return photo?.midRes ?? photo?.lowRes ?? photo?.highRes ?? "";
            })
            .filter(Boolean);
          const lightboxImages = photos
            .map((photo) => {
              if (typeof photo === "string") return photo;
              return photo?.highRes ?? photo?.midRes ?? photo?.lowRes ?? "";
            })
            .filter(Boolean);
          const images =
            stripImages.length > 0
              ? stripImages
              : lightboxImages.length > 0
              ? lightboxImages
              : property.image
              ? [property.image]
              : [];

          return (
            <div
              key={`${property.id}-${index}`}
              className="space-y-4 rounded-2xl border p-4 bg-card"
            >
              {images.length > 0 && (
                <div className="rounded-xl border bg-muted">
                  <div className="flex gap-3 overflow-x-auto snap-x snap-mandatory scroll-smooth pb-2">
                    {images.map((url, photoIndex) => (
                      <div
                        key={`${property.id}-photo-${photoIndex}`}
                        className="w-64 shrink-0 aspect-video snap-start rounded-lg overflow-hidden bg-muted"
                      >
                        <img
                          src={url}
                          alt={property.address || "Property"}
                          className="h-full w-full object-cover cursor-pointer"
                          loading="lazy"
                          onClick={() =>
                            setLightboxProperty({
                              ...property,
                              images:
                                lightboxImages.length > 0 ? lightboxImages : images,
                            })
                          }
                        />
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="space-y-1 text-sm">
                {property.price && (
                  <div>
                    <span className="font-semibold">Price:</span> {property.price}
                  </div>
                )}
                {property.address && (
                  <div>
                    <span className="font-semibold">Address:</span> {property.address}
                  </div>
                )}
                {(property.beds !== undefined || property.baths !== undefined) && (
                  <div>
                    <span className="font-semibold">Beds / Baths:</span>{" "}
                    {formatBedsBaths(property.beds, property.baths)}
                  </div>
                )}
                {details.description && (
                  <div>
                    <span className="font-semibold">Description:</span>{" "}
                    {truncateText(details.description)}
                  </div>
                )}
                {details.url && (
                  <div>
                    <a
                      href={details.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary underline"
                    >
                      View Listing
                    </a>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  const handleNewChat = () => {
    setActiveThreadId(null);
    setIsSearching(false);
    setRentVsBuyDraft(null);
    setRentVsBuyMissing([]);
    setLastRentVsBuyPrompt(null);
  };

  const handleSelectChat = (id: string) => {
    setActiveThreadId(id);
    setIsSearching(false);
    setRentVsBuyDraft(null);
    setRentVsBuyMissing([]);
    setLastRentVsBuyPrompt(null);
  };

  const handleDeleteChat = (id: string) => {
    setThreads((prev) => prev.filter((thread) => thread.id !== id));
    if (activeThreadId === id) {
      setActiveThreadId(null);
      setRentVsBuyDraft(null);
      setRentVsBuyMissing([]);
      setLastRentVsBuyPrompt(null);
    }
  };

  const chatHistory = [...threads]
    .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
    .map((thread) => ({
      id: thread.id,
      title: thread.title,
      timestamp: thread.timestamp,
    }));

  const isEmptyState = messages.length === 0;

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar
        chatHistory={chatHistory}
        activeChat={activeThreadId}
        isCollapsed={isSidebarCollapsed}
        onToggle={() => setIsSidebarCollapsed((prev) => !prev)}
        onSelectChat={handleSelectChat}
        onNewChat={handleNewChat}
        onDeleteChat={handleDeleteChat}
      />
      <main className="flex-1 flex flex-col overflow-hidden">
        {isEmptyState ? (
          <div className="flex-1 flex flex-col items-center justify-center px-6 py-12">
            <div className="w-full max-w-4xl space-y-10 flex flex-col items-center">
              <HeroSection />
              <SearchSection onSubmit={handleSearch} />
            </div>
          </div>
        ) : (
          <div className="flex-1 flex flex-col overflow-hidden">
            <div className="flex-1 overflow-y-auto px-6 py-8">
              <div className="space-y-6 max-w-4xl mx-auto">
                {messages.map((message) => {
                  if (message.role === "user") {
                    return (
                      <div key={message.id} className="flex justify-end">
                        <div className="max-w-[80%] rounded-2xl bg-primary px-4 py-3 text-sm text-primary-foreground shadow">
                          {message.text}
                        </div>
                      </div>
                    );
                  }

                  if (message.type === "property" && message.result) {
                    const result = message.result as SearchResult;
                    return (
                      <div key={message.id} className="space-y-4">
                        {message.text ? (
                          <div className="max-w-3xl rounded-2xl border bg-card px-4 py-3 text-sm">
                            {renderParagraphs(message.text)}
                          </div>
                        ) : null}
                        {renderPropertyCards(result)}
                      </div>
                    );
                  }

                  if (message.type === "rent-vs-buy" && message.result) {
                    return (
                      <div key={message.id} className="flex justify-start w-full">
                        {renderRentVsBuySummary(message.result as RentVsBuyResult)}
                      </div>
                    );
                  }

                  return (
                    <div key={message.id} className="flex justify-start">
                      <div className="max-w-[80%] rounded-2xl border bg-card px-4 py-3 text-sm">
                        {message.text ? renderParagraphs(message.text) : null}
                      </div>
                    </div>
                  );
                })}

                {isSearching && <LoadingState />}
              </div>
            </div>

            <div className="border-t py-4">
              <div className="max-w-4xl mx-auto px-6">
                <SearchSection
                  onSubmit={handleSearch}
                  shouldAnimatePlaceholder={false}
                  showSuggestions={false}
                />
              </div>
            </div>
          </div>
        )}
      </main>

      <ImageLightbox
        property={lightboxProperty}
        onClose={() => setLightboxProperty(null)}
      />
    </div>
  );
};

export default Index;
