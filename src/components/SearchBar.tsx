import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { Sparkles, Paperclip, ArrowUp } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "./ui/button";

interface SearchBarProps {
  onSearch: (query: string) => void;
  isLoading?: boolean;
  variant?: "centered" | "bottom";
  placeholder?: string;
}

const placeholderTexts = [
  "Compare home prices...",
  "Find homes with pools...",
  "Search by school district...",
  "Explore neighborhoods...",
  "Check market trends...",
];

const SearchBar = ({ onSearch, isLoading, variant = "centered", placeholder }: SearchBarProps) => {
  const [query, setQuery] = useState("");
  const [currentPlaceholder, setCurrentPlaceholder] = useState(0);
  const [isFocused, setIsFocused] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (variant === "centered" && !placeholder) {
      const interval = setInterval(() => {
        setCurrentPlaceholder((prev) => (prev + 1) % placeholderTexts.length);
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [variant, placeholder]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isLoading) {
      onSearch(query.trim());
      setQuery("");
    }
  };

  const displayPlaceholder = placeholder || placeholderTexts[currentPlaceholder];

  return (
    <motion.form
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.3 }}
      onSubmit={handleSubmit}
      className={cn("w-full max-w-2xl mx-auto", variant === "bottom" && "px-4")}
    >
      <div
        className={cn(
          "relative flex items-center gap-2 rounded-2xl bg-card border-2 transition-all duration-300",
          isFocused ? "border-primary shadow-lg shadow-primary/10" : "border-border shadow-md",
          "px-4 py-3"
        )}
      >
        <Sparkles className="w-5 h-5 text-muted-foreground shrink-0" />
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder={displayPlaceholder}
          disabled={isLoading}
          className={cn(
            "flex-1 bg-transparent border-none outline-none",
            "text-foreground placeholder:text-muted-foreground",
            "text-base"
          )}
        />
        <div className="flex items-center gap-1">
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="h-8 w-8 text-muted-foreground hover:text-foreground"
          >
            <Paperclip className="w-4 h-4" />
          </Button>
          <Button
            type="submit"
            variant="ghost"
            size="icon"
            disabled={!query.trim() || isLoading}
            className={cn(
              "h-8 w-8 rounded-lg transition-colors",
              query.trim()
                ? "bg-foreground text-background hover:bg-foreground/90"
                : "text-muted-foreground"
            )}
          >
            <ArrowUp className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </motion.form>
  );
};

export default SearchBar;
