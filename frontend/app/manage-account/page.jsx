"use client";

import API_BASE from "../../lib/api";
import { useState, useEffect } from "react";
import { useUser } from "../../context/UserContext";
import { useRouter } from "next/navigation";

export default function ManageAccount() {
  const { user, loading } = useUser();
  const router = useRouter();

  const [content, setContent] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCat, setSelectedCat] = useState([]);
  const [selectedSubCat, setSelectedSubCat] = useState([]);

  useEffect(() => {
    if (!loading && !user) {
      router.push("/login");
    } else if (user) {
      fetchData();
    }
  }, [user, loading]);

  const fetchData = async () => {
    try {
      // -----------------------------
      // Fetch categories
      // -----------------------------
      const resCat = await fetch(
        `${API_BASE}/BackendFunctions/preference-categories`,
        { credentials: "include" }
      );
      const catData = await resCat.json();

      setCategories(
        Array.isArray(catData)
          ? catData.map((c) => c.trim())
          : []
      );

      // -----------------------------
      // Fetch subcategories
      // -----------------------------
      const resSubCat = await fetch(
        `${API_BASE}/BackendFunctions/preference-sub-categories`,
        { credentials: "include" }
      );
      const subcatData = await resSubCat.json();

      setContent(Array.isArray(subcatData) ? subcatData : []);

      // -----------------------------
      // Fetch user preferences
      // -----------------------------
      const userRes = await fetch(`${API_BASE}/user/me`, {
        credentials: "include",
      });
      const userData = await userRes.json();

      setSelectedCat(
        userData.liked_cat
          ? userData.liked_cat.split(",").map((x) => x.trim()).filter(Boolean)
          : []
      );

      setSelectedSubCat(
        userData.liked_subcat
          ? userData.liked_subcat.split(",").map((x) => x.trim()).filter(Boolean)
          : []
      );
    } catch (err) {
      console.error("Error fetching content or preferences:", err);
    }
  };

  const handleSave = async () => {
    try {
      await fetch(`${API_BASE}/user/update-preferences`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          categories: selectedCat,
          subcategories: selectedSubCat,
        }),
      });

      await fetch(`${API_BASE}/BackendFunctions/refresh-recommendations`, {
        method: "POST",
        credentials: "include",
      });

      alert("Preferences saved and recommendations updated!");
      router.push("/recommendations");
    } catch (err) {
      console.error(err);
      alert("Failed to save preferences");
    }
  };

  // -----------------------------
  // Build subcategories
  // -----------------------------
  const subCategories = content
    .filter((c) =>
      selectedCat.includes(c.category?.trim())
    )
    .map((c) => c.sub_category?.trim());

  return (
    <div style={{ padding: 24 }}>
      <h1>Manage Preferences</h1>

      {/* ---------------- CATEGORY CHECKBOXES ---------------- */}
      <h3>Select Categories:</h3>

      {categories.map((cat) => (
        <label key={cat} style={{ display: "block" }}>
          <input
            type="checkbox"
            checked={selectedCat.includes(cat.trim())}
            onChange={() => {
              const normalized = cat.trim();

              const updatedCats = selectedCat.includes(normalized)
                ? selectedCat.filter((c) => c !== normalized)
                : [...selectedCat, normalized];

              setSelectedCat(updatedCats);
              setSelectedSubCat([]); // reset subcategories
            }}
          />{" "}
          {cat}
        </label>
      ))}

      {/* ---------------- SUBCATEGORY CHECKBOXES ---------------- */}
      {selectedCat.length > 0 && (
        <>
          <h3>Select Subcategories:</h3>

          {[...new Set(subCategories)].map((sub) => (
            <label key={sub} style={{ display: "block" }}>
              <input
                type="checkbox"
                checked={selectedSubCat.includes(sub?.trim())}
                onChange={() => {
                  const normalized = sub.trim();

                  setSelectedSubCat(
                    selectedSubCat.includes(normalized)
                      ? selectedSubCat.filter((s) => s !== normalized)
                      : [...selectedSubCat, normalized]
                  );
                }}
              />{" "}
              {sub}
            </label>
          ))}
        </>
      )}

      <button onClick={handleSave} style={{ marginTop: 16 }}>
        Save Preferences
      </button>
    </div>
  );
}