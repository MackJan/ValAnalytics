// src/pages/RiotCallback.tsx
import { useEffect } from 'react';

export const RiotCallback: React.FC = () => {
  useEffect(() => {
    // parse the URL hash: e.g. #access_token=XYZ&expires_in=...
    const hash = window.location.hash.substring(1);
    const params = new URLSearchParams(hash);
    const token = params.get('access_token');
    if (token) {
      window.opener?.postMessage(
        { type: 'RIOT_AUTH_TOKEN', token },
        window.location.origin
      );
    }
    // close popup (giving the message a moment to fire)
    setTimeout(() => window.close(), 100);
  }, []);

  return (
    <div style={{ padding: 20, fontFamily: 'sans-serif' }}>
      <h2>Logging you in…</h2>
      <p>If this page doesn’t close automatically, you can safely close it.</p>
    </div>
  );
};
