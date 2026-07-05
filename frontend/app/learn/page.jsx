"use client";

import { useEffect } from "react";
import { useUser } from "../../context/UserContext";
import { useRouter } from "next/navigation";

export default function LearnPage() {
  const { user } = useUser();
  const router = useRouter();

  useEffect(() => {
    // Redirect to login if not authenticated
    if (!user) router.push("/login");
  }, [user]);

  return (
    <>
      <div style={{ padding: 24 }}>
        <h1>✨ How to Use This App</h1>
        <p>Welcome! 👋 This app gives personalized news recommendations.</p>
        <ul>
          <li>🔐 Log in with your name</li>
          <li>📊 See recommendations tailored for you</li>
          <li>💬 Interact: like, dislike, share, report</li>
        </ul>

        <h2>❓ What is this app for?</h2>
        <p>It produces recommendations, allows new interactions, and extracts safety metrics.</p>
      </div>
    </>
  );
}
