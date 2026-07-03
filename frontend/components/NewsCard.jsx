"use client";

export default function NewsCard({ news, userInteractions = [], onInteract }) {
  // derive states from userInteractions
  const liked = userInteractions.some(
    (i) => i.content_id === news.content_id && i.interaction_type === "like"
  );
  const disliked = userInteractions.some(
    (i) => i.content_id === news.content_id && i.interaction_type === "dislike"
  );
  const shared = userInteractions.some(
    (i) => i.content_id === news.content_id && i.interaction_type === "share"
  );
  const reported = userInteractions.some(
    (i) => i.content_id === news.content_id && i.interaction_type === "report"
  );

  const handleClick = async (type) => {
    // Determine if undo action
    let isActive = false;
    switch (type) {
      case "like": isActive = liked; break;
      case "dislike": isActive = disliked; break;
      case "share": isActive = shared; break;
      case "report": isActive = reported; break;
      default: break;
    }

    // Compute interaction type to send to backend
    const interactionType = isActive ? `un${type}` : type;

    // Call parent handler
    await onInteract(news.content_id, interactionType);
  };

  return (
    <div className="news-card">
      <h2>{news.title}</h2>
      <p>{news.category} | {news.sub_category}</p>
      <p>{news?.abstract?.trim() || "No abstract available."}</p>

      <div style={{ display: "flex", gap: "8px", marginTop: "8px" }}>
        <button
          onClick={() => handleClick("like")}
          className={liked ? "bg-green-400 text-white" : "bg-green-200"}
        >
          👍 {liked ? 1 : 0}
        </button>

        <button
          onClick={() => handleClick("dislike")}
          className={disliked ? "bg-red-400 text-white" : "bg-red-200"}
        >
          👎 {disliked ? 1 : 0}
        </button>

        <button
          onClick={() => handleClick("share")}
          className={shared ? "bg-blue-400 text-white" : "bg-blue-200"}
        >
          🔄 {shared ? 1 : 0}
        </button>

        <button
          onClick={() => handleClick("report")}
          className={reported ? "bg-yellow-400 text-white" : "bg-yellow-200"}
        >
          🚨 {reported ? 1 : 0}
        </button>
      </div>
    </div>
  );
}
