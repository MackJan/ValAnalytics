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
    party_size: number;
    players: CurrentMatchPlayer[];
}

export interface MatchData {
    match: CurrentMatch;
}

// Types for live events
export type LiveEventType = "match_update" | "match_end";

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
    const wsRef = useRef<WebSocket | null>(null);

    useEffect(() => {
        const uuid = matchUuid || null;

        // Close existing connection if any
        if (wsRef.current) {
            wsRef.current.close();
        }

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
                    case "match_update": {
                        // Parse the data if it's a string, otherwise use it directly
                        const currentMatch = typeof eventData.data === 'string'
                            ? JSON.parse(eventData.data) as CurrentMatch
                            : eventData.data as CurrentMatch;
                        setMatchData({
                            match: currentMatch
                        });
                        break;
                    }
                    case "match_end":
                        setMatchData(undefined);
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
