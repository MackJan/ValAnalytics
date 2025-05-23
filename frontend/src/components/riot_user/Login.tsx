import React, { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { RiotLoginButton } from './RiotLoginButton';
import { RiotCallback } from './RiotCallback';

const CLIENT_ID = 'your-riot-client-id-here';

export const Login: React.FC = () => {
  const [token, setToken] = useState<string | null>(null);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/auth/callback" element={<RiotCallback />} />

        <Route
          path="*"
          element={
            <div style={{ padding: 20 }}>
              {token ? (
                <>
                  <h1>Welcome back!</h1>
                  <pre>{token}</pre>
                </>
              ) : (
                <RiotLoginButton
                  clientId={CLIENT_ID}
                  onToken={setToken}
                />
              )}
            </div>
          }
        />
      </Routes>
    </BrowserRouter>
  );
};

export default Login;