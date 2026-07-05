// frontend/lib/api.js

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default API_BASE;

// ------------------------------------
// Helper — unified request function
// ------------------------------------
async function request(endpoint, method = "GET", body = null) {
  const options = {
    method,
    credentials: "include", // REQUIRED for cookies
    headers: {},
  };

  if (body instanceof FormData) {
    options.body = body; // Browser sets headers automatically
  } else if (body) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body);
  }

  const res = await fetch(`${API_BASE}${endpoint}`, options);

  if (!res.ok) {
    const error = await res.text();
    throw new Error(`API Error ${res.status}: ${error}`);
  }

  try {
    return await res.json();
  } catch {
    return {};
  }
}

// ------------------------------------
// REGISTER
// ------------------------------------
export async function registerUser(name, password, is_child) {
  return await request("/user/register", "POST", {
    name,
    password,
    is_child,
  });
}

// ------------------------------------
// LOGIN — OAuth2 FormData
// ------------------------------------
export async function login(username, password) {
  const form = new FormData();
  form.append("username", username);
  form.append("password", password);

  return await request("/user/login", "POST", form);
}

// ------------------------------------
// LOGOUT
// ------------------------------------
export async function logout() {
  return await request("/user/logout", "POST");
}

// ------------------------------------
// GET CURRENT USER
// ------------------------------------
export async function fetchCurrentUser() {
  return await request("/user/me", "GET");
}

// ------------------------------------
// GET RECOMMENDATIONS
// ------------------------------------
export async function getRecommendations() {
  return await request("/user/get-recommendations", "POST");
}

// ------------------------------------
// STORE USER INTERACTION
// ------------------------------------
export async function storeInteraction(content_id, interaction_type) {
  return await request("/user/store-interaction", "POST", {
    content_id,
    interaction_type,
  });
}

// ------------------------------------
// UPDATE USER PREFERENCES (NEW)
// ------------------------------------
export async function updatePreferences(selected_categories) {
  return await request("/user/update-preferences", "POST", {
    categories: selected_categories,
  });
}
