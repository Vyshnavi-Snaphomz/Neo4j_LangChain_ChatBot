import { useState } from "react";
import {
  MessageSquarePlus,
  Search,
  History,
  PanelLeft,
  Trash2,
  Clock,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { SnaphomzIcon } from "./SnaphomzIcon";
import { ChatHistoryItem } from "@/data/mockData";

interface SidebarProps {
  chatHistory: ChatHistoryItem[];
  activeChat: string | null;
  onSelectChat: (id: string) => void;
  onNewChat: () => void;
  onDeleteChat: (id: string) => void;
  isCollapsed: boolean;
  onToggle: () => void;
}

const Sidebar = ({
  chatHistory,
  activeChat,
  onSelectChat,
  onNewChat,
  onDeleteChat,
  isCollapsed,
  onToggle,
}: SidebarProps) => {
  const [hoveredId, setHoveredId] = useState<string | null>(null);

  const formatTimestamp = (date: Date) => {
    const diff = Date.now() - date.getTime();
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
        "h-screen bg-[#FAFAF9] text-[#0F172A] border-r border-[#E5E7EB] flex flex-col shadow-[2px_0_12px_rgba(15,23,42,0.04)]",
        isCollapsed ? "w-16" : "w-64"
      )}
    >
      {/* COLLAPSED */}
      {isCollapsed ? (
        <div className="flex flex-col h-full py-3">
          <div className="flex flex-col items-center gap-2">
            <button
              onClick={onToggle}
              className="w-10 h-10 flex items-center justify-center rounded-lg hover:bg-[#F1F5F9]"
            >
              <SnaphomzIcon className="w-8 h-8" />
            </button>

            <button
              onClick={onNewChat}
              className="w-10 h-10 flex items-center justify-center rounded-lg text-[#475569] hover:bg-[#F1F5F9]"
            >
              <MessageSquarePlus className="w-5 h-5" />
            </button>

            <button className="w-10 h-10 flex items-center justify-center rounded-lg text-[#475569] hover:bg-[#F1F5F9]">
              <Search className="w-5 h-5" />
            </button>

            <button className="w-10 h-10 flex items-center justify-center rounded-lg text-[#475569] hover:bg-[#F1F5F9]">
              <History className="w-5 h-5" />
            </button>
          </div>

          <div className="flex-1" />

          <div className="flex justify-center">
            <button
              onClick={onToggle}
              className="w-10 h-10 flex items-center justify-center rounded-lg text-[#475569] hover:bg-[#F1F5F9]"
            >
              <PanelLeft className="w-5 h-5" />
            </button>
          </div>
        </div>
      ) : (
        <>
          {/* HEADER */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-[#E5E7EB]">
            <div className="flex items-center gap-3">
              <SnaphomzIcon className="w-8 h-8" />
              <div>
                <h1 className="text-sm font-semibold tracking-tight">
                  Snaphomz
                </h1>
                <p className="text-xs text-[#64748B]">AI Search</p>
              </div>
            </div>

            <button
              onClick={onToggle}
              className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-[#F1F5F9]"
            >
              <PanelLeft className="w-4 h-4 rotate-180" />
            </button>
          </div>

          {/* NEW CHAT */}
          <div className="p-3">
            <Button
              onClick={onNewChat}
              variant="ghost"
              className="w-full justify-start gap-3 h-10 text-[#0F172A] bg-[#F8FAFC] hover:bg-[#EEF2FF] border border-[#E5E7EB]"
            >
              <MessageSquarePlus className="w-5 h-5" />
              <span className="font-medium">New Chat</span>
            </Button>
          </div>

          {/* RECENT */}
          <div className="flex-1 flex flex-col min-h-0">
            <div className="px-4 py-2">
              <p className="text-xs font-medium uppercase tracking-wider text-[#6B7280]">
                Recent
              </p>
            </div>

            <ScrollArea className="flex-1 px-2">
              {chatHistory.length === 0 ? (
                <div className="px-4 py-6 text-center">
                  <Clock className="w-5 h-5 mx-auto text-[#CBD5E1] mb-2" />
                  <p className="text-xs text-[#94A3B8]">
                    No recent searches
                  </p>
                </div>
              ) : (
                <div className="space-y-1">
                  {chatHistory.map((chat) => (
                    <div
                      key={chat.id}
                      onClick={() => onSelectChat(chat.id)}
                      onMouseEnter={() => setHoveredId(chat.id)}
                      onMouseLeave={() => setHoveredId(null)}
                      className={cn(
                        "group relative rounded-lg px-3 py-2 cursor-pointer transition-colors",
                        activeChat === chat.id
                          ? "bg-[#EEF2FF] text-[#1E3A8A] ring-1 ring-[#C7D2FE]"
                          : "hover:bg-[#F1F5F9] text-[#0F172A]"
                      )}
                    >
                      <p className="text-sm font-medium truncate pr-6">
                        {chat.query}
                      </p>
                      <p className="text-xs text-[#9CA3AF]">
                        {formatTimestamp(chat.timestamp)}
                      </p>

                      {hoveredId === chat.id && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onDeleteChat(chat.id);
                          }}
                          className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded-md hover:bg-red-100 text-[#94A3B8] hover:text-red-500"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </ScrollArea>
          </div>

          {/* FOOTER */}
          <div className="p-3 border-t border-[#E5E7EB]">
            <p className="text-[10px] text-center text-[#94A3B8]">
              Powered by Snaphomz AI
            </p>
          </div>
        </>
      )}
    </aside>
  );
};

export default Sidebar;
