import React from 'react';
import type {MatchData} from "./Dashboard.tsx";
import {useNavigate} from "react-router-dom";

const IngameDashboard: React.FC<{ matchData: MatchData }> = ({matchData}) => {
    const navigate = useNavigate();

    const {match} = matchData;

    const team1Score = match.party_owner_enemy_score;
    const team2Score = match.party_owner_score;
    const partyOwnerTeamId = match.party_owner_team_id;
    const team1Players = match.players?.filter((p) => p.team_id !== partyOwnerTeamId) || [];
    const team2Players = match.players?.filter((p) => p.team_id === partyOwnerTeamId) || [];

    return (
        <div className="min-h-screen bg-gray-100 p-8">
            <div className="max-w-6xl mx-auto space-y-6">
                <button
                    className="bg-blue-500 text-white px-4 py-2 rounded-lg shadow hover:bg-blue-600 transition duration-200"
                    onClick={() => {
                        navigate("/live");
                    }}>
                    <i className="fas fa-arrow-left mr-2"></i> Back to Dashboard
                </button>
                {/* Top Info Card - Single row layout matching the image */}
                <div className="bg-white rounded-3xl shadow-sm border border-gray-200 p-8">
                    <div className="grid grid-cols-3 gap-8 text-center">
                        <div>
                            <div className="text-sm text-gray-500 mb-3 font-medium">Map</div>
                            <div className="text-xl font-semibold text-gray-800">{match.game_map}</div>
                        </div>

                        <div>
                            <div className="text-sm text-gray-500 mb-6 font-medium">Current Score</div>
                            <div className="flex items-center justify-center space-x-6">
                                <div
                                    className="flex items-center justify-center w-14 h-14 bg-blue-500 rounded-full shadow-lg">
                                    <span className="text-white font-bold text-xl">{team2Score}</span>
                                </div>
                                <div
                                    className="flex items-center justify-center w-14 h-14 bg-red-500 rounded-full shadow-lg">
                                    <span className="text-white font-bold text-xl">{team1Score}</span>
                                </div>
                            </div>
                        </div>

                        <div>
                            <div className="text-sm text-gray-500 mb-3 font-medium">Gamemode</div>
                            <div className="text-xl font-semibold text-gray-800">{match.game_mode}</div>
                        </div>
                    </div>
                </div>

                {/* Teams Container - Two columns matching the image layout */}
                <div className="grid grid-cols-2 gap-8">
                    {/* Team 2 (blue/Right) */}
                    <div className="bg-white rounded-3xl shadow-sm border border-gray-200 overflow-hidden">
                        <div className="p-6 border-b border-gray-100 bg-gray-50">
                            <div className="flex items-center justify-center space-x-3">
                                <div className="w-5 h-5 bg-blue-500 rounded-full"></div>
                                <span
                                    className="font-semibold text-gray-800 text-lg">Average Rank: {match.party_owner_average_rank || "Unranked"}</span>
                            </div>
                        </div>

                        <div className="p-6 space-y-4">
                            {team2Players.map((player) => (
                                <div key={player.subject}
                                     className="flex items-center justify-between p-4 bg-blue-50 rounded-2xl border border-blue-100">
                                    <div className="flex items-center space-x-4">
                                        <div
                                            className="w-10 h-10 bg-blue-200 rounded-full flex items-center justify-center">
                                            <div
                                                className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                                                {player.agent_icon ? (
                                                    <img
                                                        src={player.agent_icon}
                                                        alt={player.character}
                                                        className="w-8 h-8 object-cover rounded-full"
                                                    />
                                                ) : (
                                                    <div className="w-4 h-4 bg-white rounded-full"></div>
                                                )}
                                            </div>
                                        </div>
                                        <div className="flex-1">
                                            <div
                                                className="font-semibold text-gray-800 text-lg">{player.game_name || "NameTag"}</div>
                                            <div className="text-sm text-gray-600">{player.character || "Agent"}</div>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <div
                                            className="text-sm font-semibold text-gray-800">{player.rank || "Unranked"}</div>
                                        <div className="text-xs text-gray-500">{player.account_level || "Hidden"}</div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                    {/* Team 1 (Red/Left) */}
                    <div className="bg-white rounded-3xl shadow-sm border border-gray-200 overflow-hidden">
                        <div className="p-6 border-b border-gray-100 bg-gray-50">
                            <div className="flex items-center justify-center space-x-3">
                                <div className="w-5 h-5 bg-red-500 rounded-full"></div>
                                <span
                                    className="font-semibold text-gray-800 text-lg">Average Rank: {match.party_owner_enemy_average_rank || "Unranked"}</span>
                            </div>
                        </div>

                        <div className="p-6 space-y-4">
                            {team1Players.map((player) => (
                                <div key={player.subject}
                                     className="flex items-center justify-between p-4 bg-red-50 rounded-2xl border border-red-100">
                                    <div className="flex items-center space-x-4">
                                        <div
                                            className="w-10 h-10 bg-red-200 rounded-full flex items-center justify-center">
                                            <div
                                                className="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center">
                                                {player.agent_icon ? (
                                                    <img
                                                        src={player.agent_icon}
                                                        alt={player.character}
                                                        className="w-8 h-8 object-cover rounded-full"
                                                    />
                                                ) : (
                                                    <div className="w-4 h-4 bg-white rounded-full"></div>
                                                )}
                                            </div>
                                        </div>
                                        <div className="flex-1">
                                            <div
                                                className="font-semibold text-gray-800 text-lg">{player.game_name || "NameTag"}</div>
                                            <div className="text-sm text-gray-600">{player.character || "Agent"}</div>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <div
                                            className="text-sm font-semibold text-gray-800">{player.rank || "Immortal 3"}</div>
                                        <div className="text-xs text-gray-500">{player.account_level || "Hidden"}</div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default IngameDashboard;