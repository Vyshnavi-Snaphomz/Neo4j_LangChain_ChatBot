import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "./ui/button";
import { RadioGroup, RadioGroupItem } from "./ui/radio-group";
import { Label } from "./ui/label";

interface SearchBarProps {
  onSearch: (query: string) => void;
  isLoading?: boolean;
  variant?: "hero" | "bottom";
  placeholder?: string;
}

const placeholderTexts = [
  "Show me homes in San Jose CA",
  "Find houses near good schools",
  "3 bed homes under $500k",
  "Condos with a view in SF",
];

const SearchBar = ({ onSearch, isLoading, variant = "hero", placeholder }: SearchBarProps) => {
  const [query, setQuery] = useState("");
  const [currentPlaceholder, setCurrentPlaceholder] = useState(0);
  const [isFocused, setIsFocused] = useState(false);
  const [searchType, setSearchType] = useState("location");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (variant === "hero" && !placeholder) {
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

  if (variant === "bottom") {
    return (
      <motion.form
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        onSubmit={handleSubmit}
        className="w-full max-w-2xl mx-auto px-4"
      >
        <div
          className={cn(
            "relative flex items-center gap-2 rounded-2xl bg-card border-2 transition-all duration-300",
            isFocused ? "border-primary shadow-lg shadow-primary/10" : "border-border shadow-md",
            "px-4 py-3"
          )}
        >
          <Sparkles className="w-5 h-5 text-primary shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder={displayPlaceholder}
            disabled={isLoading}
            className="flex-1 bg-transparent border-none outline-none text-foreground placeholder:text-muted-foreground text-base"
          />
        </div>
      </motion.form>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.3 }}
      className="w-full max-w-xl mx-auto z-10 relative"
    >
      <form onSubmit={handleSubmit}>
        <div
          className={cn(
            "relative flex items-center rounded-full bg-card border-2 transition-all duration-300 overflow-hidden",
            isFocused ? "border-primary shadow-xl shadow-primary/15" : "border-border shadow-lg",
            "pl-5 pr-2 py-2"
          )}
        >
          <Sparkles className="w-5 h-5 text-primary shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder={displayPlaceholder}
            disabled={isLoading}
            className="flex-1 bg-transparent border-none outline-none text-foreground placeholder:text-muted-foreground text-base px-3"
          />
          <Button
            type="submit"
            disabled={isLoading}
            className="rounded-full bg-primary hover:bg-primary/90 text-primary-foreground font-semibold px-6 py-2.5 h-auto"
          >
            Begin Journey
          </Button>
        </div>
      </form>

      {/* Search Type Toggle */}
      <div className="flex justify-center mt-4">
        <RadioGroup
          value={searchType}
          onValueChange={setSearchType}
          className="flex items-center gap-6"
        >
          <div className="flex items-center gap-2">
            <RadioGroupItem value="location" id="location" className="border-muted-foreground" />
            <Label htmlFor="location" className="text-sm text-muted-foreground cursor-pointer">
              Search by Location
            </Label>
          </div>
          <div className="flex items-center gap-2">
            <RadioGroupItem value="address" id="address" className="border-muted-foreground" />
            <Label htmlFor="address" className="text-sm text-muted-foreground cursor-pointer">
              Search by Full Address
            </Label>
          </div>
        </RadioGroup>
      </div>
    </motion.div>
  );
};

export default SearchBar;
