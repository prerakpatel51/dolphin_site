import { createContext, useContext, useEffect, useState } from "react";
import { api, clearTokens } from "./api.js";

const AuthCtx = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  async function refresh() {
    try { setUser(await api.me()); } catch { setUser(null); }
    finally { setLoading(false); }
  }

  useEffect(() => { refresh(); }, []);

  async function login(email, password) {
    await api.login(email, password);
    await refresh();
  }
  async function signup(data) {
    await api.signup(data);
    await login(data.email, data.password);
  }
  async function logout() {
    try {
      await clearTokens();
    } finally {
      setUser(null);
    }
  }
  async function deleteAccount() {
    await api.deleteMe();
    await logout();
  }

  return (
    <AuthCtx.Provider value={{ user, loading, login, signup, logout, deleteAccount, refresh }}>
      {children}
    </AuthCtx.Provider>
  );
}

export const useAuth = () => useContext(AuthCtx);
