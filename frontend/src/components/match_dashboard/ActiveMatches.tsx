import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { activeMatchApi, type ActiveMatch } from '../../api';
import './ActiveMatches.css';

const ActiveMatches: React.FC = () => {
    const [activeMatches, setActiveMatches] = useState<ActiveMatch[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const navigate = useNavigate();

    useEffect(() => {
        fetchActiveMatches();
        // Set up auto-refresh every 30 seconds
        const interval = setInterval(fetchActiveMatches, 30000);
        return () => clearInterval(interval);
    }, []);

    const fetchActiveMatches = async () => {
        try {
            setError(null);
            const matches = await activeMatchApi.getActiveMatches();
            // Filter out ended matches for the active list
            const ongoingMatches = matches.filter(match => !match.ended_at);
            setActiveMatches(ongoingMatches);
        } catch (err) {
            setError('Failed to fetch active matches');
            console.error('Error fetching active matches:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleWatchMatch = (matchUuid: string) => {
        navigate(`/live/${matchUuid}`);
    };

    const formatTime = (dateString: string): string => {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffMins = Math.floor(diffMs / 60000);

        if (diffMins < 1) return 'Just started';
        if (diffMins < 60) return `${diffMins}m ago`;

        const diffHours = Math.floor(diffMins / 60);
        return `${diffHours}h ${diffMins % 60}m ago`;
    };

    if (loading) {
        return (
            <div className="active-matches-container">
                <h2>Active Matches</h2>
                <div className="loading">Loading active matches...</div>
            </div>
        );
    }

    return (
        <div className="active-matches-container">
            <div className="header">
                <h2>Active Matches</h2>
                <button onClick={fetchActiveMatches} className="refresh-btn">
                    Refresh
                </button>
            </div>

            {error && (
                <div className="error-message">
                    {error}
                </div>
            )}

            {activeMatches.length === 0 ? (
                <div className="no-matches">
                    <p>No active matches currently being tracked.</p>
                </div>
            ) : (
                <div className="matches-grid">
                    {activeMatches.map((match) => (
                        <div key={match.id} className="match-card">
                            <div className="match-info">
                                <h3>Match {match.match_uuid.slice(-8)}</h3>
                                <p className="match-time">Started {formatTime(match.started_at)}</p>
                                <p className="match-uuid">UUID: {match.match_uuid}</p>
                            </div>
                            <div className="match-actions">
                                <button
                                    onClick={() => handleWatchMatch(match.match_uuid)}
                                    className="watch-btn"
                                >
                                    Watch Live
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default ActiveMatches;
