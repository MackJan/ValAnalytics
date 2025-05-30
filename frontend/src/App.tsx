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
                <Route path="/" element={<Home />} />
                <Route path="/tracker" element={<Tracker />} />
                <Route path="/login" element={<Login/>} />
                <Route path="/register" element={<Register/>} />
                <Route path="/riot_login" element={<RiotLogin/>} />
                <Route
                    path="/live/:matchUuid"
                    element={<LiveLoader />}
                />
            </Routes>
        </Router>
    );
};


function LiveLoader() {
    const { matchUuid } = useParams<{ matchUuid: string }>();
    const [initialMatchData, setInitialMatchData] = React.useState<MatchData | null>(null);

    React.useEffect(() => {
        if (matchUuid) {
            FetchMatchData(matchUuid).then((data) => {
                setInitialMatchData(data);
            });
        }
    }, [matchUuid]);

    if (!initialMatchData) return <div>Loading...</div>;
    return <LiveDashboard initialMatchData={initialMatchData} />;
}

async function FetchMatchData(matchUuid: string): Promise<MatchData> {
    //const resp = await fetch(`/api/matches/${matchUuid}`);
    //return resp.json();

    return {
        'match': {
            'MatchID': '66a839f4-6f7d-412d-8e0f-6dccadd8a7d0',
            'State': 'IN_PROGRESS',
            'MapID': '/Game/Maps/Ascent/Ascent',
            'ModeID': '/Game/GameModes/Bomb/BombGameMode.BombGameMode_C',
            'Players': [
                {
                    'Subject': '2e444344-069c-5fc5-8124-6e2c6e552bfc',
                    'TeamID': 'Blue',
                    'CharacterID': '320b2a48-4d9b-a075-30f1-1f93a9b638fa',
                    'PlayerIdentity': {
                        'Subject': '2e444344-069c-5fc5-8124-6e2c6e552bfc',
                        'PlayerCardID': '59ed0836-4bd9-95a5-14c1-ed87ed786d06',
                        'PlayerTitleID': 'bf097526-4503-6b17-2859-49a67bde66d2',
                        'AccountLevel': 50,
                        'PreferredLevelBorderID': '5156a90d-4d65-58d0-f6a8-48a0c003878a',
                        'Incognito': false,
                        'HideAccountLevel': false
                    },
                    'SeasonalBadgeInfo': {
                        'SeasonID': '',
                        'NumberOfWins': 0,
                        'WinsByTier': 0,
                        'Rank': 0,
                        'LeaderboardRank': 0
                    },
                    'IsCoach': false,
                    'IsAssociated': true,
                    'PlatformType': 'pc'
                }
            ],
        },
        'players': [
            {
                'PlayerIdentity': {
                    'Subject': '2e444344-069c-5fc5-8124-6e2c6e552bfc',
                    'PlayerCardID': '59ed0836-4bd9-95a5-14c1-ed87ed786d06',
                    'PlayerTitleID': 'bf097526-4503-6b17-2859-49a67bde66d2',
                    'AccountLevel': 50,
                    'PreferredLevelBorderID': '5156a90d-4d65-58d0-f6a8-48a0c003878a',
                    'Incognito': false,
                    'HideAccountLevel': false
                },
                'CharacterID': '320b2a48-4d9b-a075-30f1-1f93a9b638fa',
                'Subject': '2e444344-069c-5fc5-8124-6e2c6e552bfc',
                'SeasonalBadgeInfo': {
                    'SeasonID': '',
                    'NumberOfWins': 0,
                    'WinsByTier': null,
                    'Rank': 0,
                    'LeaderboardRank': 0
                },
                'TeamID': 'Blue'
            }
        ]
    }
}
export default App;