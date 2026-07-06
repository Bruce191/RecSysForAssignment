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
      // Fetch categories
      const resCat = await fetch(
        `${API_BASE}/BackendFunctions/preference-categories`,
        { credentials: "include" }
      );
      const catData = await resCat.json();
      setCategories(Array.isArray(catData) ? catData : []);

      // Fetch sub-categories
      const resSubCat = await fetch(
        `${API_BASE}/BackendFunctions/preference-sub-categories`,
        { credentials: "include" }
      );
      const subcatData = await resSubCat.json();
      setContent(Array.isArray(subcatData) ? subcatData : []);

      // Fetch user info + preferences
      const userRes = await fetch(`${API_BASE}/user/me`, {
        credentials: "include",
      });
      const userData = await userRes.json();

      // ✅ FIX: convert comma-separated string → array
      setSelectedCat(
        userData.liked_cat
          ? userData.liked_cat.split(",").filter(Boolean)
          : []
      );

      setSelectedSubCat(
        userData.liked_subcat
          ? userData.liked_subcat.split(",").filter(Boolean)
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

      // refresh recommendations immediately after updating preferences
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

  // Build subcategories based on selected categories
  const subCategories = content
    .filter((c) => selectedCat.includes(c.category))
    .map((c) => c.sub_category);

  return (
    <div style={{ padding: 24 }}>
      <h1>Manage Preferences</h1>

      <h3>Select Categories:</h3>
      {categories.map((cat) => (
        <label key={cat} style={{ display: "block" }}>
          <input
            type="checkbox"
            checked={selectedCat.includes(cat)}
            onChange={() => {
              const updatedCats = selectedCat.includes(cat)
                ? selectedCat.filter((c) => c !== cat)
                : [...selectedCat, cat];

              setSelectedCat(updatedCats);
              setSelectedSubCat([]); // reset subcategories
            }}
          />{" "}
          {cat}
        </label>
      ))}

      {selectedCat.length > 0 && (
        <>
          <h3>Select Subcategories:</h3>
          {[...new Set(subCategories)].map((sub) => (
            <label key={sub} style={{ display: "block" }}>
              <input
                type="checkbox"
                checked={selectedSubCat.includes(sub)}
                onChange={() => {
                  setSelectedSubCat(
                    selectedSubCat.includes(sub)
                      ? selectedSubCat.filter((s) => s !== sub)
                      : [...selectedSubCat, sub]
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