import type {MatchData} from "./Dashboard.tsx";

const IngameDashboard: React.FC<{ matchData: MatchData }> = ({ matchData }) => {
    const {match} = matchData;

    return (
        <div className="min-h-screen bg-gray-900 text-white p-6">
            <div className="max-w-6xl mx-auto">
                {/* Header Section */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-purple-400 mb-2">Live Match Dashboard</h1>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        <div className="bg-gray-800 p-4 rounded-lg">
                            <h3 className="text-sm text-gray-400">Match ID</h3>
                            <p className="truncate">{match.MatchID}</p>
                        </div>
                        <div className="bg-gray-800 p-4 rounded-lg">
                            <h3 className="text-sm text-gray-400">Status</h3>
                            <p className={`font-semibold ${
                                match.State === 'IN_PROGRESS' ? 'text-green-400' :
                                    match.State === 'COMPLETED' ? 'text-blue-400' : 'text-yellow-400'
                            }`}>
                                {match.State.replace('_', ' ')}
                            </p>
                        </div>
                        <div className="bg-gray-800 p-4 rounded-lg">
                            <h3 className="text-sm text-gray-400">Map</h3>
                            <p>{match.MapID}</p>
                        </div>
                        <div className="bg-gray-800 p-4 rounded-lg">
                            <h3 className="text-sm text-gray-400">Mode</h3>
                            <p>{match.ModeID}</p>
                        </div>
                    </div>
                </div>

                {/* Match Stats Section */}
                <div className="mb-8 bg-gray-800 rounded-lg p-6">
                    <h2 className="text-2xl font-bold text-purple-400 mb-4">Match Statistics</h2>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                        <div className="bg-gray-700 p-4 rounded-lg">
                            <h3 className="text-sm text-gray-400">Game State</h3>
                            <p className="text-xl font-semibold">
                                {match.match_stats.sessionLoopState}
                            </p>
                        </div>
                        <div className="bg-gray-700 p-4 rounded-lg">
                            <h3 className="text-sm text-gray-400">Ally Score</h3>
                            <p className="text-xl font-semibold text-blue-400">
                                {match.match_stats.partyOwnerMatchScoreAllyTeam}
                            </p>
                        </div>
                        <div className="bg-gray-700 p-4 rounded-lg">
                            <h3 className="text-sm text-gray-400">Enemy Score</h3>
                            <p className="text-xl font-semibold text-red-400">
                                {match.match_stats.partyOwnerMatchScoreEnemyTeam}
                            </p>
                        </div>
                    </div>

                    {/* Players Section */}
                    <h3 className="text-xl font-semibold mb-3">Players ({match.Players.length})</h3>
                    <div className="overflow-x-auto">
                        <table className="min-w-full bg-gray-700 rounded-lg overflow-hidden">
                            <thead className="bg-gray-600">
                            <tr>
                                <th className="px-4 py-3 text-left">Team</th>
                                <th className="px-4 py-3 text-left">Player</th>
                                <th className="px-4 py-3 text-left">Level</th>
                                <th className="px-4 py-3 text-left">Character</th>
                                <th className="px-4 py-3 text-left">Wins</th>
                            </tr>
                            </thead>
                            <tbody>
                            {match.Players.map((player) => (
                                <tr key={player.Subject} className="border-t border-gray-600 hover:bg-gray-600">
                                    <td className={`px-4 py-3 font-medium ${
                                        player.TeamID === 'Red' ? 'text-red-400' : 'text-blue-400'
                                    }`}>
                                        {player.TeamID}
                                    </td>
                                    <td className="px-4 py-3">
                                        <div className="flex items-center">
                                            <div className="flex-shrink-0 h-8 w-8 bg-gray-500 rounded-full mr-3">
                                                <img
                                                    src={player.AgentIcon}
                                                    alt={player.CharacterID}
                                                    className="h-8 w-8 rounded-full"
                                                />
                                            </div>
                                            <div>
                                                <p className="font-medium">{player.Name}</p>
                                                <p className="text-xs text-gray-400">{player.PlatformType || 'PC'}</p>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-4 py-3">{player.PlayerIdentity.AccountLevel}</td>
                                    <td className="px-4 py-3">
                                        {typeof player.CharacterID === 'object'
                                            ? JSON.stringify(player.CharacterID)
                                            : player.CharacterID}
                                    </td>
                                    <td className="px-4 py-3">{player.SeasonalBadgeInfo.NumberOfWins}</td>
                                </tr>
                            ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default IngameDashboard;