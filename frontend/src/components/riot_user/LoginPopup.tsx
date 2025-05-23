import React, { useState } from 'react';

export const LoginPopup: React.FC = () => {
  const [loading, setLoading] = useState(false);

  const performLogin = async () => {
    setLoading(true);
    try {
      // e.g. call your API for credentials / OAuth flow
      const response = await fetch('/api/auth/login', { method: 'POST' /*...*/ });
      const { token } = await response.json();

      // tell the opener window
      window.opener?.postMessage(
        { type: 'LOGIN_SUCCESS', token },
        window.location.origin
      );
    } catch (err) {
      console.error(err);
      // you could post a failure message here too
    } finally {
      setLoading(false);
      // then close the popup
      window.close();
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>Log In</h2>
      {/* your form goes here; for demo we just trigger login immediately */}
      <button onClick={performLogin} disabled={loading}>
        {loading ? 'Logging in…' : 'Log In'}
      </button>
    </div>
  );
};
