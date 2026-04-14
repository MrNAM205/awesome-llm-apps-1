import React, { useEffect, useState } from "react";
export default function Timeline({ onSelectChat, activeChatId }) {
  const [chats, setChats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTimeline = async () => {
      try {
        const res = await fetch("/api/timeline");
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        const data = await res.json();
        setChats(data.chats || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchTimeline();
  }, []);

  if (loading) return <div style={styles.container}>Initializing timeline...</div>;
  if (error) return <div style={styles.container}>Timeline Error: {error}</div>;
  if (!chats.length) return <div style={styles.empty}>No chats ingested yet.</div>;

  return (
    <div style={styles.container}>
      {chats.map(chat => (
        <div
          key={chat.id}
          style={{
            ...styles.item,
            ...(chat.id === activeChatId ? styles.active : {})
          }}
          onClick={() => onSelectChat(chat.id)}
          className="timeline-item"
        >
          <div style={styles.title}>
            {chat.title || `Chat #${chat.id}`}
          </div>
          <div style={styles.preview}>{chat.preview || "No preview available"}</div>
          <div style={styles.meta}>
            {chat.created_at
              ? new Date(chat.created_at * 1000).toLocaleString()
              : "Unknown date"}
          </div>
        </div>
      ))}
    </div>
  );
}

const styles = {
  container: {
    height: "100%",
    width: "100%",
    overflowY: "auto",
    padding: "12px",
    background: "#020617",
    color: "#e5e7eb",
    fontFamily: "Inter, sans-serif",
    borderRight: "1px solid #1e293b"
  },
  item: {
    padding: "12px 14px",
    borderRadius: "6px",
    marginBottom: "10px",
    cursor: "pointer",
    background: "#0f172a",
    border: "1px solid #1f2937",
    transition: "background 0.15s, border 0.15s"
  },
  active: {
    background: "#1e3a8a",
    border: "1px solid #3b82f6"
  },
  title: { fontSize: "14px", fontWeight: "600", color: "#f8fafc", marginBottom: "4px" },
  preview: { fontSize: "12px", opacity: 0.8, marginBottom: "6px" },
  meta: { fontSize: "11px", opacity: 0.6 },
  empty: {
    padding: "20px",
    color: "#64748b",
    fontSize: "14px"
  }
};