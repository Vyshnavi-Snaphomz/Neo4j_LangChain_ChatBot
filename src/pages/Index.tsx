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
  "financial comparison",
  "mortgage vs rent",
  "compare renting and buying",
  "affordability",
  "budget",
  "income",
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
  "what is",
  "how does",
  "mortgage",
  "hoa",
  "escrow",
  "pmi",
  "closing costs",
  "down payment",
  "appraisal",
  "inspection",
  "interest rate",
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

  const fullAddress =
    getString(item.full_address) ||
    getString(item.fullAddress) ||
    getString(item.unparsedAddress);
  if (fullAddress) return fullAddress;

  const addressString = getString(item.address_string) || getString(item.address);
  if (addressString && typeof item.address === "string") return addressString;

  const location = isRecord(item.location) ? item.location : null;
  const addressObj = isRecord(item.address)
    ? item.address
    : location && isRecord(location)
      ? location
      : null;

  if (addressObj) {
    const parts = [
      getString(addressObj.street) || getString(addressObj.streetAddress) || getString(addressObj.line1),
      getString(addressObj.city),
      getString(addressObj.state) || getString(addressObj.stateCode) || getString(addressObj.state_code),
      getString(
        addressObj.postal_code ??
        addressObj.postalCode ??
        addressObj.zip ??
        addressObj.zipCode
      ),
    ].filter(Boolean) as string[];

    if (parts.length) return parts.join(", ");
    if (getString(addressObj.address)) return getString(addressObj.address);
  }

  const parts = [
    getString(item.city),
    getString(item.state) || getString(item.stateCode) || getString(item.state_code),
  ].filter(Boolean) as string[];

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

// 🔧 IMPROVED: Extract budget from anywhere in the text
const extractBudget = (query: string): number | null => {
  const normalized = query.toLowerCase();

  // Look for explicit budget mentions
  const budgetMatch = query.match(/\b(?:budget|price|cost|afford)(?:\s+is|\s+of)?\s*\$?([\d,]+)\s?(k|m)?/i);
  if (budgetMatch) {
    return parseMoneyValue(budgetMatch[0]);
  }

  // If "income" is mentioned, skip budget extraction to avoid confusion
  if (/\bincome\b/i.test(normalized)) {
    // Only extract if there are TWO money values (one for budget, one for income)
    const moneyMatches = query.match(/\$?([\d,]+)\s?(k|m)?/gi);
    if (moneyMatches && moneyMatches.length >= 2) {
      // First value is likely budget
      return parseMoneyValue(moneyMatches[0]);
    }
    return null;
  }

  // Look for any money value with budget keywords
  const hasBudgetCue = /\b(budget|price|cost|with|under|over|around)\b/i.test(normalized);
  if (hasBudgetCue) {
    return parseMoneyValue(query);
  }

  return null;
};

// 🔧 IMPROVED: Extract location/state from natural language
const extractLocation = (query: string): string | null => {
  const normalized = query.toLowerCase();

  // US State mapping (Input -> Full Name)
  const stateMap: Record<string, string> = {
    'california': 'California', 'ca': 'California',
    'texas': 'Texas', 'tx': 'Texas',
    'florida': 'Florida', 'fl': 'Florida',
    'new york': 'New York', 'ny': 'New York',
    'illinois': 'Illinois', 'il': 'Illinois',
    'pennsylvania': 'Pennsylvania', 'pa': 'Pennsylvania',
    'ohio': 'Ohio', 'oh': 'Ohio',
    'georgia': 'Georgia', 'ga': 'Georgia',
    'north carolina': 'North Carolina', 'nc': 'North Carolina',
    'michigan': 'Michigan', 'mi': 'Michigan',
    'arizona': 'Arizona', 'az': 'Arizona',
    'washington': 'Washington', 'wa': 'Washington',
    'colorado': 'Colorado', 'co': 'Colorado',
    'oregon': 'Oregon', 'or': 'Oregon',
    'nevada': 'Nevada', 'nv': 'Nevada',
  };

  // Look for "I live in [state]" or "in [state]"
  const liveInMatch = query.match(/\b(?:i\s+live\s+in|in|at|near|around)\s+([a-zA-Z\s]+?)(?:\s+(?:my|and|with|budget|income|$))/i);
  if (liveInMatch) {
    const location = liveInMatch[1].trim().toLowerCase();
    console.log('[extractLocation] Matched location:', liveInMatch[1], '→ normalized:', location);
    if (stateMap[location]) {
      console.log('[extractLocation] Found in stateMap:', stateMap[location]);
      return stateMap[location];
    }
    // Return capitalized if not found (e.g. city)
    const capitalized = location.charAt(0).toUpperCase() + location.slice(1);
    console.log('[extractLocation] Not in stateMap, returning as-is:', capitalized);
    return capitalized;
  }

  // Check if any state name appears in the query
  for (const [stateName, stateCode] of Object.entries(stateMap)) {
    if (normalized.includes(stateName)) {
      console.log('[extractLocation] Found state name in query:', stateName, '→', stateCode);
      return stateCode;
    }
  }

  console.log('[extractLocation] No location found');
  return null;
};

