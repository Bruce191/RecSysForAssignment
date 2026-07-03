"use client";

import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { useUser } from "../context/UserContext";
import { logout } from "../lib/api";
import { useState } from "react";

export default function Nav() {
  const router = useRouter();
  const pathname = usePathname();
  const { user, logoutUser } = useUser();
  const [loading, setLoading] = useState(false);

  const handleLogout = async () => {
    setLoading(true);
    try {
      await logout();
      logoutUser();
      router.push("/login");
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (pathname === "/login") return null;

  return (
    <nav
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        gap: 20,
        padding: 16,
        background: "#222",
        color: "#fff",
      }}
    >
      {/* LEFT SIDE: App name + links */}
      <div style={{ display: "flex", alignItems: "center", gap: 40 }}>
        <Link href="/recommendations" style={{ color: "#fff", textDecoration: "none" }}>Recommendations</Link>
        <Link href="/manage-account" style={{ color: "#fff", textDecoration: "none" }}>Manage Account</Link>
        <Link href="/learn" style={{ color: "#fff", textDecoration: "none" }}>Learn</Link>
      </div>

      {/* RIGHT SIDE: User info */}
      {user && (
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <span> {user.name} </span>
          <button
            onClick={handleLogout}
            disabled={loading}
            style={{
              padding: "8px 16px",
              background: "#e53e3e",
              border: "none",
              borderRadius: 4,
              color: "#fff",
              cursor: "pointer",
            }}
          >
            Logout
          </button>
        </div>
      )}
    </nav>
  );
}
