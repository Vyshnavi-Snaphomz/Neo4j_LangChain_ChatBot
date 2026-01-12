import { useState } from "react";
import { MessageSquarePlus, Search, History, PanelLeftClose, PanelLeft, Trash2 } from "lucide-react";
import { cn } from "@/lib/utils";
import SnaphomzIcon from "./SnaphomzIcon";
import { ChatHistoryItem } from "@/data/mockData";
import { Button } from "./ui/button";
import { ScrollArea } from "./ui/scroll-area";

interface SidebarProps {
  isCollapsed: boolean;
  onToggle: () => void;
  chatHistory: ChatHistoryItem[];
  activeChat: string | null;
  onSelectChat: (id: string) => void;
  onNewChat: () => void;
  onDeleteChat: (id: string) => void;
}

const Sidebar = ({
  isCollapsed,
  onToggle,
  chatHistory,
  activeChat,
  onSelectChat,
  onNewChat,
  onDeleteChat,
}: SidebarProps) => {
  const [hoveredChat, setHoveredChat] = useState<string | null>(null);

  const formatTimestamp = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return "Just now";
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
  };

  return (
    <aside
      className={cn(
        "h-screen bg-sidebar flex flex-col transition-all duration-300 ease-in-out",
        isCollapsed ? "w-16" : "w-64"
      )}
    >
      {/* Header */}
      <div className="p-3 flex items-center justify-between border-b border-sidebar-border">
        <div className={cn("flex items-center gap-3", isCollapsed && "justify-center w-full")}>
          <SnaphomzIcon size="md" />
          {!isCollapsed && (
            <div className="flex flex-col">
              <span className="text-sidebar-foreground font-semibold text-sm">Snaphomz</span>
              <span className="text-sidebar-muted text-xs">AI Search</span>
            </div>
          )}
        </div>
        {!isCollapsed && (
          <Button
            variant="ghost"
            size="icon"
            onClick={onToggle}
            className="text-sidebar-muted hover:text-sidebar-foreground hover:bg-sidebar-accent h-8 w-8"
          >
            <PanelLeftClose className="h-4 w-4" />
          </Button>
        )}
      </div>

      {/* Navigation */}
      <div className="p-2 space-y-1">
        <Button
          variant="ghost"
          onClick={onNewChat}
          className={cn(
            "w-full justify-start gap-3 text-sidebar-foreground hover:bg-sidebar-accent",
            isCollapsed && "justify-center px-2"
          )}
        >
          <MessageSquarePlus className="h-5 w-5" />
          {!isCollapsed && <span>New Chat</span>}
        </Button>

        {isCollapsed && (
          <>
            <Button
              variant="ghost"
              size="icon"
              className="w-full text-sidebar-muted hover:text-sidebar-foreground hover:bg-sidebar-accent"
            >
              <Search className="h-5 w-5" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="w-full text-sidebar-muted hover:text-sidebar-foreground hover:bg-sidebar-accent"
            >
              <History className="h-5 w-5" />
            </Button>
          </>
        )}
      </div>

      {/* Chat History */}
      {!isCollapsed && (
        <div className="flex-1 overflow-hidden flex flex-col">
          <div className="px-3 py-2">
            <span className="text-xs font-medium text-sidebar-muted uppercase tracking-wider">
              Recent
            </span>
          </div>
          <ScrollArea className="flex-1 px-2">
            <div className="space-y-1 pb-4">
              {chatHistory.map((chat) => (
                <div
                  key={chat.id}
                  className={cn(
                    "group relative rounded-lg p-2 cursor-pointer transition-colors",
                    activeChat === chat.id
                      ? "bg-sidebar-primary text-sidebar-primary-foreground"
                      : "hover:bg-sidebar-accent text-sidebar-foreground"
                  )}
                  onClick={() => onSelectChat(chat.id)}
                  onMouseEnter={() => setHoveredChat(chat.id)}
                  onMouseLeave={() => setHoveredChat(null)}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{chat.query}</p>
                      <p
                        className={cn(
                          "text-xs mt-0.5",
                          activeChat === chat.id ? "text-white/70" : "text-sidebar-muted"
                        )}
                      >
                        {formatTimestamp(chat.timestamp)}
                      </p>
                    </div>
                    {hoveredChat === chat.id && (
                      <Button
                        variant="ghost"
                        size="icon"
                        className={cn(
                          "h-6 w-6 shrink-0",
                          activeChat === chat.id
                            ? "text-white/70 hover:text-white hover:bg-white/10"
                            : "text-sidebar-muted hover:text-sidebar-foreground hover:bg-sidebar-accent"
                        )}
                        onClick={(e) => {
                          e.stopPropagation();
                          onDeleteChat(chat.id);
                        }}
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
        </div>
      )}

      {/* Collapse button when collapsed */}
      {isCollapsed && (
        <div className="mt-auto p-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={onToggle}
            className="w-full text-sidebar-muted hover:text-sidebar-foreground hover:bg-sidebar-accent"
          >
            <PanelLeft className="h-5 w-5" />
          </Button>
        </div>
      )}

      {/* Footer */}
      {!isCollapsed && (
        <div className="p-3 border-t border-sidebar-border">
          <p className="text-xs text-sidebar-muted text-center">Powered by Snaphomz AI</p>
        </div>
      )}
    </aside>
  );
};

export default Sidebar;
