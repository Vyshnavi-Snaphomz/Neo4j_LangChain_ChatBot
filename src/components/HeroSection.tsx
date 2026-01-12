import { motion } from "framer-motion";

const HeroSection = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="text-center"
    >
      <h1 className="font-display text-6xl md:text-7xl lg:text-8xl italic text-foreground mb-4">
        AI Search
      </h1>
      <p className="text-lg md:text-xl text-muted-foreground">
        Your AI-powered real estate assistant
      </p>
    </motion.div>
  );
};

export default HeroSection;
