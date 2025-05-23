import api from "../api";

// src/services/auth.ts
export interface RiotAuthPayload {
  type: "auth";
  language: "de";
  remember: boolean;
  riot_identity: {
    username: string;
    password: string;
    captcha: string;
  };
}

export async function loginWithRiot(
  username: string,
  password: string,
  hcaptchaToken: string
) {
  const payload: RiotAuthPayload = {
    type: "auth",
    language: "de",
    remember: true,
    riot_identity: { username, password, captcha: hcaptchaToken },
  };
  return api.post("/api/riot_login/", payload);
}
