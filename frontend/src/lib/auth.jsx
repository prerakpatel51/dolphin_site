import { createContext, useContext, useEffect, useRef, useState } from "react";
import { api, clearTokens } from "./api.js";

const AuthCtx = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const refreshSeq = useRef(0);

  async function refresh() {
    const seq = ++refreshSeq.current;
    try {
      const nextUser = await api.me();
      if (seq === refreshSeq.current) setUser(nextUser);
    } catch {
      if (seq === refreshSeq.current) setUser(null);
    } finally {
      if (seq === refreshSeq.current) setLoading(false);
    }
  }

  useEffect(() => { refresh(); }, []);

  async function login(email, password) {
    await api.login(email, password);
    await refresh();
  }
  async function signup(data) {
    await api.signup(data);
    try {
      await login(data.email, data.password);
    } catch (err) {
      console.error("Auto-login after signup failed", err);
    }
  }
  async function logout() {
    const seq = ++refreshSeq.current;
    try {
      await clearTokens();
    } finally {
      if (seq === refreshSeq.current) {
        setUser(null);
        setLoading(false);
      }
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
