"use client";

import { useState, useEffect } from "react";
import { useUser } from "../../context/UserContext";
import { useRouter } from "next/navigation";

export default function ManageAccount() {
  const { user, loading } = useUser();
  const router = useRouter();

  const [content, setContent] = useState([]); // now holding subcategories
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
      const resCat = await fetch("http://localhost:8000/BackendFunctions/preference-categories", {
        credentials: "include",
      });
      const catData = await resCat.json();
      setCategories(Array.isArray(catData) ? catData : []);

      // Fetch sub-categories
      const resSubCat = await fetch("http://localhost:8000/BackendFunctions/preference-sub-categories", {
        credentials: "include",
      });
      const subcatData = await resSubCat.json();
      setContent(Array.isArray(subcatData) ? subcatData : []);

      // Fetch user info + preferences
      const userRes = await fetch("http://localhost:8000/user/me", {
        credentials: "include",
      });
      const userData = await userRes.json();

      setSelectedCat(Array.isArray(userData.liked_cat) ? userData.liked_cat : []);
      setSelectedSubCat(Array.isArray(userData.liked_subcat) ? userData.liked_subcat : []);
    } catch (err) {
      console.error("Error fetching content or preferences:", err);
    }
  };

  const handleSave = async () => {
    try {
      await fetch("http://localhost:8000/user/update-preferences", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          categories: selectedCat,
          subcategories: selectedSubCat,
        }),
      });
      
      //refresh recommendations immediately after updating preferences
      await fetch("http://localhost:8000/BackendFunctions/refresh-recommendations", {
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

  // Updated content with subcategories
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
