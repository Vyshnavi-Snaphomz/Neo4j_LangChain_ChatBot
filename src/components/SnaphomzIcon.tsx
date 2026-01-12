import { cn } from "@/lib/utils";

interface SnaphomzIconProps {
  className?: string;
  size?: "sm" | "md" | "lg";
}

const SnaphomzIcon = ({ className, size = "md" }: SnaphomzIconProps) => {
  const sizeClasses = {
    sm: "w-6 h-6",
    md: "w-8 h-8",
    lg: "w-10 h-10",
  };

  return (
    <div
      className={cn(
        "rounded-full bg-gradient-to-br from-primary to-orange-600 flex items-center justify-center",
        sizeClasses[size],
        className
      )}
    >
      <svg
        viewBox="0 0 24 24"
        fill="none"
        className="w-[60%] h-[60%]"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M12 3L4 9V21H9V14H15V21H20V9L12 3Z"
          fill="white"
          stroke="white"
          strokeWidth="1.5"
          strokeLinejoin="round"
        />
        <circle cx="12" cy="10" r="2" fill="hsl(var(--primary))" />
      </svg>
    </div>
  );
};

export default SnaphomzIcon;
