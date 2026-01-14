import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";

import Sidebar from "@/components/Sidebar";
import HeroSection from "@/components/HeroSection";
import SearchSection from "@/components/SearchBar";

import ImageLightbox from "@/components/ImageLightbox";
import LoadingState from "@/components/LoadingState";

import { searchProperties } from "@/lib/api";

import {
  ChatHistoryItem,
  SearchResult,
  Property,
} from "@/data/mockData";

const formatPrice = (value: any): string | undefined => {
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

const formatAddress = (item: any): string | undefined => {
  if (item?.addressUnparsedAddress) return item.addressUnparsedAddress;
  if (typeof item?.address === "string") return item.address;

  const addressObj = item?.address;
  if (addressObj && typeof addressObj === "object") {
    const parts = [
      addressObj.street,
      addressObj.city,
      addressObj.state,
      addressObj.postal_code ?? addressObj.postalCode ?? addressObj.zip,
    ].filter(Boolean);
    if (parts.length) return parts.join(", ");
  }

  const parts = [item?.city, item?.state].filter(Boolean);

  return parts.length ? parts.join(", ") : undefined;
};

const parseNumber = (value: any): number | undefined => {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric : undefined;
};

const formatBedsBaths = (beds?: number, baths?: number) => {
  const parts: string[] = [];
  if (beds !== undefined) parts.push(`${beds} beds`);
  if (baths !== undefined) parts.push(`${baths} baths`);
  return parts.join(" / ");
};

type PropertyExtras = {
  photos?: string[];
  livingArea?: number;
  score?: number;
  description?: string;
  url?: string;
};

const extractPhotos = (item: any): string[] => {
  const list =
    item?.photos ??
    item?._raw_listing?.media?.photosList ??
    [];

  if (Array.isArray(list)) {
    return list
      .map((photo) => photo?.highRes || photo?.midRes || photo?.url)
      .filter(Boolean);
  }

  return item?.image_url ? [item.image_url] : [];
};

const mapApiResponseToSearchResult = (
  query: string,
  data: any
): SearchResult => {
  const rawProperties = Array.isArray(data?.properties)
    ? data.properties
    : Array.isArray(data?.results)
    ? data.results
    : Array.isArray(data?.listings)
    ? data.listings
    : [];

  const mappedProperties: Property[] = rawProperties.map((item: any, index: number) => {
    const photos = extractPhotos(item);
    return {
    id: String(
      item?.id ??
        item?.listing_id ??
        item?.property_id ??
        item?._id ??
        `${query}-${index}`
    ),
    image: photos[0] ?? item?.image_url ?? "",
    source: item?.source ?? item?.provider ?? item?.site ?? "Listing",
    sourceColor: item?.sourceColor ?? item?.source_color ?? "#0f172a",
    price: formatPrice(item?.list_price ?? item?.price),
    address: formatAddress(item) ?? item?.full_address ?? item?.location?.address,
    beds: parseNumber(item?.propertyBedroomTotal ?? item?.beds ?? item?.bedrooms),
    baths: parseNumber(item?.propertyBathroomTotal ?? item?.baths ?? item?.bathrooms),
    photos,
    livingArea: parseNumber(item?.living_area ?? item?.propertyLivingArea),
    score: typeof item?.score === "number" ? item.score : undefined,
    description: item?.publicRemark ?? item?.remarks,
    url: item?.url,
  };
  });

  const limitedProperties = mappedProperties.slice(0, 10);

  const followUps = Array.isArray(data?.followUps)
    ? data.followUps
    : Array.isArray(data?.follow_ups)
    ? data.follow_ups
    : Array.isArray(data?.followups)
    ? data.followups
    : [];

  const timestampValue = data?.timestamp ? new Date(data.timestamp) : new Date();
  const timestamp = Number.isNaN(timestampValue.getTime())
    ? new Date()
    : timestampValue;

  return {
    query: data?.query ?? query,
    sourcesCount:
      data?.sourcesCount ?? data?.sources_count ?? limitedProperties.length,
    followUps,
    properties: limitedProperties,
    summary: data?.summary ?? data?.answer ?? data?.message ?? "",
    timestamp,
  };
};

const Index = () => {
  const [chatHistory, setChatHistory] = useState<ChatHistoryItem[]>([]);
  const [currentResult, setCurrentResult] = useState<SearchResult | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [lightboxProperty, setLightboxProperty] = useState<Property | null>(null);
  const [activeChat, setActiveChat] = useState<string | null>(null);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  const handleSearch = useCallback(async (query: string) => {
    if (!query.trim()) return;

    setIsSearching(true);
    setCurrentResult(null);

    await new Promise((r) => setTimeout(r, 1200));

    const apiResponse = await searchProperties({ query });
    const result = mapApiResponseToSearchResult(query, apiResponse);
    setCurrentResult(result);
    setIsSearching(false);

    const chat: ChatHistoryItem = {
      id: Date.now().toString(),
      query,
      timestamp: new Date(),
      result,
    };

    setChatHistory((prev) => [chat, ...prev]);
    setActiveChat(chat.id);
  }, []);

  const handleNewChat = () => {
    setCurrentResult(null);
    setActiveChat(null);
    setIsSearching(false);
  };

  const handleSelectChat = (id: string) => {
    const chat = chatHistory.find((c) => c.id === id);
    if (!chat) return;
    setCurrentResult(chat.result);
    setActiveChat(id);
  };

  const handleDeleteChat = (id: string) => {
    setChatHistory((prev) => prev.filter((c) => c.id !== id));
    if (activeChat === id) {
      setCurrentResult(null);
      setActiveChat(null);
    }
  };

const isEmptyState = !currentResult && !isSearching;
  const luxuryKeywords = [
    "luxury",
    "estate",
    "mansion",
    "architectural",
    "designer",
    "premium",
    "high-end",
  ];
  const isLuxuryQuery = /luxury|mansion|estate|high-end/i.test(
    currentResult?.query ?? ""
  );
  const luxuryAreas = ["beverly hills", "bel air", "malibu", "palo alto"];
  const filteredProperties = currentResult
    ? currentResult.properties
        .filter((property) => {
          if (!isLuxuryQuery) return true;
          const price = Number(property.price?.replace(/[^0-9]/g, ""));
          const desc = (property.description || "").toLowerCase();
          const address = (property.address || "").toLowerCase();
          const livingArea = (property as Property & PropertyExtras).livingArea;
          const matchesKeyword = luxuryKeywords.some((keyword) =>
            desc.includes(keyword)
          );
          const matchesArea = luxuryAreas.some((area) => address.includes(area));
          const matchesLivingArea =
            Number.isFinite(livingArea) && livingArea >= 4000;
          return (
            (Number.isFinite(price) && price >= 2000000) ||
            matchesKeyword ||
            matchesArea ||
            matchesLivingArea
          );
        })
        .sort((a, b) => {
          const scoreA = (a as Property & PropertyExtras).score ?? 0;
          const scoreB = (b as Property & PropertyExtras).score ?? 0;
          if (scoreA !== scoreB) return scoreB - scoreA;
          const pa = Number(a.price?.replace(/[^0-9]/g, ""));
          const pb = Number(b.price?.replace(/[^0-9]/g, ""));
          return (Number.isFinite(pb) ? pb : 0) - (Number.isFinite(pa) ? pa : 0);
        })
    : [];

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar
        chatHistory={chatHistory}
        activeChat={activeChat}
        isCollapsed={isSidebarCollapsed}
        onToggle={() => setIsSidebarCollapsed((p) => !p)}
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
              <AnimatePresence mode="wait">
                {isSearching ? (
                  <LoadingState />
                ) : (
                  currentResult && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="space-y-6 max-w-4xl mx-auto"
                    >
                      <h1 className="text-3xl">{currentResult.query}</h1>
                      {(currentResult as any)?.data_source && (
                        <p className="text-xs text-muted-foreground">
                          Data source: {(currentResult as any).data_source}
                        </p>
                      )}

                      <div className="space-y-8">
                        {filteredProperties.slice(0, 10).map((property, index) => {
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
                                <div className="relative overflow-x-auto">
                                  <div className="flex gap-4 snap-x snap-mandatory">
                                    {images.map((url, photoIndex) => (
                                      <div
                                        key={`${property.id}-photo-${photoIndex}`}
                                        className="w-[384px] h-[224px] flex-shrink-0 snap-start rounded-xl overflow-hidden bg-muted"
                                      >
                                        <img
                                          src={url}
                                          alt={property.address || "Property"}
                                          className="w-full h-full object-cover cursor-pointer"
                                          loading="lazy"
                                          onClick={() =>
                                            setLightboxProperty({
                                              ...property,
                                              images: lightboxImages.length > 0 ? lightboxImages : images,
                                            } as any)
                                          }
                                        />
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              )}

                              <div className="space-y-1">
                                {property.price && (
                                  <div>
                                    <span className="font-semibold">Price:</span>{" "}
                                    {property.price}
                                  </div>
                                )}
                                {property.address && (
                                  <div>
                                    <span className="font-semibold">Address:</span>{" "}
                                    {property.address}
                                  </div>
                                )}
                                {(property.beds !== undefined || property.baths !== undefined) && (
                                  <div>
                                    <span className="font-semibold">Bedrooms / Bathrooms:</span>{" "}
                                    {formatBedsBaths(property.beds, property.baths)}
                                  </div>
                                )}
                                {details.description && (
                                  <div>
                                    <span className="font-semibold">Description:</span>{" "}
                                    {details.description}
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
                    </motion.div>
                  )
                )}
              </AnimatePresence>
            </div>

            {/* Bottom slim search bar */}
            <div className="border-t py-4">
              <div className="max-w-4xl mx-auto px-6">
                <SearchSection
                  onSubmit={handleSearch}
                  shouldAnimatePlaceholder={false}
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


