"use client";
import API_BASE from "../../lib/api";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useUser } from "../../context/UserContext";

export default function LoginPage() {
  const router = useRouter();
  const { loginUser } = useUser();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [checkingAuth, setCheckingAuth] = useState(true);

  // CHECK IF ALREADY LOGGED IN
  useEffect(() => {
    async function checkIfLoggedIn() {
      try {
        const res = await fetch(`${API_BASE}/user/me`, {
          credentials: "include",
        });

        if (res.ok) {
          const userData = await res.json();
          loginUser(userData);
          router.replace("/recommendations");
          return;
        }
      } catch (err) {}

      setCheckingAuth(false);
    }

    checkIfLoggedIn();
  }, []);

  // LOGIN
  const handleLogin = async (e) => {
    e.preventDefault();
    setMessage("");

    if (!username || !password) {
      setMessage("Please enter both username and password.");
      return;
    }

    setLoading(true);

    try {
      const formData = new URLSearchParams();
      formData.append("username", username);
      formData.append("password", password);

      const res = await fetch(`${API_BASE}/user/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        credentials: "include",
        body: formData.toString(),
      });

      if (!res.ok) {
        const errData = await res.json();
        setMessage(errData.detail || "Login failed.");
        return;
      }

      const userRes = await fetch(`${API_BASE}/user/me`, {
        credentials: "include",
      });

      const userData = await userRes.json();
      loginUser(userData);

      router.push("/recommendations");
    } catch (err) {
      console.error(err);
      setMessage("Login failed. Check console for details.");
    } finally {
      setLoading(false);
    }
  };

  if (checkingAuth) return null;

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        padding: "40px 16px",
        backgroundColor: "#f0f2f5",
        minHeight: "100vh",
        alignItems: "flex-start",
      }}
    >
      <div
        style={{
          backgroundColor: "#fff",
          padding: "32px",
          borderRadius: "12px",
          boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
          width: "100%",
          maxWidth: "400px",
        }}
      >
        <h1
          style={{
            textAlign: "center",
            marginBottom: "24px",
            color: "#1e40af",
            fontSize: "24px",
          }}
        >
          Recommender Systems App
        </h1>

        {message && (
          <div
            style={{
              marginBottom: "16px",
              padding: "10px",
              borderRadius: "6px",
              textAlign: "center",
              fontSize: "14px",
              backgroundColor: "#f8d7da",
              color: "#721c24",
              border: "1px solid #f5c6cb",
            }}
          >
            {message}
          </div>
        )}

        <form onSubmit={handleLogin}>
          <input
            type="text"
            placeholder="Enter your username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            style={{
              width: "100%",
              padding: "10px 12px",
              borderRadius: "6px",
              border: "1px solid #ccc",
              marginBottom: "16px",
              fontSize: "14px",
            }}
          />

          <input
            type="password"
            placeholder="Enter your password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{
              width: "100%",
              padding: "10px 12px",
              borderRadius: "6px",
              border: "1px solid #ccc",
              marginBottom: "24px",
              fontSize: "14px",
            }}
          />

          <button
            type="submit"
            disabled={loading}
            style={{
              width: "100%",
              padding: "10px",
              borderRadius: "6px",
              border: "none",
              backgroundColor: "#1e40af",
              color: "#fff",
              fontWeight: "bold",
              cursor: "pointer",
            }}
          >
            {loading ? "Logging in..." : "Log In"}
          </button>
        </form>
      </div>
    </div>
  );
}