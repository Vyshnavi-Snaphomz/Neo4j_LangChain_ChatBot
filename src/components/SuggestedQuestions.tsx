import { motion } from "framer-motion";
import { Eye, Users, Heart, Home, TrendingUp, Shield } from "lucide-react";
import { cn } from "@/lib/utils";

interface SuggestedQuestionsProps {
  onSelect: (question: string) => void;
}

const questions = [
  { icon: Eye, text: "What should I look out for?" },
  { icon: Users, text: "Will I like my neighbors?" },
  { icon: Heart, text: "Can I raise a family here?" },
  { icon: Home, text: "What's the home worth?" },
  { icon: TrendingUp, text: "How's the market trending?" },
  { icon: Shield, text: "Is this neighborhood safe?" },
];

const SuggestedQuestions = ({ onSelect }: SuggestedQuestionsProps) => {
  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.05,
        delayChildren: 0.2,
      },
    },
  };

  const item = {
    hidden: { opacity: 0, y: 10 },
    show: { opacity: 1, y: 0 },
  };

  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="show"
      className="flex flex-wrap justify-center gap-3 max-w-3xl mx-auto"
    >
      {questions.map((question, index) => {
        const Icon = question.icon;
        return (
          <motion.button
            key={index}
            variants={item}
            onClick={() => onSelect(question.text)}
            className={cn(
              "flex items-center gap-2 px-4 py-2.5 rounded-full",
              "bg-card border border-border",
              "text-sm text-foreground font-medium",
              "hover:border-primary/50 hover:shadow-md",
              "transition-all duration-200 ease-out",
              "focus:outline-none focus:ring-2 focus:ring-primary/20"
            )}
          >
            <Icon className="w-4 h-4 text-muted-foreground" />
            <span>{question.text}</span>
          </motion.button>
        );
      })}
    </motion.div>
  );
};

export default SuggestedQuestions;
