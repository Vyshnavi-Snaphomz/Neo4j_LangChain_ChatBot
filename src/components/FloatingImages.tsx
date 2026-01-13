import { motion } from "framer-motion";

const floatingImages = [
  {
    src: "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=300&h=300&fit=crop",
    position: "top-[15%] left-[5%]",
    size: "w-32 h-40 md:w-40 md:h-48",
    rotate: -12,
    delay: 0,
  },
  {
    src: "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=300&h=300&fit=crop",
    position: "top-[5%] left-[25%]",
    size: "w-28 h-36 md:w-36 md:h-44",
    rotate: 8,
    delay: 0.1,
  },
  {
    src: "https://images.unsplash.com/photo-1501183638710-841dd1904471?w=300&h=300&fit=crop",
    position: "top-[8%] right-[22%]",
    size: "w-32 h-40 md:w-40 md:h-48",
    rotate: -5,
    delay: 0.2,
  },
  {
    src: "https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=300&h=300&fit=crop",
    position: "top-[20%] right-[5%]",
    size: "w-28 h-36 md:w-36 md:h-44",
    rotate: 15,
    delay: 0.3,
  },
  {
    src: "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=300&h=300&fit=crop",
    position: "bottom-[25%] left-[8%]",
    size: "w-36 h-44 md:w-44 md:h-52",
    rotate: 10,
    delay: 0.4,
  },
  {
    src: "https://images.unsplash.com/photo-1605276374104-dee2a0ed3cd6?w=300&h=300&fit=crop",
    position: "bottom-[20%] right-[8%]",
    size: "w-32 h-40 md:w-40 md:h-48",
    rotate: -8,
    delay: 0.5,
  },
];

const FloatingImages = () => {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {floatingImages.map((image, index) => (
        <motion.div
          key={index}
          initial={{ opacity: 0, scale: 0.8, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{
            duration: 0.6,
            delay: image.delay,
            ease: "easeOut",
          }}
          className={`absolute ${image.position} ${image.size}`}
          style={{ transform: `rotate(${image.rotate}deg)` }}
        >
          <motion.div
            animate={{
              y: [0, -10, 0],
            }}
            transition={{
              duration: 4 + index * 0.5,
              repeat: Infinity,
              ease: "easeInOut",
            }}
            className="w-full h-full"
          >
            <img
              src={image.src}
              alt="Property"
              className="w-full h-full object-cover rounded-2xl shadow-xl"
              style={{ transform: `rotate(${image.rotate}deg)` }}
            />
          </motion.div>
        </motion.div>
      ))}
    </div>
  );
};

export default FloatingImages;