const isLikelyLocationReply = (query: string) => {
  const normalized = query.toLowerCase().trim();
  if (/\b(in|at|near|around|live)\b/.test(normalized)) return true;
  if (/\d/.test(normalized)) return false;
  if (/\b(income|budget|mortgage|loan|rate|down payment)\b/.test(normalized))
    return false;
  if (/\b(rent|buy)\b/.test(normalized)) return false;
  return normalized.split(/\s+/).length <= 3;
};

// 🔧 IMPROVED: Extract income from anywhere in the text
const extractIncome = (query: string): number | null => {
  const normalized = query.toLowerCase();

  // Look for explicit income mentions
  const incomeMatch = query.match(/\b(?:monthly\s+)?income(?:\s+is|\s+of)?\s*\$?([\d,]+)\s?(k|m)?/i);
  if (incomeMatch) {
    return parseMoneyValue(incomeMatch[0]);
  }

  // If "income" keyword exists, try to find the associated number
  if (/\bincome\b/i.test(normalized)) {
    // Look for number after "income"
    const afterIncomeMatch = query.match(/\bincome\b[^0-9$%]*\$?([\d,]+)\s?(k|m)?/i);
    if (afterIncomeMatch) {
      return parseMoneyValue(afterIncomeMatch[0]);
    }

    // If there are multiple money values, the last one is likely income
    const moneyMatches = query.match(/\$?([\d,]+)\s?(k|m)?/gi);
    if (moneyMatches && moneyMatches.length >= 2) {
      return parseMoneyValue(moneyMatches[moneyMatches.length - 1]);
    }

    // Single money value with "income" keyword
    if (moneyMatches && moneyMatches.length === 1) {
      return parseMoneyValue(moneyMatches[0]);
    }
  }

  return null;
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

  if (Array.isArray(record.photos) && record.photos.length > 0) {
    return record.photos.filter((p) => typeof p === "string") as string[];
  }

  const imageUrl =
    getString(record.image_url) ??
    getString(record.imageUrl) ??
    getString(record.image) ??
    getString(record.primaryImageUrl);

  return imageUrl ? [imageUrl] : [];
};

