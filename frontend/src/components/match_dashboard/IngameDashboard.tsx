import React from 'react';
import type {MatchData, CurrentMatchPlayer} from "./Dashboard.tsx";

const IngameDashboard: React.FC<{ matchData: MatchData }> = ({matchData}) => {
    const {match} = matchData;

    const team1Score = match.party_owner_score;
    const team2Score = match.party_owner_enemy_score;

    const team1Players = match.players?.filter((p) => p.team_id === "Blue") || [];
    const team2Players = match.players?.filter((p) => p.team_id === "Red") || [];

    const getAverageRank = (players: CurrentMatchPlayer[]) => {
        if (players.length === 0) return "N/A";
        return "Placeholder"; // This would need actual rank calculation logic
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
            <div className="max-w-7xl mx-auto px-6 py-8">
                {/* Header Section */}
                <div className="mb-8">
                    <div className="flex items-center justify-between mb-6">
                        <div>
                            <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
                                Live Match Dashboard
                            </h1>
                            <p className="text-gray-400">Real-time match information</p>
                        </div>
                        <div className="flex items-center space-x-2">
                            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                            <span className="text-sm text-gray-400">Live</span>
                        </div>
                    </div>

                    {/* Match Info Bar */}
                    <div className="bg-slate-800/60 backdrop-blur-sm border border-slate-700 p-6 rounded-xl mb-8">
                        <div className="flex items-center justify-between flex-wrap gap-4">
                            <div className="flex items-center space-x-6">
                                <div className="text-center">
                                    <div className="text-sm text-gray-400 mb-1">Map</div>
                                    <div className="text-lg font-semibold text-white">{match.game_map}</div>
                                </div>
                                <div className="text-center">
                                    <div className="text-sm text-gray-400 mb-1">Mode</div>
                                    <div className="text-lg font-semibold text-white">{match.game_mode}</div>
                                </div>
                                <div className="text-center">
                                    <div className="text-sm text-gray-400 mb-1">Status</div>
                                    <div className={`text-lg font-semibold ${match.state === "IN_PROGRESS" ? "text-green-400" : "text-red-400"}`}>
                                        {match.state === "IN_PROGRESS" ? "In Progress" : "Ended"}
                                    </div>
                                </div>
                            </div>
                            <div className="text-center">
                                <div className="text-sm text-gray-400 mb-1">Party Size</div>
                                <div className="text-lg font-semibold text-white">{match.party_size}</div>
                            </div>
                        </div>
                    </div>

                    {/* Score Section */}
                    <div className="bg-slate-800/60 backdrop-blur-sm border border-slate-700 p-6 rounded-xl mb-8">
                        <div className="text-center">
                            <div className="text-sm text-gray-400 mb-4 uppercase tracking-wider">Current Score</div>
                            <div className="flex items-center justify-center space-x-12">
                                <div className="text-center">
                                    <div className="text-5xl font-bold text-blue-400 mb-2">{team1Score}</div>
                                    <div className="text-lg text-gray-300">Team Blue</div>
                                </div>
                                <div className="text-2xl text-gray-500">-</div>
                                <div className="text-center">
                                    <div className="text-5xl font-bold text-red-400 mb-2">{team2Score}</div>
                                    <div className="text-lg text-gray-300">Team Red</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Teams Container */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Team 1 Panel */}
                    <div className="bg-slate-800/60 backdrop-blur-sm border border-slate-700 rounded-xl overflow-hidden">
                        {/* Team Header */}
                        <div className="bg-blue-600/20 border-b border-blue-600/30 p-6">
                            <div className="flex items-center justify-between">
                                <h2 className="text-2xl font-bold text-blue-400">Team Blue</h2>
                                <div className="text-blue-400 text-3xl font-bold">{team1Score}</div>
                            </div>
                            <div className="mt-2 text-sm text-gray-300">
                                Average Rank: {getAverageRank(team1Players)}
                            </div>
                        </div>

                        {/* Player List */}
                        <div className="p-6">
                            <div className="space-y-4">
                                {team1Players.length > 0 ? team1Players.map((player) => (
                                    <div
                                        key={player.subject}
                                        className="bg-slate-700/50 border border-slate-600 rounded-lg p-4 hover:bg-slate-700/70 transition-all duration-200"
                                    >
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center space-x-4">
                                                <div className="relative">
                                                    <div className="h-12 w-12 bg-gray-600 rounded-full flex items-center justify-center overflow-hidden border-2 border-blue-500">
                                                        <img
                                                            src={player.agent_icon}
                                                            alt={player.character}
                                                            className="h-full w-full object-cover"
                                                        />
                                                    </div>
                                                </div>
                                                <div>
                                                    <div className="text-white font-medium">{player.game_name}</div>
                                                    <div className="text-blue-400 text-sm">{player.character}</div>
                                                </div>
                                            </div>
                                            <div className="text-right">
                                                <div className="text-white font-medium">{player.rank}</div>
                                                <div className="text-gray-400 text-sm">Level {player.account_level || "N/A"}</div>
                                            </div>
                                        </div>
                                    </div>
                                )) : (
                                    <div className="text-center text-gray-400 py-8">
                                        No players found
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Team 2 Panel */}
                    <div className="bg-slate-800/60 backdrop-blur-sm border border-slate-700 rounded-xl overflow-hidden">
                        {/* Team Header */}
                        <div className="bg-red-600/20 border-b border-red-600/30 p-6">
                            <div className="flex items-center justify-between">
                                <h2 className="text-2xl font-bold text-red-400">Team Red</h2>
                                <div className="text-red-400 text-3xl font-bold">{team2Score}</div>
                            </div>
                            <div className="mt-2 text-sm text-gray-300">
                                Average Rank: {getAverageRank(team2Players)}
                            </div>
                        </div>

                        {/* Player List */}
                        <div className="p-6">
                            <div className="space-y-4">
                                {team2Players.length > 0 ? team2Players.map((player) => (
                                    <div
                                        key={player.subject}
                                        className="bg-slate-700/50 border border-slate-600 rounded-lg p-4 hover:bg-slate-700/70 transition-all duration-200"
                                    >
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center space-x-4">
                                                <div className="relative">
                                                    <div className="h-12 w-12 bg-gray-600 rounded-full flex items-center justify-center overflow-hidden border-2 border-red-500">
                                                        <img
                                                            src={player.agent_icon}
                                                            alt={player.character}
                                                            className="h-full w-full object-cover"
                                                        />
                                                    </div>
                                                </div>
                                                <div>
                                                    <div className="text-white font-medium">{player.game_name}</div>
                                                    <div className="text-red-400 text-sm">{player.character}</div>
                                                </div>
                                            </div>
                                            <div className="text-right">
                                                <div className="text-white font-medium">{player.rank}</div>
                                                <div className="text-gray-400 text-sm">Level {player.account_level || "N/A"}</div>
                                            </div>
                                        </div>
                                    </div>
                                )) : (
                                    <div className="text-center text-gray-400 py-8">
                                        No players found
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default IngameDashboard;