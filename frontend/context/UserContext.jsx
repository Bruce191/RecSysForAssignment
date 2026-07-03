"use client";

import { createContext, useContext, useState, useEffect } from "react";
import { useRouter } from "next/navigation";

// Create the context
const UserContext = createContext();

// Provider component to wrap the app
export function UserProvider({ children }) {
  const [user, setUser] = useState(null); // Stores logged-in user info
  const [loading, setLoading] = useState(true); // True while checking auth status
  const router = useRouter();

  // Auto-fetch current user on mount
  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await fetch("http://localhost:8000/user/me", {
          credentials: "include", // Include JWT cookie
        });

        if (res.ok) {
          const data = await res.json();
          // Ensure we always have the expected fields
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

  // Login updates user state
  const loginUser = (userData) => {
    // Only update expected fields
    setUser({ name: userData.name, user_id: userData.user_id });
  };

  // Logout clears user state and calls backend
  const logoutUser = async () => {
    try {
      await fetch("http://localhost:8000/user/logout", {
        method: "POST",
        credentials: "include",
      });
    } catch (err) {
      console.error("Logout failed:", err);
    } finally {
      setUser(null);
      router.push("/login"); // optional: redirect after logout
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

// Custom hook to use the user context
export function useUser() {
  return useContext(UserContext);
}
