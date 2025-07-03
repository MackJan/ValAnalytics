import React, {useEffect, useState} from "react";
import {useParams} from "react-router-dom";
import IngameDashboard from "./IngameDashboard.tsx";
import {activeMatchApi} from "../../api.ts";

export interface Friend {
    Name: string;
    Subject: string;
    PlatformType: string;
    IsOnline: boolean;
    IsPlaying: boolean;
}

export interface MenuData {
    Name: string;
    Rank: string;
    RR: number;
    LeaderboardRank: number | null;
    Friends: Friend[];
    Season: string | null;
    InParty: boolean;
    PartySize: number;
}

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
    Name: string;
    AgentIcon: string;
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
    players: Omit<Player, "IsCoach" | "IsAssociated" | "PlatformType">[];
    matchData?: MatchData;
}

// Types for live events (unchanged)
export type LiveEventType = "match_update" | "stats_update" | "match_end";

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

export const LiveDashboard: React.FC = () => {
    const {matchUuid} = useParams<{ matchUuid: string }>();
    const [matchData, setMatchData] = useState<MatchData>();

    useEffect(() => {
        const uuid = matchUuid || null;
        console.log("Connecting to WebSocket for match:", uuid);

        const ws = new WebSocket(
            `${import.meta.env.VITE_WS_URL}/ws/live/${uuid}`
        );
        const connectionId = Math.random().toString(36).substring(2, 10);

        ws.onopen = () =>
            console.log(`WebSocket ${connectionId} connected for match ${uuid}`);
        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data) as LiveEvent;
                console.log("Received event:", data);

                switch (data.type) {
                    case "match_update": {
                        const matchUpdate = data.data as MatchUpdate;
                        setMatchData({
                            match: {
                                ...matchUpdate.match,
                                match_stats: matchUpdate.match.match_stats || {},
                            },
                            players: matchUpdate.players || [],
                        });
                        break;
                    }
                    case "match_end":
                        // Handle match end if you want
                        break;
                    // (You can add a “stats_update” case here if need‐be)
                }
            } catch (err) {
                console.error("Error parsing WebSocket message:", err);
            }
        };
        ws.onerror = (err) =>
            console.error(`WebSocket ${connectionId} error:`, err);
            if (matchUuid) {
                activeMatchApi.deleteActiveMatchUUID(matchUuid);
            }
        ws.onclose = () =>
            console.log(`WebSocket ${connectionId} closed for match ${uuid}`);

        return () => {
            ws.close();
        };
    }, [matchUuid]);

    return (
        <div className="min-h-screen bg-zinc-900 text-white p-6">
            <div className="max-w-6xl mx-auto">
                {/* Only render IngameDashboard once matchData is defined */}
                {matchData ? (
                    <IngameDashboard matchData={matchData}/>
                ) : (
                    <div className="text-gray-500">Waiting for live data…</div>
                )}
            </div>
        </div>
    );
};
