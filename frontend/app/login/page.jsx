"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useUser } from "../../context/UserContext";

export default function LoginPage() {
  const router = useRouter();
  const { loginUser } = useUser();

  const [mode, setMode] = useState("login"); // NEW: login or register

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isChild, setIsChild] = useState(false); // NEW for register
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  // ------------------------------
  // LOGIN
  // ------------------------------
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

      const res = await fetch("http://localhost:8000/user/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        credentials: "include",
        body: formData.toString(),
      });

      if (!res.ok) {
        const errData = await res.json();
        setMessage(errData.detail || "Login failed.");
        setLoading(false);
        return;
      }

      const userRes = await fetch("http://localhost:8000/user/me", {
        credentials: "include",
      });

      if (!userRes.ok) {
        setMessage("Failed to fetch user info after login.");
        setLoading(false);
        return;
      }

      const userData = await userRes.json();
      loginUser(userData);

      setMessage("Login successful!");
      router.push("/recommendations");
    } catch (err) {
      console.error(err);
      setMessage("Login failed. Check console for details.");
    } finally {
      setLoading(false);
    }
  };

  // ------------------------------
  // REGISTER  (NEW)
  // ------------------------------
  const handleRegister = async (e) => {
    e.preventDefault();
    setMessage("");

    if (!username || !password) {
      setMessage("Please enter both username and password.");
      return;
    }

    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/user/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          name: username,
          password: password,
          is_child: isChild,
        }),
      });

      if (!res.ok) {
        const errData = await res.json();
        if (Array.isArray(errData.detail)) {
          setMessage(errData.detail.map( e => e.msg).join(", "));
        } else {
          setMessage(errData.detail || "Registration failed.");
        }
        setLoading(false);
        return;
      }

      const data = await res.json();

      // Auto-login after register
      loginUser({ name: data.name, user_id: data.user_id });
      setMessage("Registration successful! Redirecting...");
      setTimeout(() => router.push("/recommendations"), 800);
    } catch (err) {
      console.error(err);
      setMessage("Registration failed. Check console for details.");
    } finally {
      setLoading(false);
    }
  };

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

        {/* Toggle Login / Register */}
        <div style={{ textAlign: "center", marginBottom: 16 }}>
          <button
            onClick={() => setMode("login")}
            style={{
              marginRight: 8,
              padding: "6px 12px",
              borderRadius: 6,
              cursor: "pointer",
              backgroundColor: mode === "login" ? "#1e40af" : "#f0f0f0",
              color: mode === "login" ? "#fff" : "#000",
            }}
          >
            Login
          </button>

          <button
            onClick={() => setMode("register")}
            style={{
              padding: "6px 12px",
              borderRadius: 6,
              cursor: "pointer",
              backgroundColor: mode === "register" ? "#1e40af" : "#f0f0f0",
              color: mode === "register" ? "#fff" : "#000",
            }}
          >
            Register
          </button>
        </div>

        {message && (
          <div
            style={{
              marginBottom: "16px",
              padding: "10px",
              borderRadius: "6px",
              color: message.includes("successful") ? "#155724" : "#721c24",
              backgroundColor: message.includes("successful")
                ? "#d4edda"
                : "#f8d7da",
              border: message.includes("successful")
                ? "1px solid #c3e6cb"
                : "1px solid #f5c6cb",
              textAlign: "center",
              fontSize: "14px",
            }}
          >
            {message}
          </div>
        )}

        <form onSubmit={mode === "login" ? handleLogin : handleRegister}>
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
              marginBottom: mode === "register" ? "12px" : "24px",
              fontSize: "14px",
            }}
          />

          {/* Only show "Is child" checkbox in register mode */}
          {mode === "register" && (
            <label style={{ display: "block", marginBottom: "16px" }}>
              <input
                type="checkbox"
                checked={isChild}
                onChange={() => setIsChild(!isChild)}
                style={{ marginRight: 8 }}
              />
              Is child account
            </label>
          )}

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
            {loading
              ? mode === "login"
                ? "Logging in..."
                : "Registering..."
              : mode === "login"
              ? "Log In"
              : "Register"}
          </button>
        </form>
      </div>
    </div>
  );
}
