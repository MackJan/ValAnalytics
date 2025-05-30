import React, {useEffect, useState} from 'react';
import {useParams} from 'react-router-dom';

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
}

export interface MatchData {
    match: MatchMeta;
    players: Omit<Player, 'IsCoach' | 'IsAssociated' | 'PlatformType'>[];
}

// Types for live events
export type LiveEventType = 'match_start' | 'stats_update' | 'match_end';

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
    data: unknown;
}

interface LiveDashboardProps {
    initialMatchData: MatchData;
}

export const LiveDashboard: React.FC<LiveDashboardProps> = ({initialMatchData}) => {
    const {matchUuid} = useParams<{ matchUuid: string }>();
    const [events, setEvents] = useState<LiveEvent[]>([]);
    const [stats, setStats] = useState<StatsUpdate | null>(null);

    useEffect(() => {
        // Prefer URL param, fallback to initial data
        const uuid = matchUuid || initialMatchData.match.MatchID;
        const ws = new WebSocket(
            `${import.meta.env.VITE_WS_URL}/ws/live/${uuid}`
        );

        ws.onopen = () => console.log('WebSocket connected for match', uuid);
        ws.onmessage = (event) => {
            console.log('WebSocket message received:', event.data);
            const liveEvent: LiveEvent = JSON.parse(event.data);
            setEvents((prev) => [...prev, liveEvent]);

            if (liveEvent.type === 'stats_update') {
                setStats(liveEvent.data as StatsUpdate);
            }
        };
        ws.onerror = (err) => console.error('WebSocket error:', err);
        ws.onclose = () => console.log('WebSocket closed for match', uuid);

        return () => {
            ws.close();
        };
    }, [matchUuid, initialMatchData.match.MatchID]);

    const {match} = initialMatchData;

    return (
        <div className="p-4">
            <h2 className="text-2xl font-bold mb-2">Live Match Dashboard</h2>
            <div className="mb-4">
                <p><strong>Match ID:</strong> {match.MatchID}</p>
                <p><strong>State:</strong> {match.State}</p>
                <p><strong>Map:</strong> {match.MapID.split('/').pop()}</p>
                <p><strong>Mode:</strong> {match.ModeID.split('/').pop()}</p>
            </div>

            {stats && (
                <div className="mb-4">
                    <h3 className="text-xl font-semibold">Round {stats.round} - {stats.roundPhase}</h3>
                    <table className="min-w-full table-auto border-collapse">
                        <thead>
                        <tr>
                            <th className="border px-2 py-1">Player</th>
                            <th className="border px-2 py-1">Kills</th>
                            <th className="border px-2 py-1">Deaths</th>
                            <th className="border px-2 py-1">Assists</th>
                            <th className="border px-2 py-1">Score</th>
                        </tr>
                        </thead>
                        <tbody>
                        {stats.playerStats.map((ps) => (
                            <tr key={ps.riotId}>
                                <td className="border px-2 py-1">{ps.riotId}</td>
                                <td className="border px-2 py-1">{ps.kills}</td>
                                <td className="border px-2 py-1">{ps.deaths}</td>
                                <td className="border px-2 py-1">{ps.assists}</td>
                                <td className="border px-2 py-1">{ps.score}</td>
                            </tr>
                        ))}
                        </tbody>
                    </table>
                </div>
            )}

            <div>
                <h3 className="text-xl font-semibold">Event Log</h3>
                <div className="h-48 overflow-y-auto bg-gray-100 p-2 rounded">
                    {events.map((e, idx) => (
                        <div key={idx} className="mb-1">
                            <strong>[{new Date(e.timestamp).toLocaleTimeString()}]</strong> {e.type}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};