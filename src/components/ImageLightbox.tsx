import { motion, AnimatePresence } from "framer-motion";
import { X, Bed, Bath, MapPin } from "lucide-react";
import { Property } from "@/data/mockData";
import { Button } from "./ui/button";

interface ImageLightboxProps {
  property: Property | null;
  onClose: () => void;
}

const ImageLightbox = ({ property, onClose }: ImageLightboxProps) => {
  if (!property) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-sm p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          transition={{ type: "spring", damping: 25, stiffness: 300 }}
          className="relative max-w-5xl w-full max-h-[90vh] overflow-hidden rounded-2xl bg-card"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Close Button */}
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="absolute top-4 right-4 z-10 bg-black/50 hover:bg-black/70 text-white rounded-full"
          >
            <X className="h-5 w-5" />
          </Button>

          {/* Image */}
          <div className="relative">
            <img
              src={property.image}
              alt={property.address || "Property"}
              className="w-full h-auto max-h-[70vh] object-cover"
            />
            {/* Source Badge */}
            <div
              className="absolute top-4 left-4 px-4 py-1.5 rounded-lg text-sm font-semibold text-white"
              style={{ backgroundColor: property.sourceColor }}
            >
              {property.source}
            </div>
          </div>

          {/* Details */}
          <div className="p-6 bg-card">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div>
                {property.price && (
                  <h2 className="text-2xl font-bold text-foreground">{property.price}</h2>
                )}
                {property.address && (
                  <div className="flex items-center gap-2 text-muted-foreground mt-1">
                    <MapPin className="h-4 w-4" />
                    <span>{property.address}</span>
                  </div>
                )}
              </div>
              <div className="flex items-center gap-6">
                {property.beds && (
                  <div className="flex items-center gap-2">
                    <Bed className="h-5 w-5 text-muted-foreground" />
                    <span className="font-medium">{property.beds} beds</span>
                  </div>
                )}
                {property.baths && (
                  <div className="flex items-center gap-2">
                    <Bath className="h-5 w-5 text-muted-foreground" />
                    <span className="font-medium">{property.baths} baths</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default ImageLightbox;
