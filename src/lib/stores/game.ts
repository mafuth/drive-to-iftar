import { writable } from 'svelte/store';
import { tweened } from 'svelte/motion';
import { cubicOut } from 'svelte/easing';
import { GAME_CONFIG } from '$lib/config';

export const speed = writable(0);
export const score = writable(0);
export const isPlaying = writable(false);
export const isGameOver = writable(false);
export const selectedCharacter = writable(0);
export const selectedCar = writable(0);

// Lane: Centered index
// If maxLanes=3: -1, 0, 1.
// If maxLanes=4: -1.5, -0.5, 0.5, 1.5.
// Configured in config.ts as 1-based index (1 = Leftmost)
// Convert 1-based index to internal centered coordinate:
// Formula: internal = user - (maxLanes + 1) / 2
export const initialLane = GAME_CONFIG.player.initialLane - (GAME_CONFIG.lanes.maxLanes + 1) / 2;
export const targetLane = writable(initialLane);

export const lane = tweened(initialLane, {
    duration: 200,
    easing: cubicOut
});

export const assignedLane = writable<number | null>(null);

// Lane X coordinates mapping
// Helper to get current lane positions
export const getLanePositions = () => ({
    '-1': -GAME_CONFIG.lanes.width,
    '0': 0,
    '1': GAME_CONFIG.lanes.width
});

// Deprecate constant export or make it a getter if possible, but function is safer for hot reload
export const LANE_X_POSITIONS = {
    get '-1'() { return -GAME_CONFIG.lanes.width },
    get '0'() { return 0 },
    get '1'() { return GAME_CONFIG.lanes.width }
};

// Watermelons collected
export const watermelons = writable(0);
export const collectEvent = writable({ amount: 0, points: 0, timestamp: 0 }); // Used to broadcast collection events

// Nitro State
export const nitroActive = writable(false);
export const nitroTimer = tweened(0);
export const nitroTrigger = writable(0); // Incremented to trigger nitro animation across clients

// Game Seed for deterministic generation
// Always loaded fromconfig to ensure shared multiplayer reality
export const gameSeed = writable<string | number>(
    GAME_CONFIG.world.seed
);

// Zone at the horizon (for spawning traffic/obstacles)
export const currentHorizonZone = writable<string>('city');

// Menu Selection Direction (for animations)
// -1: Left/Next, 1: Right/Prev
export const selectionDirection = writable(0);

// Transition state for starting the game
export const isStarting = writable(false);

// Multiplayer / Sync Stores
import type { User, Lobby } from '../api';
export const currentUser = writable<User | null>(null);
export const currentSession = writable<Lobby | null>(null);
export const currentRaceId = writable<number | null>(null);
export const totalDistance = writable(0);

// Global Time (0-24 hour format)
export const gameTime = writable(
    GAME_CONFIG.world.sky.dynamic
        ? new Date().getHours()
        : GAME_CONFIG.world.sky.defaultTime
);

export type RivalData = {
    id: string;
    lane: number;
    distance: number;
    carIndex: number;
    lastUpdate: number;
};
export const rivals = writable<Map<string, RivalData>>(new Map());

// Performance Metrics
import { derived } from 'svelte/store';
export const obstacleCount = writable(0);
export const collectibleCount = writable(0);
export const worldModelCount = writable(0);
export const fps = writable(60);
export const totalObjects = derived(
    [obstacleCount, collectibleCount, worldModelCount],
    ([$oc, $cc, $wc]) => $oc + $cc + $wc + 1 // +1 for player
);
