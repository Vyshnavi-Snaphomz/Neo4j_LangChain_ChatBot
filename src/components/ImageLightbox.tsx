import { motion, AnimatePresence } from "framer-motion";
import { X, Bed, Bath, MapPin, Ruler, Calendar, Home, Info, ExternalLink } from "lucide-react";
import { Property } from "@/data/mockData";
import { Button } from "./ui/button";

interface ExtendedProperty extends Property {
  images?: string[];
  sqft?: number;
  lotSize?: string;
  yearBuilt?: number;
  propertyType?: string;
  status?: string;
  listingUrl?: string;
  description?: string;
}

interface ImageLightboxProps {
  property: ExtendedProperty | null;
  onClose: () => void;
}

const ImageLightbox = ({ property, onClose }: ImageLightboxProps) => {
  if (!property) return null;

  // Normalize images to ensure we always have an array
  const images = property.images && property.images.length > 0
    ? property.images
    : property.image
      ? [property.image]
      : [];

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-[100] flex items-center justify-center bg-black/95 backdrop-blur-sm"
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ type: "spring", duration: 0.5, bounce: 0.3 }}
          className="relative w-full max-w-7xl h-[95vh] bg-zinc-950 rounded-2xl overflow-hidden shadow-2xl flex flex-col border border-white/10"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Close Button */}
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="absolute top-6 right-6 z-50 bg-black/50 hover:bg-white/20 text-white rounded-full h-10 w-10 transition-colors backdrop-blur-md border border-white/10"
          >
            <X className="h-5 w-5" />
          </Button>

          {/* 1. Image Gallery (Horizontal Scroll) */}
          <div className="w-full h-[60%] min-h-[400px] bg-black/50 overflow-hidden relative group">
            <div className="absolute inset-0 flex items-center overflow-x-auto snap-x snap-mandatory scrollbar-hide px-6 gap-4 py-6 scroll-smooth">
              {images.length > 0 ? (
                images.map((url, index) => (
                  <div
                    key={`${property.id}-img-${index}`}
                    className="relative h-full flex-shrink-0 snap-center first:pl-2 last:pr-2"
                  >
                    <img
                      src={url}
                      alt={`${property.address || "Property"} - View ${index + 1}`}
                      className="h-full w-auto object-cover rounded-lg shadow-lg select-none pointer-events-none border border-white/5"
                      loading={index < 2 ? "eager" : "lazy"}
                      onError={(e) => {
                        e.currentTarget.src = "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&q=80";
                        e.currentTarget.onerror = null;
                      }}
                    />
                  </div>
                ))
              ) : (
                <div className="w-full h-full flex items-center justify-center text-white/30 bg-white/5 rounded-xl">
                  <div className="flex flex-col items-center gap-2">
                    <Info className="h-8 w-8" />
                    <span>No images available</span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* 2. Property Metadata (Vertical Scroll) */}
          <div className="flex-1 bg-zinc-900/50 backdrop-blur-xl border-t border-white/10 overflow-y-auto custom-scrollbar">
            <div className="max-w-5xl mx-auto p-8 space-y-8">

              {/* Header Info */}
              <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-6">
                <div className="space-y-2">
                  <div className="flex items-center gap-3">
                    <h2 className="text-4xl font-light text-white tracking-tight">
                      {property.price || "Price pending"}
                    </h2>
                    {property.status && (
                      <span className="px-3 py-1 rounded-full text-xs font-medium bg-white/10 text-white border border-white/10">
                        {property.status}
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-2 text-zinc-400 text-lg">
                    <MapPin className="h-5 w-5" />
                    <span>{property.address || "Address unavailable"}</span>
                  </div>
                </div>

                <div className="flex gap-4">
                  {property.listingUrl && (
                    <Button
                      className="bg-white text-black hover:bg-zinc-200 rounded-full px-6"
                      onClick={() => window.open(property.listingUrl, '_blank')}
                    >
                      View Original
                      <ExternalLink className="ml-2 h-4 w-4" />
                    </Button>
                  )}
                </div>
              </div>

              {/* Specs Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 py-6 border-y border-white/5">
                <div className="flex flex-col gap-1 p-3 rounded-lg bg-white/5 border border-white/5">
                  <div className="flex items-center gap-2 text-zinc-500 text-xs uppercase tracking-wider font-medium">
                    <Bed className="h-4 w-4" /> Beds
                  </div>
                  <span className="text-xl text-white font-light">{property.beds || "—"}</span>
                </div>

                <div className="flex flex-col gap-1 p-3 rounded-lg bg-white/5 border border-white/5">
                  <div className="flex items-center gap-2 text-zinc-500 text-xs uppercase tracking-wider font-medium">
                    <Bath className="h-4 w-4" /> Baths
                  </div>
                  <span className="text-xl text-white font-light">{property.baths || "—"}</span>
                </div>

                <div className="flex flex-col gap-1 p-3 rounded-lg bg-white/5 border border-white/5">
                  <div className="flex items-center gap-2 text-zinc-500 text-xs uppercase tracking-wider font-medium">
                    <Ruler className="h-4 w-4" /> Sqft
                  </div>
                  <span className="text-xl text-white font-light">
                    {property.sqft ? property.sqft.toLocaleString() : "—"}
                  </span>
                </div>

                <div className="flex flex-col gap-1 p-3 rounded-lg bg-white/5 border border-white/5">
                  <div className="flex items-center gap-2 text-zinc-500 text-xs uppercase tracking-wider font-medium">
                    <Home className="h-4 w-4" /> Lot
                  </div>
                  <span className="text-xl text-white font-light">{property.lotSize || "—"}</span>
                </div>

                <div className="flex flex-col gap-1 p-3 rounded-lg bg-white/5 border border-white/5">
                  <div className="flex items-center gap-2 text-zinc-500 text-xs uppercase tracking-wider font-medium">
                    <Calendar className="h-4 w-4" /> Built
                  </div>
                  <span className="text-xl text-white font-light">{property.yearBuilt || "—"}</span>
                </div>

                <div className="flex flex-col gap-1 p-3 rounded-lg bg-white/5 border border-white/5">
                  <div className="flex items-center gap-2 text-zinc-500 text-xs uppercase tracking-wider font-medium">
                    <Info className="h-4 w-4" /> Type
                  </div>
                  <span className="text-xl text-white font-light">{property.propertyType || "Home"}</span>
                </div>
              </div>

              {/* Description */}
              <div className="space-y-4">
                <h3 className="text-xl font-medium text-white">Description</h3>
                <p className="text-zinc-400 leading-relaxed text-lg max-w-4xl">
                  {property.description ||
                    `A stunning ${property.beds || 3}-bedroom, ${property.baths || 2}-bath residence located at ${property.address}. 
                   This property features modern amenities, spacious living areas, and is situated in a desirable neighborhood. 
                   Perfect for those looking for luxury living with convenient access to local attractions.`}
                </p>
              </div>

            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default ImageLightbox;
