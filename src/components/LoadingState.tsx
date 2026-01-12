import { motion } from "framer-motion";

const LoadingState = () => {
  return (
    <div className="space-y-6">
      {/* Query Skeleton */}
      <div className="space-y-3">
        <div className="h-8 w-3/4 bg-muted rounded-lg animate-shimmer" />
        <div className="h-4 w-32 bg-muted rounded animate-shimmer" />
      </div>

      {/* Follow-ups Skeleton */}
      <div className="flex gap-2">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="h-10 w-32 bg-muted rounded-full animate-shimmer"
            style={{ animationDelay: `${i * 0.1}s` }}
          />
        ))}
      </div>

      {/* Property Cards Skeleton */}
      <div className="flex gap-4 overflow-hidden">
        {[1, 2, 3, 4].map((i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.1 }}
            className="shrink-0 w-56 md:w-64 aspect-[4/3] bg-muted rounded-xl animate-shimmer"
          />
        ))}
      </div>

      {/* Summary Skeleton */}
      <div className="space-y-3 pt-4">
        <div className="h-4 w-full bg-muted rounded animate-shimmer" />
        <div className="h-4 w-5/6 bg-muted rounded animate-shimmer" />
        <div className="h-4 w-4/5 bg-muted rounded animate-shimmer" />
      </div>
    </div>
  );
};

export default LoadingState;
