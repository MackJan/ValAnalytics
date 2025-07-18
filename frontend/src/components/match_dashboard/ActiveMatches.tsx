import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { activeMatchApi, type ActiveMatch } from '../../api';

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
            setActiveMatches(matches);
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
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white flex items-center justify-center">
                <div className="text-center">
                    <h2 className="text-2xl font-bold text-purple-400 mb-4">Active Matches</h2>
                    <div className="text-gray-400">Loading active matches...</div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white p-6">
            <div className="max-w-7xl mx-auto">
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">Active Matches</h2>
                    <button
                        onClick={fetchActiveMatches}
                        className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-all duration-200"
                    >
                        Refresh
                    </button>
                </div>

                {error && (
                    <div className="bg-red-600/20 border border-red-600 text-red-400 p-4 rounded-lg mb-6">
                        {error}
                    </div>
                )}

                {activeMatches.length === 0 ? (
                    <div className="text-center text-gray-400 py-12">
                        No active matches currently being tracked.
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {activeMatches.map((match) => (
                            <div
                                key={match.id}
                                className="bg-slate-800/60 backdrop-blur-sm border border-slate-700 p-6 rounded-xl hover:bg-slate-800/80 transition-all duration-200"
                            >
                                <div className="mb-4">
                                    <h3 className="text-xl font-bold text-purple-400">{match.game_mode} - {match.game_map}</h3>
                                    <p className="text-gray-400">Started {formatTime(match.created_at)}</p>
                                    <p className="text-gray-500 text-sm">UUID: {match.match_uuid}</p>
                                </div>
                                <button
                                    onClick={() => handleWatchMatch(match.match_uuid)}
                                    className="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-all duration-200"
                                >
                                    Watch Live
                                </button>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default ActiveMatches;
