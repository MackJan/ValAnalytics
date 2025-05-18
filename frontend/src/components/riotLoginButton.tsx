import React, { useState } from 'react';
import { openAuthPopup } from './openAuthPopup.ts';
import type {AuthRedirectData} from "./parseAuthRedirect.ts";

const RiotLoginButton: React.FC = () => {
  const [authData, setAuthData] = useState<AuthRedirectData>();
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async () => {
    try {
      const data = await openAuthPopup();
      setAuthData(data);
      console.log(data);
    } catch (e: unknown) {
      if (e instanceof Error) {
        setError(e.message);
      } else {
        setError('An unknown error occurred');
      }
    }
  };

  return (
    <div>
      <button onClick={handleLogin}>Login with Riot</button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {authData && (
        <pre>{JSON.stringify(authData, null, 2)}</pre>
      )}
    </div>
  );
};

export default RiotLoginButton;