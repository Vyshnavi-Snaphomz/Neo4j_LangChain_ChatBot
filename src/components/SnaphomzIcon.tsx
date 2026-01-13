import { cn } from "@/lib/utils";

interface SnaphomzIconProps {
  className?: string;
}

export function SnaphomzIcon({ className }: SnaphomzIconProps) {
  return (
    <svg
      viewBox="0 0 100 100"
      className={cn("rounded-xl", className)}
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Background with gradient */}
      <defs>
        <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#F57F2E" />
          <stop offset="50%" stopColor="#E85D75" />
          <stop offset="100%" stopColor="#9B59B6" />
        </linearGradient>
      </defs>
      
      {/* Orange/pink gradient arc at top */}
      <path
        d="M 10 60 Q 10 10 50 10 Q 90 10 90 60"
        fill="none"
        stroke="url(#bgGradient)"
        strokeWidth="20"
        strokeLinecap="round"
      />
      
      {/* Black face area */}
      <rect x="10" y="35" width="80" height="55" rx="10" fill="#1a1a1a" />
      
      {/* Left eye - curved white arc */}
      <path
        d="M 25 55 Q 33 40 41 55"
        fill="none"
        stroke="white"
        strokeWidth="6"
        strokeLinecap="round"
      />
      
      {/* Right eye - curved white arc */}
      <path
        d="M 59 55 Q 67 40 75 55"
        fill="none"
        stroke="white"
        strokeWidth="6"
        strokeLinecap="round"
      />
    </svg>
  );
}