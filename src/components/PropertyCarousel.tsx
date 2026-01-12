import { motion } from "framer-motion";
import useEmblaCarousel from "embla-carousel-react";
import { Property } from "@/data/mockData";
import { cn } from "@/lib/utils";

interface PropertyCarouselProps {
  properties: Property[];
  onPropertyClick: (property: Property) => void;
}

const PropertyCarousel = ({ properties, onPropertyClick }: PropertyCarouselProps) => {
  const [emblaRef] = useEmblaCarousel({
    align: "start",
    containScroll: "trimSnaps",
    dragFree: true,
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.2 }}
      className="w-full"
    >
      <div className="overflow-hidden" ref={emblaRef}>
        <div className="flex gap-4">
          {properties.map((property, index) => (
            <motion.div
              key={property.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              className={cn(
                "shrink-0 w-56 md:w-64 cursor-pointer group",
                "rounded-xl overflow-hidden",
                "transition-transform duration-300 hover:scale-[1.02]"
              )}
              onClick={() => onPropertyClick(property)}
            >
              <div className="relative aspect-[4/3]">
                <img
                  src={property.image}
                  alt={property.address || "Property"}
                  className="w-full h-full object-cover"
                />
                {/* Source Badge */}
                <div
                  className="absolute top-3 left-3 px-3 py-1 rounded-md text-xs font-semibold text-white"
                  style={{ backgroundColor: property.sourceColor }}
                >
                  {property.source}
                </div>
                {/* Price Overlay */}
                {property.price && (
                  <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-3 pt-8">
                    <p className="text-white font-bold text-lg">{property.price}</p>
                    {property.address && (
                      <p className="text-white/80 text-sm truncate">{property.address}</p>
                    )}
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </motion.div>
  );
};

export default PropertyCarousel;
