import { useState, useRef, useEffect } from "react";
import { Sparkles, Paperclip, ArrowUp } from "lucide-react";
import { cn } from "@/lib/utils";

/* ---------------- TYPES ---------------- */

interface SearchSectionProps {
  onSubmit: (query: string) => void;
  shouldAnimatePlaceholder?: boolean;
  showSuggestions?: boolean;
}

/* ---------------- DATA ---------------- */

const PLACEHOLDER_PHRASES = [
  "Ask about homes in California",
  "Find neighborhoods for families",
  "Compare home prices",
  "Show me houses with pools",
];

const SUGGESTED_QUESTIONS = [
  "What should I look out for?",
  "Will I like my neighbors?",
  "Can I raise a family here?",
  "What's the home worth?",
  "How's the market trending?",
  "Is this neighborhood safe?",
];

/* ---------------- COMPONENT ---------------- */

export default function SearchSection({
  onSubmit,
  shouldAnimatePlaceholder = true,
  showSuggestions = true,
}: SearchSectionProps) {
  const [query, setQuery] = useState("");
  const [displayedText, setDisplayedText] = useState("");
  const [phraseIndex, setPhraseIndex] = useState(0);
  const [isTyping, setIsTyping] = useState(true);
  const [animationStopped, setAnimationStopped] = useState(!shouldAnimatePlaceholder);

  const inputRef = useRef<HTMLInputElement>(null);

  /* ---------------- PLACEHOLDER ANIMATION ---------------- */

  useEffect(() => {
    if (!shouldAnimatePlaceholder || animationStopped) {
      setDisplayedText("Ask anything about this area");
      return;
    }

    const phrase = PLACEHOLDER_PHRASES[phraseIndex];

    if (isTyping) {
      if (displayedText.length < phrase.length) {
        const t = setTimeout(() => {
          setDisplayedText(phrase.slice(0, displayedText.length + 1));
        }, 35);
        return () => clearTimeout(t);
      } else {
        const t = setTimeout(() => setIsTyping(false), 2000);
        return () => clearTimeout(t);
      }
    } else {
      if (displayedText.length > 0) {
        const t = setTimeout(() => {
          setDisplayedText(displayedText.slice(0, -1));
        }, 20);
        return () => clearTimeout(t);
      } else {
        setPhraseIndex((p) => (p + 1) % PLACEHOLDER_PHRASES.length);
        setIsTyping(true);
      }
    }
  }, [
    displayedText,
    isTyping,
    phraseIndex,
    shouldAnimatePlaceholder,
    animationStopped,
  ]);

  const stopAnimation = () => {
    if (!animationStopped) {
      setAnimationStopped(true);
      setDisplayedText("Ask anything about this area");
    }
  };

  /* ---------------- SINGLE SUBMIT FUNCTION (IMPORTANT) ---------------- */

  const submitQuery = (value: string) => {
    const finalQuery = value.trim();
    if (!finalQuery) return;

    onSubmit(finalQuery);
    setQuery("");
  };

  /* ---------------- HANDLERS ---------------- */

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    submitQuery(query);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      submitQuery(query);
    }
  };

  const handleSuggestionClick = (q: string) => {
    submitQuery(q);
  };

  /* ---------------- UI ---------------- */

  return (
    <div className="w-full flex flex-col items-center gap-6">
      {showSuggestions && (
        <div className="flex flex-wrap justify-center gap-3 max-w-3xl">
          {SUGGESTED_QUESTIONS.map((q) => (
            <button
              key={q}
              onClick={() => handleSuggestionClick(q)}
              className="px-4 py-2 rounded-full border border-border bg-background text-sm hover:bg-muted transition"
            >
              {q}
            </button>
          ))}
        </div>
      )}

      <form onSubmit={handleSubmit} className="w-full max-w-2xl">
        <div className="relative flex items-center gap-3 px-4 py-2 rounded-2xl bg-card border border-border shadow-sm">
          <Sparkles className="w-5 h-5 text-muted-foreground shrink-0" />

          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => {
              stopAnimation();
              setQuery(e.target.value);
            }}
            onFocus={stopAnimation}
            onKeyDown={handleKeyDown}
            placeholder={displayedText}
            className="flex-1 bg-transparent outline-none text-foreground placeholder:text-muted-foreground text-sm"
          />

          <button type="button" className="p-2 rounded-full hover:bg-muted">
            <Paperclip className="w-4 h-4 text-muted-foreground" />
          </button>

          <button
            type="submit"
            disabled={!query.trim()}
            className={cn(
              "p-3 rounded-full transition",
              query.trim()
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground"
            )}
          >
            <ArrowUp className="w-4 h-4" />
          </button>
        </div>
      </form>
    </div>
  );
}
