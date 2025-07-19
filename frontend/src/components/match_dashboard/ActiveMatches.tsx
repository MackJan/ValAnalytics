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
            // Ensure we always have an array
            if (Array.isArray(matches)) {
                setActiveMatches(matches);
            } else {
                console.error('API returned non-array data:', matches);
                setActiveMatches([]);
                setError('Invalid data format received from server');
            }
        } catch (err) {
            setError('Failed to fetch active matches');
            console.error('Error fetching active matches:', err);
            // Ensure activeMatches stays as an empty array on error
            setActiveMatches([]);
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
            <div className="min-h-screen bg-gray-100 p-8">
                <div className="max-w-6xl mx-auto">
                    <div className="bg-white rounded-3xl shadow-sm border border-gray-200 p-8">
                        <div className="text-center">
                            <h2 className="text-3xl font-bold text-gray-800 mb-4">Active Matches</h2>
                            <div className="text-gray-500">Loading active matches...</div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-100 p-8">
            <div className="max-w-6xl mx-auto space-y-6">
                {/* Header Card */}
                <div className="bg-white rounded-3xl shadow-sm border border-gray-200 p-8">
                    <div className="flex items-center justify-between">
                        <div>
                            <h2 className="text-3xl font-bold text-gray-800 mb-2">Active Matches</h2>
                            <p className="text-gray-500">Currently tracked live matches</p>
                        </div>
                        <button
                            onClick={fetchActiveMatches}
                            className="px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-all duration-200 font-medium"
                        >
                            Refresh
                        </button>
                    </div>
                </div>

                {error && (
                    <div className="bg-white rounded-3xl shadow-sm border border-red-200 p-6">
                        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl">
                            {error}
                        </div>
                    </div>
                )}

                {activeMatches.length === 0 ? (
                    <div className="bg-white rounded-3xl shadow-sm border border-gray-200 p-12">
                        <div className="text-center text-gray-500">
                            <div className="text-xl font-medium mb-2">No Active Matches</div>
                            <div>No matches are currently being tracked.</div>
                        </div>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {activeMatches.map((match) => (
                            <div
                                key={match.id}
                                className="bg-white rounded-3xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-all duration-200"
                            >
                                <div className="p-6">
                                    <div className="mb-6">
                                        <h3 className="text-xl font-bold text-gray-800 mb-2">
                                            {match.game_mode} - {match.game_map}
                                        </h3>
                                        <p className="text-gray-500 mb-1">Started {formatTime(match.created_at)}</p>
                                        <p className="text-gray-400 text-sm font-mono">
                                            {match.match_uuid.slice(0, 8)}...
                                        </p>
                                    </div>
                                    <button
                                        onClick={() => handleWatchMatch(match.match_uuid)}
                                        className="w-full px-4 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-all duration-200 font-medium"
                                    >
                                        Watch Live
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default ActiveMatches;
