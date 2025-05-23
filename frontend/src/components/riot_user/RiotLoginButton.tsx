// src/components/RiotLoginButton.tsx
import React, { useEffect, useRef } from 'react';
import { openPopup } from './openPopup';

interface Props {
  clientId: string;
  onToken: (token: string) => void;
}

export const RiotLoginButton: React.FC<Props> = ({ clientId, onToken }) => {
  const popupRef = useRef<Window | null>(null);

  const handleClick = () => {
    const redirectUri = `${window.location.origin}/auth/callback`;
    const authUrl = [
      'https://auth.riotgames.com/authorize',
      `?client_id=${encodeURIComponent(clientId)}`,
      `&redirect_uri=${encodeURIComponent(redirectUri)}`,
      `&response_type=token`,
      `&scope=openid%20profile`
    ].join('');
    popupRef.current = openPopup(authUrl);
  };

  useEffect(() => {
    const onMessage = (e: MessageEvent) => {
      if (e.origin !== window.location.origin) return;
      if (e.data.type === 'RIOT_AUTH_TOKEN' && typeof e.data.token === 'string') {
        onToken(e.data.token);
        popupRef.current?.close();
      }
    };
    window.addEventListener('message', onMessage);
    return () => window.removeEventListener('message', onMessage);
  }, [onToken]);

  return <button onClick={handleClick}>Login with Riot</button>;
};
