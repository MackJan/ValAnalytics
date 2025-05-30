import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

// Types for incoming data
export interface PlayerIdentity {
    Subject: string;
    PlayerCardID: string;
    PlayerTitleID: string;
    AccountLevel: number;
    PreferredLevelBorderID: string;
    Incognito: boolean;
    HideAccountLevel: boolean;
}

export interface SeasonalBadgeInfo {
    SeasonID: string;
    NumberOfWins: number;
    WinsByTier: unknown;
    Rank: number;
    LeaderboardRank: number;
}

export interface Player {
    Subject: string;
    TeamID: string;
    CharacterID: string;
    PlayerIdentity: PlayerIdentity;
    SeasonalBadgeInfo: SeasonalBadgeInfo;
    IsCoach?: boolean;
    IsAssociated?: boolean;
    PlatformType?: string;
}

export interface MatchMeta {
    MatchID: string;
    State: string;
    MapID: string;
    ModeID: string;
    Players: Player[];
    MatchmakingData: unknown;
    match_stats: {
        sessionLoopState: string;
        partyOwnerMatchScoreAllyTeam: number;
        partyOwnerMatchScoreEnemyTeam: number;
        matchMap: string;
        partySize: number;
    };
}

export interface MatchData {
    match: MatchMeta;
    players: Omit<Player, 'IsCoach' | 'IsAssociated' | 'PlatformType'>[];
}

// Types for live events
export type LiveEventType = 'match_update' | 'stats_update' | 'match_end';

export interface MatchUpdate {
    match: MatchMeta;
    players: Player[];
}

export interface StatsUpdate {
    matchUuid: string;
    round: number;
    roundPhase: string;
    playerStats: Array<{
        riotId: string;
        kills: number;
        deaths: number;
        assists: number;
        score: number;
    }>;
}

export interface LiveEvent {
    type: LiveEventType;
    timestamp: string;
    data: MatchUpdate | StatsUpdate | unknown;
}

interface LiveDashboardProps {
    initialMatchData: MatchData;
}

export const LiveDashboard: React.FC<LiveDashboardProps> = ({ initialMatchData }) => {
    const { matchUuid } = useParams<{ matchUuid: string }>();
    const [events, setEvents] = useState<LiveEvent[]>([]);
    const [stats, setStats] = useState<StatsUpdate | null>(null);
    const [matchData, setMatchData] = useState<MatchData>(initialMatchData);

    useEffect(() => {
        const uuid = matchUuid || initialMatchData.match.MatchID;
        console.log("Connecting to WebSocket for match:", uuid);

        const ws = new WebSocket(`${import.meta.env.VITE_WS_URL}/ws/live/${uuid}`);
        const connectionId = Math.random().toString(36).substring(2, 10);

        ws.onopen = () => console.log(`WebSocket ${connectionId} connected for match ${uuid}`);
        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data) as LiveEvent;
                console.log('Received event:', data);

                setEvents((prev) => [...prev, {
                    type: data.type,
                    timestamp: data.timestamp,
                    data: data.data
                }]);

                switch (data.type) {
                    case 'match_update':
                        { const matchUpdate = data.data as MatchUpdate;
                        setMatchData(prev => ({
                            ...prev,
                            match: {
                                ...prev.match,
                                ...matchUpdate.match,
                                match_stats: {
                                    ...prev.match.match_stats,
                                    ...matchUpdate.match.match_stats
                                }
                            },
                            players: matchUpdate.players || prev.players
                        }));
                        break; }
                    case 'stats_update':
                        setStats(data.data as StatsUpdate);
                        break;
                    case 'match_end':
                        // Handle match end logic
                        break;
                }
            } catch (err) {
                console.error('Error parsing WebSocket message:', err);
            }
        };
        ws.onerror = (err) => console.error(`WebSocket ${connectionId} error:`, err);
        ws.onclose = () => console.log(`WebSocket ${connectionId} closed for match ${uuid}`);

        return () => {
            ws.close();
        };
    }, [matchUuid, initialMatchData.match.MatchID]);

    // Helper functions
    const getMapName = (mapId: string) => mapId.split('/').pop() || 'Unknown';
    const getModeName = (modeId: string) => {
        const mode = modeId.split('/').pop() || 'Unknown';
        return mode.replace('GameMode_C', '').replace('GameMode', '');
    };

    const { match } = matchData;

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
                            <p>{getMapName(match.MapID)}</p>
                        </div>
                        <div className="bg-gray-800 p-4 rounded-lg">
                            <h3 className="text-sm text-gray-400">Mode</h3>
                            <p>{getModeName(match.ModeID)}</p>
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
                                                <div className="flex-shrink-0 h-8 w-8 bg-gray-500 rounded-full mr-3"></div>
                                                <div>
                                                    <p className="font-medium">Player {player.Subject.slice(0, 8)}</p>
                                                    <p className="text-xs text-gray-400">{player.PlatformType || 'PC'}</p>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-4 py-3">{player.PlayerIdentity.AccountLevel}</td>
                                        <td className="px-4 py-3">{player.CharacterID.slice(0, 8)}</td>
                                        <td className="px-4 py-3">{player.SeasonalBadgeInfo.NumberOfWins}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Live Stats Section */}
                {stats && (
                    <div className="mb-8 bg-gray-800 rounded-lg p-6">
                        <h2 className="text-2xl font-bold text-purple-400 mb-4">Live Round Stats</h2>
                        <div className="mb-4">
                            <p className="text-lg">
                                <span className="font-semibold">Round:</span> {stats.round} |
                                <span className="font-semibold"> Phase:</span> {stats.roundPhase}
                            </p>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="min-w-full bg-gray-700 rounded-lg overflow-hidden">
                                <thead className="bg-gray-600">
                                    <tr>
                                        <th className="px-4 py-3 text-left">Player</th>
                                        <th className="px-4 py-3 text-left">Kills</th>
                                        <th className="px-4 py-3 text-left">Deaths</th>
                                        <th className="px-4 py-3 text-left">Assists</th>
                                        <th className="px-4 py-3 text-left">Score</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {stats.playerStats.map((ps) => (
                                        <tr key={ps.riotId} className="border-t border-gray-600 hover:bg-gray-600">
                                            <td className="px-4 py-3">{ps.riotId}</td>
                                            <td className="px-4 py-3">{ps.kills}</td>
                                            <td className="px-4 py-3">{ps.deaths}</td>
                                            <td className="px-4 py-3">{ps.assists}</td>
                                            <td className="px-4 py-3 font-semibold">{ps.score}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}

                {/* Event Log Section */}
                <div className="bg-gray-800 rounded-lg p-6">
                    <h2 className="text-2xl font-bold text-purple-400 mb-4">Event Log</h2>
                    <div className="h-64 overflow-y-auto bg-gray-700 p-4 rounded-lg">
                        {events.length === 0 ? (
                            <p className="text-gray-400">No events yet. Waiting for updates...</p>
                        ) : (
                            events.map((e, idx) => (
                                <div key={idx} className="mb-2 pb-2 border-b border-gray-600 last:border-0">
                                    <span className="text-purple-300">[{new Date(e.timestamp).toLocaleTimeString()}]</span>{' '}
                                    <span className="font-medium">{e.type}</span>
                                    {e.type === 'stats_update' && (
                                        <span className="ml-2 text-sm text-gray-400">Round updated</span>
                                    )}
                                    {e.type === 'match_update' && (
                                        <span className="ml-2 text-sm text-gray-400">Match data updated</span>
                                    )}
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};