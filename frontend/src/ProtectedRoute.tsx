import { Navigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode";
import api from "./api";
import { ACCESS_TOKEN } from "./constants";
import { REFRESH_TOKEN } from "./constants";
import { useState, useEffect } from "react";
import type {ReactNode} from "react";

function ProtectedRoute({ children }: { children: ReactNode }) {
  const [isAuthorized, setIsAuthorized] = useState<boolean>(false);

  useEffect(() => {
    auth().catch(() => setIsAuthorized(false));
  }, []);

  const refreshToken = async () => {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN);
    try {
      const res = await api.post("/atpi/token/refresh/", {
        refresh: refreshToken,
      });
      if (res.status === 200) {
        localStorage.setItem(ACCESS_TOKEN, res.data.access);
        return;
      } else {
        console.log("Failed to refresh token");
        setIsAuthorized(false);
      }
    } catch {
      console.log("Failed to refresh token");
      setIsAuthorized(false);
    }
  };

  const auth = async () => {
    const token = localStorage.getItem(ACCESS_TOKEN);
    if (!token) {
      setIsAuthorized(false);
      return;
    }
    const decoded = jwtDecode(token);
    const tokenExp = decoded.exp;
    const currentTime = Date.now() / 1000;
    if (tokenExp && tokenExp < currentTime) {
      await refreshToken();
    }
    if (!token) {
      setIsAuthorized(false);
      return;
    }

    setIsAuthorized(true);
  };

  if (isAuthorized === null) return <p>Checking authentication...</p>;
  return isAuthorized ? children : <Navigate to="/MC/login" />;
}

export default ProtectedRoute;
