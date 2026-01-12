import { motion } from "framer-motion";

interface AISummaryProps {
  summary: string;
  sourcesCount: number;
}

const AISummary = ({ summary, sourcesCount }: AISummaryProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.3 }}
      className="space-y-4"
    >
      <p className="text-sm text-muted-foreground">
        Reviewed {sourcesCount} sources
      </p>
      <div className="prose prose-neutral max-w-none">
        <p className="text-foreground text-base md:text-lg leading-relaxed">
          {summary}
        </p>
      </div>
    </motion.div>
  );
};

export default AISummary;
