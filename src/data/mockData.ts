export interface Property {
  id: string;
  image: string;
  source: string;
  sourceColor: string;
  price?: string;
  address?: string;
  beds?: number;
  baths?: number;
}

export interface SearchResult {
  query: string;
  sourcesCount: number;
  followUps: string[];
  properties: Property[];
  summary: string;
  timestamp: Date;
}

export interface ChatHistoryItem {
  id: string;
  query: string;
  timestamp: Date;
  result: SearchResult;
}

export const suggestedQuestions = [
  { icon: "eye", text: "What should I look out for?" },
  { icon: "users", text: "Will I like my neighbors?" },
  { icon: "heart", text: "Can I raise a family here?" },
  { icon: "home", text: "What's the home worth?" },
  { icon: "trending", text: "How's the market trending?" },
  { icon: "shield", text: "Is this neighborhood safe?" },
];

export const mockProperties: Property[] = [
  {
    id: "1",
    image: "https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=800&h=600&fit=crop",
    source: "Zillow",
    sourceColor: "#006AFF",
    price: "$2,450,000",
    address: "123 Ocean View Dr, Malibu",
    beds: 4,
    baths: 3,
  },
  {
    id: "2",
    image: "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&h=600&fit=crop",
    source: "Redfin",
    sourceColor: "#A02021",
    price: "$1,875,000",
    address: "456 Sunset Blvd, Beverly Hills",
    beds: 5,
    baths: 4,
  },
  {
    id: "3",
    image: "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&h=600&fit=crop",
    source: "Realtor",
    sourceColor: "#D92228",
    price: "$1,875,000",
    address: "789 Palm Avenue, Santa Monica",
    beds: 4,
    baths: 3,
  },
  {
    id: "4",
    image: "https://images.unsplash.com/photo-1605276374104-dee2a0ed3cd6?w=800&h=600&fit=crop",
    source: "Sotheby's",
    sourceColor: "#1a1a1a",
    price: "$3,200,000",
    address: "321 Mountain View, Bel Air",
    beds: 6,
    baths: 5,
  },
];

export const getMockResponse = (query: string): SearchResult => {
  return {
    query,
    sourcesCount: 4,
    followUps: [
      "What's the price trend in this area?",
      "Show me homes with pools",
      "Compare school districts",
      "What are the HOA fees?",
    ],
    properties: mockProperties,
    summary: `Based on your search, I found several exceptional properties in prime California locations. The current market shows strong demand for luxury homes with modern amenities. Beverly Hills and Malibu remain the most sought-after areas, with average home prices ranging from $2M to $8M. Properties with ocean views or hillside locations command premium prices, often selling within 30 days of listing.`,
    timestamp: new Date(),
  };
};
