import React from 'react';

import './App.css';
import Login from "./components/user/Login.tsx";
import Register from "./components/user/Register.tsx";
import Home from "./Home";
import Header from "./components/header/Header.tsx";
import RiotLogin from "./components/riot_user/Login.tsx";
import {LiveDashboard} from "./components/match_dashboard/Dashboard.tsx";
import type {MatchData} from "./components/match_dashboard/Dashboard.tsx";

import {
    BrowserRouter as Router,
    Routes,
    Route, useParams,
} from "react-router-dom";
import Tracker from "./components/Tracker";

const App = () => {
    return (
        <Router>
            <Header/>
            <Routes>
                <Route path="/" element={<Home/>}/>
                <Route path="/tracker" element={<Tracker/>}/>
                <Route path="/login" element={<Login/>}/>
                <Route path="/register" element={<Register/>}/>
                <Route path="/riot_login" element={<RiotLogin/>}/>
                <Route
                    path="/live/:matchUuid"
                    element={<LiveLoader/>}
                />
            </Routes>
        </Router>
    );
};


function LiveLoader() {
    const {matchUuid} = useParams<{ matchUuid: string }>();
    const [initialMatchData, setInitialMatchData] = React.useState<MatchData | null>(null);

    React.useEffect(() => {
        if (matchUuid) {
            FetchMatchData(matchUuid).then((data) => {
                setInitialMatchData(data);
            });
        }
    }, [matchUuid]);

    if (!initialMatchData) return <div>Loading...</div>;
    return <LiveDashboard initialMatchData={initialMatchData}/>;
}

async function FetchMatchData(matchUuid: string): Promise<MatchData> {
    //const resp = await fetch(`/api/matches/${matchUuid}`);

    return {
        "match": {
            "MatchID": "a3c7c279-7c90-4e94-ad94-1861c9bfdd07",
            "State": "IN_PROGRESS",
            "MapID": "/Game/Maps/Canyon/Canyon",
            "ModeID": "/Game/GameModes/Bomb/BombGameMode.BombGameMode_C",
            "Players": [
                {
                    "Subject": "2e444344-069c-5fc5-8124-6e2c6e552bfc",
                    "TeamID": "Red",
                    "CharacterID": "320b2a48-4d9b-a075-30f1-1f93a9b638fa",
                    "PlayerIdentity": {
                        "Subject": "2e444344-069c-5fc5-8124-6e2c6e552bfc",
                        "PlayerCardID": "59ed0836-4bd9-95a5-14c1-ed87ed786d06",
                        "PlayerTitleID": "bf097526-4503-6b17-2859-49a67bde66d2",
                        "AccountLevel": 50,
                        "PreferredLevelBorderID": "5156a90d-4d65-58d0-f6a8-48a0c003878a",
                        "Incognito": false,
                        "HideAccountLevel": false
                    },
                    "SeasonalBadgeInfo": {
                        "SeasonID": "",
                        "NumberOfWins": 0,
                        "WinsByTier": undefined,
                        "Rank": 0,
                        "LeaderboardRank": 0
                    },
                    "IsCoach": false,
                    "IsAssociated": true,
                    "PlatformType": "pc"
                }
            ],
            "MatchmakingData": undefined,
            "match_stats": {
                "sessionLoopState": "INGAME",
                "partyOwnerMatchScoreAllyTeam": 0,
                "partyOwnerMatchScoreEnemyTeam": 0,
                "matchMap": "/Game/Maps/Canyon/Canyon",
                "partySize": 1
            }
        },
        "players": [
            {
                "PlayerIdentity": {
                    "Subject": "2e444344-069c-5fc5-8124-6e2c6e552bfc",
                    "PlayerCardID": "59ed0836-4bd9-95a5-14c1-ed87ed786d06",
                    "PlayerTitleID": "bf097526-4503-6b17-2859-49a67bde66d2",
                    "AccountLevel": 50,
                    "PreferredLevelBorderID": "5156a90d-4d65-58d0-f6a8-48a0c003878a",
                    "Incognito": false,
                    "HideAccountLevel": false
                },
                "CharacterID": "320b2a48-4d9b-a075-30f1-1f93a9b638fa",
                "TeamID": "Red",
                "Subject": "2e444344-069c-5fc5-8124-6e2c6e552bfc",
                "SeasonalBadgeInfo": {
                    "SeasonID": "",
                    "NumberOfWins": 0,
                    "WinsByTier": undefined,
                    "Rank": 0,
                    "LeaderboardRank": 0
                }
            }
        ]
    }
}

export default App;