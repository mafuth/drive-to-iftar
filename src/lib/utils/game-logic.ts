import { GAME_CONFIG } from "$lib/config";
import { SeededRNG } from "$lib/utils/rng";

// Zone Calculation Logic
export function getZone(index: number, seed: string | number): string {
    const zoneBlock = Math.floor(index / GAME_CONFIG.zones.segmentLength);
    // Use a stable RNG for the zone block
    const zoneRng = new SeededRNG(seed + "" + zoneBlock * 9999);
    const zones = GAME_CONFIG.zones.sequence;
    // Pick a random zone from the sequence
    return zones[zoneRng.rangeInt(0, zones.length)];
}
