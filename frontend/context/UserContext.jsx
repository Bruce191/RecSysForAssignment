"use client";

import { createContext, useContext, useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import API_BASE from "../lib/api";

// Create the context
const UserContext = createContext();

// Provider component to wrap the app
export function UserProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await fetch(`${API_BASE}/user/me`, {
          credentials: "include",
        });

        if (res.ok) {
          const data = await res.json();
          setUser({ name: data.name, user_id: data.user_id });
        } else {
          setUser(null);
        }
      } catch (err) {
        console.error("Failed to fetch current user:", err);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, []);

  const loginUser = (userData) => {
    setUser({ name: userData.name, user_id: userData.user_id });
  };

  const logoutUser = async () => {
    try {
      await fetch(`${API_BASE}/user/logout`, {
        method: "POST",
        credentials: "include",
      });
    } catch (err) {
      console.error("Logout failed:", err);
    } finally {
      setUser(null);
      router.push("/login");
    }
  };

  return (
    <UserContext.Provider
      value={{
        user,
        loginUser,
        logoutUser,
        loading,
        setLoading,
      }}
    >
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  return useContext(UserContext);
}