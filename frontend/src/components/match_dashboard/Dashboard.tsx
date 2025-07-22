import React, {useEffect, useState, useRef} from "react";
import {useParams} from "react-router-dom";
import IngameDashboard from "./IngameDashboard.tsx";

// Updated types to match agent models
export interface CurrentMatchPlayer {
    subject: string;
    character: string;
    team_id: string;
    game_name: string;
    account_level: number | null;
    player_card_id: string | null;
    player_title_id: string | null;
    preferred_level_border_id: string | null;
    agent_icon: string;
    rank: string;
    rr: number | null;
    leaderboard_rank: number | null;
}

export interface CurrentMatch {
    match_id: string;
    game_map: string;
    game_start: number;
    game_mode: string;
    state: string;
    party_owner_score: number;
    party_owner_enemy_score: number;
    party_owner_average_rank: string;
    party_owner_enemy_average_rank: string;
    party_owner_team_id: string;
    party_size: number;
    players: CurrentMatchPlayer[];
}

export interface MatchData {
    match: CurrentMatch;
}

// Types for live events
export type LiveEventType = "match_update" | "match_end" | "initial_data";

export interface LiveEvent {
    type: LiveEventType;
    match_id: string;
    data: CurrentMatch;
    timestamp: string;
}

// Updated types for menu data that align with agent models
export interface MenuData {
    name: string;
    rank: string;
    rr: number | null;
    leaderboard_rank: number | null;
    season: string | null;
    in_party: boolean;
}

export const LiveDashboard: React.FC = () => {
    const {matchUuid} = useParams<{ matchUuid: string }>();
    const [matchData, setMatchData] = useState<MatchData>();

    // Use useRef instead of useState for initial player data
    const initialPlayerDataRef = useRef<CurrentMatchPlayer[] | null>(null);
    const initialPartyOwnerAverageRankRef = useRef<string | null>(null);
    const initialPartyOwnerEnemyAverageRankRef = useRef<string | null>(null);
    const initialPartyOwnerTeamIdRef = useRef<string | null>(null);

    const wsRef = useRef<WebSocket | null>(null);

    useEffect(() => {
        const uuid = matchUuid || null;

        // Close existing connection if any
        if (wsRef.current) {
            wsRef.current.close();
        }

        // Reset initial player data when connecting to new match
        initialPlayerDataRef.current = null;
        initialPartyOwnerAverageRankRef.current = null;
        initialPartyOwnerEnemyAverageRankRef.current = null;
        initialPartyOwnerTeamIdRef.current = null;

        console.log("Connecting to WebSocket for match:", uuid);

        const ws = new WebSocket(
            `${import.meta.env.VITE_WS_URL}/ws/live/${uuid}`
        );
        wsRef.current = ws;

                const connectionId = Math.random().toString(36).substring(2, 10);

                ws.onopen = () =>
                    console.log(`WebSocket ${connectionId} connected for match ${uuid}`);
                ws.onmessage = (event) => {
                    try {
                        const eventData = JSON.parse(event.data) as LiveEvent;
                        console.log("Received event:", eventData);

                        switch (eventData.type) {
                            case "initial_data": {
                                const currentMatch = eventData.data as CurrentMatch;
                                // Store in ref for immediate access
                                initialPlayerDataRef.current = currentMatch.players;
                                initialPartyOwnerAverageRankRef.current = currentMatch.party_owner_average_rank;
                                initialPartyOwnerEnemyAverageRankRef.current = currentMatch.party_owner_enemy_average_rank;
                                initialPartyOwnerTeamIdRef.current = currentMatch.party_owner_team_id;
                                setMatchData({
                                    match: currentMatch
                                });
                                break;
                            }
                            case "match_update": {
                                const currentMatch = eventData.data as CurrentMatch;
                                console.log("Initial player data:", initialPlayerDataRef.current);

                                // Use ref data if available
                                if (initialPlayerDataRef.current && initialPlayerDataRef.current.length > 0) {
                                    currentMatch.players = initialPlayerDataRef.current;
                                }
                                if (initialPartyOwnerAverageRankRef.current) {
                                    currentMatch.party_owner_average_rank = initialPartyOwnerAverageRankRef.current;
                                }
                                if (initialPartyOwnerEnemyAverageRankRef.current) {
                                    currentMatch.party_owner_enemy_average_rank = initialPartyOwnerEnemyAverageRankRef.current;
                                }
                                if (initialPartyOwnerTeamIdRef.current) {
                                    currentMatch.party_owner_team_id = initialPartyOwnerTeamIdRef.current;
                                }


                        setMatchData({
                            match: currentMatch
                        });
                        break;
                    }
                    case "match_end":
                        setMatchData(undefined);
                        initialPlayerDataRef.current = null;
                        break;
                }
            } catch (err) {
                console.error("Error parsing WebSocket message:", err);
            }
        };
        ws.onerror = (err) => {
            console.error(`WebSocket ${connectionId} error:`, err);
        }
        ws.onclose = () =>
            console.log(`WebSocket ${connectionId} closed for match ${uuid}`);

        return () => {
            if (wsRef.current) {
                wsRef.current.close();
                wsRef.current = null;
            }
        };
    }, [matchUuid]); // Only depend on matchUuid

    return (
        <div>
            {matchData ? (
                <IngameDashboard matchData={matchData}/>
            ) : (
                <div className="text-gray-500">Waiting for live data…</div>
            )}
        </div>
    );
};