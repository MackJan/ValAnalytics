# Valorant Performance Tracker

Valorant Performance Tracker is a multi-component application that collects live match information from the game client and displays it in real time. It currently consists of:

- **Agent** – A Python script that communicates with local Riot APIs to obtain your presence, match details and other information. It sends live updates to the backend via WebSockets and updates Discord Rich Presence.
- **Backend** – A FastAPI service that stores active match data in a PostgreSQL database and relays live updates to connected front‑end clients through WebSockets.
- **Frontend** – A React + TypeScript web application providing dashboards for ongoing matches.

The services can be run together using the provided Docker Compose setup. When the agent is running while you play Valorant, the backend receives continuous match updates which are displayed on the dashboard and used for Discord RPC.

## Running the stack

Use Docker Compose to start the database, backend and frontend:

```bash
docker compose -f infra/docker-compose.yml up
```

Run the agent locally (requires Python 3.9 and `pip install -r agent/requirements.txt`). It will connect to the backend at `http://localhost:8000` and start updating Discord Rich Presence.

## Features

- Tracks the current match and party information directly from the Valorant client.
- Updates Discord Rich Presence with map, mode, score and party size.
- Stores active match data in PostgreSQL via FastAPI.
- Live match dashboard showing team scores and players (WIP).

## Screenshots

![Discord RPC](https://media.discordapp.net/attachments/768367820119343107/1393234035844710471/image.png?ex=68726dcf&is=68711c4f&hm=45258ea274555b727f2ce4b9f3e9a655b0974ae7a6c68cb08233dbe9b8457964&=&format=webp&quality=lossless)

![Active Matches](https://media.discordapp.net/attachments/768367820119343107/1393234035182145779/image.png?ex=68726dcf&is=68711c4f&hm=657bc66976cf392b3cb5a6f28fb81312d806390b1bff05e9d5ce80192f9a2bd2&=&format=webp&quality=lossless)

![Match Dashboard](https://media.discordapp.net/attachments/768367820119343107/1393234035614027906/image.png?ex=68726dcf&is=68711c4f&hm=03f26632cd33fca5de941adb7b46cc73cf167204024157555a9c7b85054ebd2f&=&format=webp&quality=lossless&width=853&height=856)
