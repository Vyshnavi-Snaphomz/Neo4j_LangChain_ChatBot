const LoadingState = () => {
  return (
    <div className="flex justify-start">
      <div className="rounded-2xl border bg-card px-4 py-3">
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Thinking</span>
          <div className="flex items-center gap-1">
            <span
              className="h-2 w-2 rounded-full bg-muted-foreground/70 animate-bounce"
              style={{ animationDelay: "0ms" }}
            />
            <span
              className="h-2 w-2 rounded-full bg-muted-foreground/70 animate-bounce"
              style={{ animationDelay: "120ms" }}
            />
            <span
              className="h-2 w-2 rounded-full bg-muted-foreground/70 animate-bounce"
              style={{ animationDelay: "240ms" }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoadingState;
