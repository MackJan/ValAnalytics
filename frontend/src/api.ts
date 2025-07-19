import axios from "axios";
import { ACCESS_TOKEN } from "./constants";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem(ACCESS_TOKEN);
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
},
    (error) => {
        return Promise.reject(error);
    }
);

// Active Match API functions
export interface ActiveMatch {
    id: number;
    match_uuid: string;
    created_at: string;
    game_map: string;
    game_mode: string;
}

export interface ActiveMatchCreate {
    match_uuid: string;
}

export const activeMatchApi = {
    // Get all active matches
    getActiveMatches: async (): Promise<ActiveMatch[]> => {
        const response = await api.get('/active_matches/');
        return response.data;
    },

    // Create a new active match
    createActiveMatch: async (activeMatch: ActiveMatchCreate): Promise<ActiveMatch> => {
        const response = await api.post('/active_matches/', activeMatch);
        return response.data;
    },

    // Get a specific active match
    getActiveMatch: async (id: number): Promise<ActiveMatch> => {
        const response = await api.get(`/active_matches/${id}/`);
        return response.data;
    },

    // End an active match
    endActiveMatch: async (id: number): Promise<ActiveMatch> => {
        const response = await api.patch(`/active_matches/${id}/`, {
            ended_at: new Date().toISOString()
        });
        return response.data;
    },

    // Delete an active match
    deleteActiveMatch: async (id: number): Promise<void> => {
        await api.delete(`/active_matches/${id}/`);
    },

    deleteActiveMatchUUID: async (uuid: string): Promise<void> => {
        await api.delete(`/active_matches/uuid/${uuid}`);
    }
};

export default api;