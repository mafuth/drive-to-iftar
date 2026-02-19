/**
 * Simple Seeded Random Number Generator using Mulberry32
 * Fast and deterministic.
 */
export class SeededRNG {
    private seed: number;

    constructor(seed: number | string) {
        this.seed = this.hash(seed);
    }

    /**
     * FNV-1a-like hash to convert string/number to a start seed
     */
    private hash(input: number | string): number {
        let str = input.toString();
        let h = 0x811c9dc5;
        for (let i = 0; i < str.length; i++) {
            h ^= str.charCodeAt(i);
            h = Math.imul(h, 0x01000193);
        }
        return h >>> 0;
    }

    /**
     * Returns a float between 0 (inclusive) and 1 (exclusive)
     */
    next(): number {
        this.seed += 0x6d2b79f5;
        let t = this.seed;
        t = Math.imul(t ^ (t >>> 15), t | 1);
        t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    }

    /**
     * Returns a float between min (inclusive) and max (exclusive)
     */
    range(min: number, max: number): number {
        return min + this.next() * (max - min);
    }

    /**
     * Returns an integer between min (inclusive) and max (exclusive)
     */
    rangeInt(min: number, max: number): number {
        return Math.floor(this.range(min, max));
    }

    /**
     * Returns true with the given probability (0-1)
     */
    chance(probability: number): boolean {
        return this.next() < probability;
    }

    /**
     * Picks a random element from an array
     */
    pick<T>(array: T[]): T | undefined {
        if (array.length === 0) return undefined;
        return array[this.rangeInt(0, array.length)];
    }
}
