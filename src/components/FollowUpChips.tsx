import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { ScrollArea, ScrollBar } from "./ui/scroll-area";

interface FollowUpChipsProps {
  chips: string[];
  onSelect: (chip: string) => void;
}

const FollowUpChips = ({ chips, onSelect }: FollowUpChipsProps) => {
  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.05,
      },
    },
  };

  const item = {
    hidden: { opacity: 0, x: -10 },
    show: { opacity: 1, x: 0 },
  };

  return (
    <ScrollArea className="w-full whitespace-nowrap">
      <motion.div
        variants={container}
        initial="hidden"
        animate="show"
        className="flex gap-2 pb-2"
      >
        {chips.map((chip, index) => (
          <motion.button
            key={index}
            variants={item}
            onClick={() => onSelect(chip)}
            className={cn(
              "shrink-0 px-4 py-2 rounded-full",
              "bg-card border border-border",
              "text-sm text-foreground font-medium",
              "hover:border-primary/50 hover:bg-secondary/50",
              "transition-all duration-200",
              "focus:outline-none focus:ring-2 focus:ring-primary/20"
            )}
          >
            {chip}
          </motion.button>
        ))}
      </motion.div>
      <ScrollBar orientation="horizontal" />
    </ScrollArea>
  );
};

export default FollowUpChips;
