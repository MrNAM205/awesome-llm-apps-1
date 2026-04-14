import React, { useState } from "react";
import Timeline from "../organs/timeline/timeline_ui";
import ChatViewer from "../organs/chat_viewer/chat_viewer_ui";
import EntityMapUI from "../organs/entity_map/entity_map_ui";
import ReasoningOverlay from "../organs/reasoning/reasoning_ui";

export default function CockpitApp() {
  const [selectedChat, setSelectedChat] = useState(null);
  const [harvesting, setHarvesting] = useState(false);

  const handleHarvestNow = async () => {
    setHarvesting(true);
    try {
      await fetch("/harvest", { method: "POST" });
      window.location.reload();
    } catch (e) {
      console.error("Harvest failed", e);
      alert("Harvest failed. Ensure Edge is running with --remote-debugging-port=9222");
    } finally {
      setHarvesting(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-900 text-slate-200">
      <div className="flex items-center justify-between px-4 py-2 border-b border-slate-800 bg-slate-950">
        <div className="text-sm font-bold tracking-tight">OMNI COCKPIT</div>
        <button
          onClick={handleHarvestNow}
          disabled={harvesting}
          className="px-3 py-1 text-xs font-semibold rounded bg-sky-600 hover:bg-sky-500 disabled:opacity-50 transition-colors"
        >
          {harvesting ? "HARVESTING..." : "HARVEST NOW"}
        </button>
      </div>
      <div className="grid grid-cols-[260px_minmax(0,1.5fr)_minmax(0,1.2fr)] flex-1 overflow-hidden">
        <Timeline onSelectChat={setSelectedChat} activeChatId={selectedChat} />
        <ChatViewer chatId={selectedChat} />
        <div className="flex flex-col border-l border-slate-800">
          <div className="flex-1 border-b border-slate-800 overflow-hidden">
            <EntityMapUI chatId={selectedChat} />
          </div>
          <div className="flex-1 overflow-hidden">
            <ReasoningOverlay chatId={selectedChat} />
          </div>
        </div>
      </div>
    </div>
  );
}