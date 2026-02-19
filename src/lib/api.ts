
import { type Writable, writable } from 'svelte/store';

const API_BASE = '/api';

export interface User {
    id: number;
    username: string | null;
    email: string;
    profile_photo: string | null;
    score: number;
    access_token?: string;
    is_guest?: boolean;
    rank?: number;
}

export interface Lobby {
    session_id: string;
    host_id: number;
    players: { id: number, username: string }[];
}

export interface GameConfig {
    seed: string;
    lanes: number;
    is_multiplayer: boolean;
}

function getAuthHeaders(): Record<string, string> {
    const token = localStorage.getItem('access_token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
}

export const api = {
    auth: {
        async login(code: string): Promise<User> {
            const res = await fetch(`${API_BASE}/auth/zitadel`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code })
            });
            if (!res.ok) throw new Error('Login failed');
            const data = await res.json();
            if (data.access_token) {
                localStorage.setItem('access_token', data.access_token);
            }
            return data;
        },
        async guestLogin(): Promise<User> {
            const res = await fetch(`${API_BASE}/auth/guest`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            if (!res.ok) throw new Error('Guest login failed');
            const data = await res.json();
            if (data.access_token) {
                localStorage.setItem('access_token', data.access_token);
            }
            return data;
        },
        async getMe(): Promise<User> {
            const res = await fetch(`${API_BASE}/auth/me`, {
                headers: getAuthHeaders()
            });
            if (!res.ok) throw new Error('Failed to get user');
            return res.json();
        },
        async getAuthConfig(): Promise<{ issuer: string, client_id: string }> {
            const res = await fetch(`${API_BASE}/auth/config`);
            if (!res.ok) throw new Error('Failed to get auth config');
            return res.json();
        },
        async updateUsername(username: string): Promise<User> {
            const res = await fetch(`${API_BASE}/auth/username`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    ...getAuthHeaders()
                },
                body: JSON.stringify({ username })
            });
            if (!res.ok) throw new Error('Failed to update username');
            return res.json();
        }
    },
    game: {
        async createLobby(maxPlayers: number = 5): Promise<Lobby> {
            const res = await fetch(`${API_BASE}/game/lobby`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...getAuthHeaders()
                },
                body: JSON.stringify({ max_players: maxPlayers })
            });
            if (!res.ok) throw new Error('Failed to create lobby');
            return res.json();
        },
        async joinLobby(sessionId: string, carIndex: number): Promise<Lobby> {
            const res = await fetch(`${API_BASE}/game/lobby/${sessionId}/join`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...getAuthHeaders()
                },
                body: JSON.stringify({ car_index: carIndex })
            });
            if (!res.ok) throw new Error('Failed to join lobby');
            return res.json();
        },
        async startGame(sessionId: string): Promise<{ status: string, race_id: number }> {
            const res = await fetch(`${API_BASE}/game/lobby/${sessionId}/start`, {
                method: 'POST',
                headers: getAuthHeaders()
            });
            if (!res.ok) throw new Error('Failed to start game');
            return res.json();
        },
        async retryGame(sessionId: string): Promise<{ status: string, race_id: number }> {
            const res = await fetch(`${API_BASE}/game/lobby/${sessionId}/retry`, {
                method: 'POST',
                headers: getAuthHeaders()
            });
            if (!res.ok) throw new Error('Failed to retry game');
            return res.json();
        },
        async startSinglePlayer(config?: any): Promise<{ status: string, race_id: number, session_id: string, config: any }> {
            const res = await fetch(`${API_BASE}/game/start/single`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...getAuthHeaders()
                },
                body: JSON.stringify(config || {})
            });
            if (!res.ok) throw new Error('Failed to start single player game');
            return res.json();
        },
        async getLeaderboard(): Promise<{ id: number, username: string, score: number, photo: string }[]> {
            const res = await fetch(`${API_BASE}/game/leaderboard`);
            if (!res.ok) throw new Error('Failed to get leaderboard');
            return res.json();
        },
        async getGameConfig(): Promise<any> {
            const res = await fetch(`${API_BASE}/game/config`);
            if (!res.ok) throw new Error('Failed to get game config');
            return res.json();
        },
        async submitScore(raceId: number, score: number): Promise<any> {
            const res = await fetch(`${API_BASE}/game/${raceId}/score`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...getAuthHeaders()
                },
                body: JSON.stringify({ score })
            });
            if (!res.ok) throw new Error('Failed to submit score');
            return res.json();
        },
        async getChallengeStatus(): Promise<{ active: boolean, target: number, collected: number, window: string }> {
            const res = await fetch(`${API_BASE}/game/challenge/status`, {
                headers: getAuthHeaders()
            });
            if (!res.ok) throw new Error('Failed to get challenge status');
            return res.json();
        },
        async collectDate(count: number = 1): Promise<{ status: string, collected: number }> {
            const res = await fetch(`${API_BASE}/game/challenge/collect`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...getAuthHeaders()
                },
                body: JSON.stringify({ count })
            });
            if (!res.ok) throw new Error('Failed to collect date');
            return res.json();
        },
        async getChallengeLeaderboard(): Promise<{ username: string, dates: number, photo: string | null }[]> {
            const res = await fetch(`${API_BASE}/game/challenge/leaderboard`);
            if (!res.ok) throw new Error('Failed to get challenge leaderboard');
            return res.json();
        }
    }
};
