import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";

import Sidebar from "@/components/Sidebar";
import HeroSection from "@/components/HeroSection";
import SearchSection from "@/components/SearchBar";

import PropertyCarousel from "@/components/PropertyCarousel";
import ImageLightbox from "@/components/ImageLightbox";
import LoadingState from "@/components/LoadingState";

import {
  ChatHistoryItem,
  SearchResult,
  Property,
  getMockResponse,
} from "@/data/mockData";

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

    const result = getMockResponse(query);
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

                      <PropertyCarousel
                        properties={currentResult.properties}
                        onPropertyClick={setLightboxProperty}
                      />

                      <p>{currentResult.summary}</p>
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
