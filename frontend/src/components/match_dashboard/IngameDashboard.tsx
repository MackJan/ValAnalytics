import type {MatchData} from "./Dashboard.tsx";

const IngameDashboard: React.FC<{ matchData: MatchData }> = ({matchData}) => {
    const {match} = matchData;

    const team1Score = match.party_owner_score;
    const team2Score = match.party_owner_enemy_score;

    const team1Players = match.players?.filter((p) => p.team_id === "Blue") || [];
    const team2Players = match.players?.filter((p) => p.team_id === "Red") || [];

    return (
        <div className="min-h-screen bg-zinc-900 text-white p-6 flex flex-col items-center">
            {/* ── Score Section ───────────────────────────────────────────────────────── */}
            <div className="mb-6 flex flex-col items-center">
                <button className="mb-2 px-4 py-1 border border-gray-500 rounded-md text-gray-300 hover:bg-gray-800">
                    Score
                </button>

                <div className="flex items-center space-x-40">
                    <span className="text-3xl font-bold">{team1Score}</span>
                    <span className="text-3xl font-bold">{team2Score}</span>
                </div>
            </div>

            {/* ── Teams Container ───────────────────────────────────────────────────────── */}
            <div className="flex space-x-10">
                {/* ── Team 1 Panel ─────────────────────────────────────────────────── */}
                <div className="w-150 border border-gray-600 rounded-lg bg-zinc-800">
                    {/* Team Name */}
                    <div className="py-2 text-center">
                        <span className="text-lg font-bold">Team 1</span>
                    </div>

                    {/* Average Rank */}
                    <div className="px-4 flex items-center justify-center space-x-2 mb-4">
                        <span className="text-sm text-gray-300">Average Rank: Placeholder 3</span>
                    </div>

                    {/* Player List */}
                    <div className="space-y-2 px-2 pb-4">
                        {team1Players.length > 0 ? team1Players.map((player) => (
                            <div
                                key={player.subject}
                                className="flex items-center justify-between bg-zinc-700 rounded-lg px-3 py-2 hover:bg-zinc-600"
                            >
                                {/* Icon + Name#Tag */}
                                <div className="flex items-center space-x-3">
                                    <div
                                        className="h-8 w-8 bg-gray-600 rounded-full flex items-center justify-center overflow-hidden">
                                        <img
                                            src={player.agent_icon}
                                            alt={player.character}
                                            className="h-full w-full object-cover rounded-full"
                                        />
                                    </div>
                                    <span className="truncate">{player.game_name}</span>
                                </div>

                                {/* Agent */}
                                <span className="text-sm text-gray-300">{player.character}</span>

                                {/* Rank */}
                                <span className="text-sm text-gray-300">{player.rank}</span>

                                {/* Account Level */}
                                <div className="ml-2">
                                    <span className="bg-zinc-600 px-2 py-1 rounded text-sm">{player.account_level || "N/A"}</span>
                                </div>
                            </div>
                        )) : (
                            <div className="text-center text-gray-400 py-4">
                                No players found
                            </div>
                        )}
                    </div>
                </div>

                {/* ── Team 2 Panel ─────────────────────────────────────────────────── */}
                <div className="w-150 border border-gray-600 rounded-lg bg-zinc-800">
                    {/* Team Name */}
                    <div className="py-2 text-center">
                        <span className="text-lg font-bold">Team 2</span>
                    </div>

                    {/* Average Rank */}
                    <div className="px-4 flex items-center justify-center space-x-2 mb-4">
                        <span className="text-sm text-gray-300">Average Rank: PlaceHolder</span>
                    </div>

                    {/* Player List */}
                    <div className="space-y-2 px-2 pb-4">
                        {team2Players.length > 0 ? team2Players.map((player) => (
                            <div
                                key={player.subject}
                                className="flex items-center justify-between bg-zinc-700 rounded-lg px-3 py-2 hover:bg-zinc-600"
                            >
                                {/* Icon + Name#Tag */}
                                <div className="flex items-center space-x-3">
                                    <div
                                        className="h-8 w-8 bg-gray-600 rounded-full flex items-center justify-center overflow-hidden">
                                        <img
                                            src={player.agent_icon}
                                            alt={player.character}
                                            className="h-full w-full object-cover rounded-full"
                                        />
                                    </div>
                                    <span className="truncate">{player.game_name}</span>
                                </div>

                                {/* Agent */}
                                <span className="text-sm text-gray-300">{player.character}</span>

                                {/* Rank */}
                                <span className="text-sm text-gray-300">{player.rank}</span>

                                {/* Account Level */}
                                <div className="ml-2">
                                    <span className="bg-zinc-600 px-2 py-1 rounded text-sm">{player.account_level || "N/A"}</span>
                                </div>
                            </div>
                        )) : (
                            <div className="text-center text-gray-400 py-4">
                                No players found
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default IngameDashboard;