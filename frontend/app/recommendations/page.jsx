"use client";

import { useEffect, useState } from "react";
import { useUser } from "../../context/UserContext";
import { useRouter } from "next/navigation";
import NewsCard from "../../components/NewsCard";

export default function RecommendationsPage() {
  const { user, loading } = useUser();
  const router = useRouter();
  const [recs, setRecs] = useState([]);
  const [userInteractions, setUserInteractions] = useState([]);
  const [updating, setUpdating] = useState(false); // spinner state

  useEffect(() => {
    if (!loading && !user) {
      router.push("/login");
    } else if (user) {
      fetchRecommendations();
      fetchUserInteractions();
    }
  }, [user, loading]);

  const fetchRecommendations = async () => {
    try {
      const res = await fetch("http://localhost:8000/user/get-recommendations", {
        method: "POST",
        credentials: "include",
      });
      if (!res.ok) return;
      setRecs(await res.json());
    } catch (err) {
      console.error("Error fetching recommendations:", err);
    }
  };

  const fetchUserInteractions = async () => {
    try {
      const res = await fetch("http://localhost:8000/user/interactions", {
        credentials: "include",
      });
      if (!res.ok) return;
      
      const data = await res.json();

      setUserInteractions(
        data.map((i) => ({
          content_id: i.content_id,
          interaction_type: i.interaction_type.toLowerCase(),
        }))
      );
    } catch (err) {
      console.error("Error fetching interactions:", err);
    }
  };

  /** 🔥 Main Interaction Handler */
  const handleInteraction = async (contentId, interactionType) => {
    if (!user) return { success: false };

    try {
      // 1️⃣ Store the interaction in backend
      const res = await fetch("http://localhost:8000/user/store-interaction", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ content_id: contentId, interaction_type: interactionType }),
      });

      if (!res.ok) {
        console.error("Failed to store interaction");
        return { success: false };
      }

      // 2️⃣ Update UI Local State (optimistic UI)
      setUserInteractions((prev) => {
        const type = interactionType.startsWith("un")
          ? interactionType.slice(2).toLowerCase()
          : interactionType.toLowerCase();

        if (interactionType.startsWith("un")) {
          return prev.filter(
            (i) => !(i.content_id === contentId && i.interaction_type.toLowerCase() === type.toLowerCase())
          );
        }

        let updated = prev.filter((i) => {
          if (type === "like")
            return !(i.content_id === contentId && i.interaction_type === "dislike");
          if (type === "dislike")
            return !(i.content_id === contentId && i.interaction_type === "like");
          return true;
        });

        return [
          ...updated,
          { content_id: contentId, interaction_type: type }
        ];
      });

      // Debounce recommender refresh (wait 1.5s after last interaction)
      if (window.refreshTimer) clearTimeout(window.refreshTimer);

      window.refreshTimer = setTimeout(async () => {
      setUpdating(true);
      await fetch("http://localhost:8000/BackendFunctions/refresh-recommendations", {
      method: "POST",
      credentials: "include",
      });
      await fetchRecommendations();
      setUpdating(false);
      }, 1500);

      // 4️⃣ Load updated recommendations
      await fetchRecommendations();

      setUpdating(false);

      return { success: true };
    } catch (err) {
      console.error("Error storing interaction:", err);
      return { success: false };
    }
  };

  if (loading) return <p>Loading...</p>;

  return (
    <div style={{ padding: 24 }}>
      <h1>Recommended Content</h1>

      {updating && (
        <p style={{ color: "blue", fontStyle: "italic", marginBottom: 10 }}>
          🔄 Updating recommendations…
        </p>
      )}

      {recs.length === 0 ? (
        <p>No recommendations found.</p>
      ) : (
        recs.map((item) => (
          <NewsCard
            key={item.content_id}
            news={item}
            userInteractions={userInteractions}
            onInteract={handleInteraction}
          />
        ))
      )}
    </div>
  );
}