const mapApiResponseToSearchResult = (
  query: string,
  data: unknown
): SearchResult => {
  // Single Source of Truth for extraction (checking top-level and common wrappers)
  const getRawProperties = (val: unknown): unknown[] => {
    if (Array.isArray(val)) return val;
    if (!isRecord(val)) return [];
    if (Array.isArray(val.properties)) return val.properties;
    if (Array.isArray(val.listings)) return val.listings;
    if (Array.isArray(val.results)) return val.results;

    // Check nested wrappers
    const nested = isRecord(val.data) ? val.data : isRecord(val.result) ? val.result : null;
    if (nested) {
      if (Array.isArray(nested.properties)) return nested.properties;
      if (Array.isArray(nested.listings)) return nested.listings;
      if (Array.isArray(nested.results)) return nested.results;
    }
    return [];
  };

  const rawProperties = getRawProperties(data);

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
          itemRecord.zpid ??
          itemRecord._id ??
          `${query}-${index}`
        ),
        image:
          photos[0] ??
          getString(itemRecord.image_url) ??
          getString(itemRecord.primaryImageUrl) ??
          getString(itemRecord.imageUrl) ??
          getString(itemRecord.image) ??
          "",
        source:
          getString(itemRecord.source) ??
          getString(itemRecord.provider) ??
          getString(itemRecord.site) ??
          getString(itemRecord.attribution) ??
          "Listing",
        sourceColor:
          getString(itemRecord.sourceColor) ??
          getString(itemRecord.source_color) ??
          "#0f172a",
        price: formatPrice(
          itemRecord.list_price ??
          itemRecord.price ??
          itemRecord.amount ??
          itemRecord.asking_price ??
          itemRecord.listPrice ??
          itemRecord.cost
        ),
        address:
          formatAddress(itemRecord) ??
          getString(itemRecord.full_address) ??
          getString(itemRecord.address_string) ??
          getString(itemRecord.streetAddress) ??
          getString(location?.full_address) ??
          getString(location?.address),
        beds: parseNumber(
          itemRecord.propertyBedroomTotal ??
          itemRecord.beds ??
          itemRecord.bedrooms ??
          itemRecord.bed ??
          itemRecord.br
        ),
        baths: parseNumber(
          itemRecord.propertyBathroomTotal ??
          itemRecord.baths ??
          itemRecord.bathrooms ??
          itemRecord.bath ??
          itemRecord.ba
        ),
        photos,
        livingArea: parseNumber(
          itemRecord.living_area ??
          itemRecord.propertyLivingArea ??
          itemRecord.sqft ??
          itemRecord.square_feet ??
          itemRecord.lotSize ??
          itemRecord.area
        ),
        yearBuilt: parseNumber(
          itemRecord.year_built ??
          itemRecord.yearBuilt ??
          itemRecord.year
        ),
        lotSize: getString(itemRecord.lot_size ?? itemRecord.lotSize) ??
          (typeof itemRecord.lotSize === 'number' ? `${itemRecord.lotSize} sqft` : undefined),
        propertyType: getString(
          itemRecord.prop_type ??
          itemRecord.propertyType ??
          itemRecord.property_type ??
          itemRecord.type
        ),
        status: getString(
          itemRecord.status ??
          itemRecord.listingStatus ??
          itemRecord.listing_status
        ),
        score:
          typeof itemRecord.score === "number"
            ? itemRecord.score
            : typeof itemRecord.relevance_score === "number"
              ? itemRecord.relevance_score
              : undefined,
        description:
          getString(itemRecord.publicRemark) ??
          getString(itemRecord.remarks) ??
          getString(itemRecord.description) ??
          getString(itemRecord.summary),
        url:
          getString(itemRecord.url) ??
          getString(itemRecord.link) ??
          getString(itemRecord.listing_url),
      };
    }
  );

  const limitedProperties = mappedProperties.slice(0, 10);
  const record = isRecord(data) ? data : {};
  const metadata = isRecord(record.metadata) ? record.metadata : null;
  const apiQuery = query;

  const summary =
    getString(record.summary) ??
    getString(record.answer) ??
    getString(record.message) ??
    getString(metadata?.summary) ??
    getString(isRecord(record.data) ? record.data.summary : undefined) ??
    getString(isRecord(record.result) ? record.result.summary : undefined) ??
    getString(isRecord(record.data) ? record.data.answer : undefined) ??
    getString(isRecord(record.result) ? record.result.answer : undefined) ??
    getString(isRecord(record.data) ? record.data.message : undefined) ??
    getString(isRecord(record.result) ? record.result.message : undefined) ??
    "";

  return {
    type: "search",
    query: apiQuery,
    sourcesCount:
      (typeof record.sourcesCount === "number" ? record.sourcesCount : undefined) ??
      (typeof record.sources_count === "number" ? record.sources_count : undefined) ??
      (typeof metadata?.total_results === "number" ? metadata?.total_results : undefined) ??
      limitedProperties.length,
    followUps: [],
    properties: limitedProperties,
    summary,
    timestamp: new Date(),
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

  // Restore chat history on mount
  useEffect(() => {
    try {
      const savedThreads = localStorage.getItem("chat_history");
      const savedActiveId = localStorage.getItem("active_thread_id");

      if (savedThreads) {
        const parsedThreads = JSON.parse(savedThreads);
        if (Array.isArray(parsedThreads)) {
          const restoredThreads = parsedThreads.map((t: any) => ({
            ...t,
            timestamp: new Date(t.timestamp),
            messages: t.messages || []
          }));
          setThreads(restoredThreads);
        }
      }

      if (savedActiveId) {
        setActiveThreadId(savedActiveId);
      }
    } catch (e) {
      console.error("Failed to restore chat history", e);
    }
  }, []);

  // Save chat history on update
  useEffect(() => {
    if (threads.length > 0) {
      localStorage.setItem("chat_history", JSON.stringify(threads));
    }
    if (activeThreadId) {
      localStorage.setItem("active_thread_id", activeThreadId);
    }
  }, [threads, activeThreadId]);

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
    // 1. Extract values from current query
    const extractedIncome = extractIncome(query);
    const extractedBudget = extractBudget(query);
    const extractedLocation = extractLocation(query);
    const extractedDownPayment = extractDownPayment(query);
    const extractedLoanTerm = extractLoanTerm(query);
    const extractedMortgageRate = extractMortgageRate(query);
    const numericValue = isNumericOnlyQuery(query) ? parseMoneyValue(query) : null;

    // 2. Start with existing draft or initialize new
    const base: RentVsBuyDraft = existingDraft
      ? { ...existingDraft }
      : { query };

    // 3. Correctly merge new values (only if found)
    // ✅ This fixes the bug where state was being reset because we weren't spreading previous state
    if (extractedLocation) base.location = extractedLocation;
    if (extractedBudget !== null) base.budget = extractedBudget;
    if (extractedIncome !== null) base.income = extractedIncome;
    if (extractedDownPayment !== null) base.down_payment = extractedDownPayment;
    if (extractedLoanTerm !== null) base.loan_term = extractedLoanTerm;
    if (extractedMortgageRate !== null) base.mortgage_rate = extractedMortgageRate;

    // 4. Handle numeric shortcuts for context (e.g. user just types "5000")
    if (numericValue !== null) {
      if (missingFields.includes("income") && extractedIncome === null) {
        base.income = numericValue;
      } else if (missingFields.includes("budget") && extractedBudget === null) {
        base.budget = numericValue;
      } else if (base.income === undefined && base.budget !== undefined) {
        // Ambiguous number, assume missing field
        base.income = numericValue;
      } else if (base.budget === undefined && base.income !== undefined) {
        base.budget = numericValue;
      } else if (base.income === undefined) {
        base.income = numericValue;
      }
    }

    // 🔧 Log extracted values for debugging
    console.log('[RentVsBuy] Updated draft:', {
      query,
      newly_extracted: {
        location: extractedLocation,
        budget: extractedBudget,
        income: extractedIncome
      },
      merged_result: base
    });

    return base;
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
            const messageText = `To compare rent vs buy, I still need your ${readableMissing}.\n\nExtracted so far:\n- State: ${updatedDraft.location || 'not found'}\n- Budget: ${updatedDraft.budget ? `$${updatedDraft.budget.toLocaleString()}` : 'not found'}\n- Income: ${updatedDraft.income ? `$${updatedDraft.income.toLocaleString()}` : 'not found'}`;
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

          // ✅ Send payload with correct field names matching backend contract
          // Validate that we have all required fields before calling API
          if (!updatedDraft.location || !updatedDraft.budget || !updatedDraft.income) {
            console.error('[RentVsBuy] Missing required fields:', {
              location: updatedDraft.location,
              budget: updatedDraft.budget,
              income: updatedDraft.income,
            });
            // This should have been caught by the missingFields check above
            // But adding this as a safety net
            return;
          }

          // Calculate defaults if missing
          const defaultDownPayment = updatedDraft.budget ? updatedDraft.budget * 0.20 : 0;

          const response = await rentVsBuy({
            location: updatedDraft.location, // Full state name (e.g., "California")
            budget: updatedDraft.budget,
            income: updatedDraft.income,
            down_payment: updatedDraft.down_payment ?? defaultDownPayment,
            loan_term: updatedDraft.loan_term ?? 30,
            mortgage_rate: updatedDraft.mortgage_rate ?? 6.5,
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
            id: `${Date.now()
              } - assistant`,
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
            use_cache: true,
          });
          const result = mapApiResponseToSearchResult(trimmed, apiResponse);

          // 🔑 Normalize query for property searches
          if (/show|find|list|houses|homes|properties/i.test(result.query)) {
            const inferredLocation = extractLocation(trimmed);
            if (inferredLocation) {
              result.query = inferredLocation;
            }
          }

          const introText =
            result.properties.length > 0
              ? `Here are ${result.properties.length} homes in ${result.query}.`
              : result.summary || `I could not find any properties in ${result.query}.`;

          appendMessage({
            id: `${Date.now()} - assistant`,
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
          id: `${Date.now()} - assistant`,
          role: "assistant",
          type: "text",
          text: answerText,
        });
      } catch (error) {
        // ✅ Show actual error message from API, not generic fallback
        const errorMessage = error instanceof Error
          ? error.message
          : resolvedIntent === "rent-vs-buy"
            ? "Missing required details to calculate rent vs buy"
            : resolvedIntent === "property"
              ? "Unable to fetch property listings"
              : "Service temporarily unavailable. Please try again.";

        console.error('[Index] Search Error:', error);

        appendMessage({
          id: `${Date.now()} - assistant`,
          role: "assistant",
          type: "text",
          text: errorMessage,
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
        <p key={`${paragraph} - ${index}`} className="text-sm leading-relaxed">
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
                      ? `$${Math.round(value / 1000)} k`
                      : `${value} `
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
                          ? `$${Math.round(value / 1000)} k`
                          : `${value} `
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
                    <li key={`${entry.year ?? "year"} -${index} `}>
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
    if (!result || !result.properties) return null;
    if (result.properties.length === 0) {
      return (
        <div className="rounded-2xl border bg-card p-4 text-sm text-muted-foreground shadow-sm">
          I could not find any listings that match that request yet. Try a different city, zip, or property type.
        </div>
      );
    }

    return (
      <div className="space-y-6">
        {result.properties.slice(0, 10).map((property, index) => {
          const details = property as Property & PropertyExtras;
          const photos = Array.isArray(details.photos) ? details.photos : [];


          // STRICT RULE: Images must come from photos[] or single image property
          const images = photos.length > 0
            ? photos
            : property.image && (property.image.startsWith('http') || property.image.startsWith('/'))
              ? [property.image]
              : [];

          return (
            <div
              key={`${property.id} -${index} `}
              className="space-y-4 rounded-2xl border p-4 bg-card"
            >
              {images.length > 0 && (
                <div className="flex gap-3 overflow-x-auto scrollbar-hide pb-2">
                  {images.map((img, idx) => (
                    <img
                      key={`${property.id}-img-${idx}`}
                      src={img}
                      className="h-48 w-72 flex-shrink-0 rounded-xl object-cover cursor-pointer hover:opacity-95 transition-opacity"
                      alt={`Property image ${idx + 1}`}
                      onClick={() =>
                        setLightboxProperty({
                          ...property,
                          images: images,
                          sqft: (property as any).livingArea,
                          yearBuilt: (property as any).yearBuilt,
                          lotSize: (property as any).lotSize,
                          propertyType: (property as any).propertyType,
                          status: (property as any).status,
                          listingUrl: (property as any).url,
                          description: (property as any).description,
                        } as any)
                      }
                    />
                  ))}
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
        property={lightboxProperty as any}
        onClose={() => setLightboxProperty(null)}
      />
    </div>
  );
};

export default Index;
