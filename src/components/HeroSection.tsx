import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

const rotatingWords = ["Very Easy", "Stress-Free", "Simple", "Exciting"];

const HeroSection = () => {
  const [currentWord, setCurrentWord] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentWord((prev) => (prev + 1) % rotatingWords.length);
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="text-center z-10 relative"
    >
      <h1 className="font-display text-4xl md:text-5xl lg:text-6xl text-foreground leading-tight">
        Buying a home
        <br />
        should be{" "}
        <span className="inline-block relative">
          <AnimatePresence mode="wait">
            <motion.span
              key={currentWord}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="font-display italic text-primary"
            >
              {rotatingWords[currentWord]}
            </motion.span>
          </AnimatePresence>
        </span>
      </h1>

      <p className="mt-4 text-lg md:text-xl text-muted-foreground">
        First end-to-end guided real estate platform
      </p>
    </motion.div>
  );
};

export default HeroSection;
