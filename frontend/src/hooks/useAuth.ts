import { useEffect, useState } from "react";
import { me } from "../api/auth";
import type { User } from "../types";

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("laudoia_token");
    if (!token) {
      setLoading(false);
      return;
    }

    me()
      .then(setUser)
      .catch(() => {
        localStorage.removeItem("laudoia_token");
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  return { user, setUser, loading };
}
