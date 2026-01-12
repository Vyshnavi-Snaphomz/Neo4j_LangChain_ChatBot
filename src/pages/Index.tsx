import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Sidebar from "@/components/Sidebar";
import HeroSection from "@/components/HeroSection";
import SearchBar from "@/components/SearchBar";
import FloatingImages from "@/components/FloatingImages";
import FollowUpChips from "@/components/FollowUpChips";
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
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [lightboxProperty, setLightboxProperty] = useState<Property | null>(null);
  const [activeChat, setActiveChat] = useState<string | null>(null);

  const handleSearch = useCallback(async (query: string) => {
    setIsSearching(true);
    setCurrentResult(null);

    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 1500));

    const result = getMockResponse(query);
    setCurrentResult(result);
    setIsSearching(false);

    // Add to history
    const newChat: ChatHistoryItem = {
      id: Date.now().toString(),
      query,
      timestamp: new Date(),
      result,
    };

    setChatHistory((prev) => [newChat, ...prev]);
    setActiveChat(newChat.id);
  }, []);

  const handleNewChat = useCallback(() => {
    setCurrentResult(null);
    setActiveChat(null);
    setIsSearching(false);
  }, []);

  const handleSelectChat = useCallback((id: string) => {
    const chat = chatHistory.find((c) => c.id === id);
    if (chat) {
      setCurrentResult(chat.result);
      setActiveChat(id);
    }
  }, [chatHistory]);

  const handleDeleteChat = useCallback((id: string) => {
    setChatHistory((prev) => prev.filter((c) => c.id !== id));
    if (activeChat === id) {
      setCurrentResult(null);
      setActiveChat(null);
    }
  }, [activeChat]);

  const isEmptyState = !currentResult && !isSearching;

  return (
    <div className="flex min-h-screen bg-background">
      {/* Sidebar */}
      <Sidebar
        isCollapsed={isSidebarCollapsed}
        onToggle={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        chatHistory={chatHistory}
        activeChat={activeChat}
        onSelectChat={handleSelectChat}
        onNewChat={handleNewChat}
        onDeleteChat={handleDeleteChat}
      />

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-h-screen overflow-hidden">
        {isEmptyState ? (
          /* Empty State - Hero with floating images */
          <div className="flex-1 flex flex-col items-center justify-center px-6 py-12 relative">
            {/* Floating Property Images */}
            <FloatingImages />

            <div className="w-full max-w-4xl space-y-8 flex flex-col items-center">
              {/* Hero Section */}
              <HeroSection />

              {/* Search Bar */}
              <SearchBar onSearch={handleSearch} isLoading={isSearching} variant="hero" />
            </div>
          </div>
        ) : (
          /* Results State */
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Scrollable Content */}
            <div className="flex-1 overflow-y-auto px-6 md:px-12 py-8">
              <div className="max-w-4xl">
                <AnimatePresence mode="wait">
                  {isSearching ? (
                    <motion.div
                      key="loading"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                    >
                      <LoadingState />
                    </motion.div>
                  ) : (
                    currentResult && (
                      <motion.div
                        key="results"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="space-y-6"
                      >
                        {/* Query Title */}
                        <motion.h1
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="font-display text-3xl md:text-4xl text-foreground"
                        >
                          {currentResult.query}
                        </motion.h1>

                        {/* Sources Count */}
                        <motion.p
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ delay: 0.1 }}
                          className="text-sm text-muted-foreground"
                        >
                          Reviewed {currentResult.sourcesCount} sources
                        </motion.p>

                        {/* Follow-up Chips */}
                        <FollowUpChips
                          chips={currentResult.followUps}
                          onSelect={handleSearch}
                        />

                        {/* Property Carousel */}
                        <PropertyCarousel
                          properties={currentResult.properties}
                          onPropertyClick={setLightboxProperty}
                        />

                        {/* AI Summary */}
                        <div className="pt-4">
                          <p className="text-foreground text-base md:text-lg leading-relaxed">
                            {currentResult.summary}
                          </p>
                        </div>

                        {/* Divider */}
                        <div className="border-t border-border my-8" />
                      </motion.div>
                    )
                  )}
                </AnimatePresence>
              </div>
            </div>

            {/* Fixed Bottom Search Bar */}
            <div className="border-t border-border bg-background py-4">
              <SearchBar
                onSearch={handleSearch}
                isLoading={isSearching}
                variant="bottom"
                placeholder="Ask a follow-up about this area..."
              />
            </div>
          </div>
        )}

        {/* Footer - Only on empty state */}
        {isEmptyState && (
          <footer className="py-4 text-center z-10 relative">
            <p className="text-xs text-muted-foreground">Powered by Snaphomz AI</p>
          </footer>
        )}
      </main>

      {/* Image Lightbox */}
      <ImageLightbox
        property={lightboxProperty}
        onClose={() => setLightboxProperty(null)}
      />
    </div>
  );
};

export default Index;
