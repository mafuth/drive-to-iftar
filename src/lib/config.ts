export let GAME_CONFIG = {
    // ... (Default values will be overwritten)
    world: {
        tileLength: 30,
        seed: new Date().toDateString(),
        numTiles: 12, // Reduce render distance for performance
        roadScale: [1.5, 3, 6] as [number, number, number], // MUCH wider road strips
        roadRotation: [0, Math.PI / 2, 0] as [number, number, number],
        // ... (Keep existing defaults as fallback)
        fog: {
            color: "#000816",
            near: 30,
            far: 300
        },
        curvature: -0.0003,
        sky: {
            dynamic: false,
            defaultTime: 13,
            day: {
                fog: "#87ceeb",
                ambient: "#99ccff",
                directional: "#fff5e6",
                intensity: 2.0
            },
            sunset: {
                fog: "#ff7b39",
                ambient: "#4a4a8a",
                directional: "#ffaa33",
                intensity: 3.0
            },
            night: {
                fog: "#000816",
                ambient: "#151530",
                directional: "#88aaff",
                intensity: 0.8
            }
        },
        sidewalk: {
            width: 200,
            height: 1,
            offset: 57.5,
            segments: 50,
            color: {
                city: "#ffffff",
                nature: "#7eff3d",
                bridge: "#00ffff"
            }
        },
        ground: {
            width: 1000,
            height: 40,
            yOffset: -35.5,
            segments: 40,
            color: {
                city: "#ffffff",
                nature: "#7eff3d",
                bridge: "#00ffff"
            }
        }
    },
    zones: {
        segmentLength: 40,
        sequence: ["city", "suburbs", "industrial", "bridge", "nature"] as const,
        zoneTransitionGap: 5,
        bridge: {
            waterColor: "#00ffff",
            boats: {
                density: 0.05,
                offset: 15,
                offsetVariance: 16,
                scale: { min: 1, max: 2 },
                yOffset: -0.8,
                bobbing: {
                    amplitude: 0.15,
                    speed: 1.5
                }
            }
        },
        nature: {
            scale: { min: 10, max: 12 },
            density: 0.8,
            offsetVariance: 15
        }
    },
    lanes: {
        width: 4.5,
        maxLanes: 3
    },
    player: {
        scale: 2.2,
        speed: {
            initial: 20,
            increment: 0.5,
            max: 50
        },
        initialLane: 2,
        laneChangeSpeed: 10,
        bankingIntensity: 0.2,
        jumpHeight: 0,
        camera: {
            position: [0, 15, 27] as [number, number, number],
            fov: 70,
            lookAt: [0, 0, -10] as [number, number, number]
        },
        hitbox: { width: 4, height: 2, depth: 4 },
        nitro: {
            duration: 5000,
            speedBoost: 50,
            flyHeight: 5,
            flySpeed: 500,
            tiltNitro: 0.1,
            tiltEnding: -0.15,
            watermelonThreshold: 5
        },
        scoreMultiplier: 0.2
    },
    buildings: {
        offset: 30,
        scale: { min: 12, max: 22 },
        spawnChance: 1.0
    },
    lights: {
        offset: 8,
        scale: 10,
        spawnChance: 0.3,
        spawnInterval: 100,
        rotation: [0, Math.PI, 0] as [number, number, number]
    },
    obstacles: {
        scale: 2.2,
        spawnDistance: -250,
        rotation: [0, Math.PI, 0] as [number, number, number],
        hitbox: { width: 4, height: 2, depth: 4 },
        proximitySoundDistance: 40,
        spawn: {
            initialDelay: 2500,
            minDelay: 1000,
            decreaseFactor: 40
        }
    },
    collectibles: {
        scale: 3,
        hitbox: { width: 3, height: 3, depth: 3 },
        spawnDistance: -250,
        spawn: {
            interval: 1000,
            chance: 0.1
        },
        points: 100
    },
    dates: {
        scale: 3,
        hitbox: { width: 2, height: 2, depth: 2 },
        spawnDistance: -250,
        spawn: {
            interval: 800,
            chance: 0.15
        },
        points: 50,
        target: 10,
        startHour: 1,
        endHour: 24
    },
    menus: {
        start: {
            camera: {
                position: [6, 1.2, 0] as [number, number, number],
                lookAt: [0, 0.8, 0] as [number, number, number],
                fov: 45
            },
            car: {
                position: [0, 0, 1.5] as [number, number, number],
                rotation: [0, -Math.PI / 2, 0] as [number, number, number]
            },
            character: {
                position: [0, 0, 1.5] as [number, number, number],
                rotation: [0, Math.PI / 6, 0] as [number, number, number],
                scale: 1.9
            }
        },
        gameover: {
            groupOffset: [0, 0, 5] as [number, number, number],
            car: {
                position: [0, 0.5, -2] as [number, number, number],
                rotation: [Math.PI / 8, Math.PI + Math.PI / 4, Math.PI / 12] as [number, number, number]
            },
            character: {
                position: [2, 0, -2] as [number, number, number],
                rotation: [0, -Math.PI / 4, 0] as [number, number, number],
                scale: 2
            }
        }
    },
    development: {
        collisionEnabled: true,
        devMode: false,
        showHitboxes: false
    }
};

import { api } from "$lib/api";
import { Logger } from "$lib/utils/logger";

const log = new Logger("Config");

export async function loadGameConfig() {
    try {
        const backendConfig = await api.game.getGameConfig();
        // Merge backend config into GAME_CONFIG
        // Using helper to preserve nested structures if needed, but simple Object.assign might shallow copy.
        // Deep merge is safer if we get partial updates, but we expect full config.

        // Careful with arrays and strict types, but Object.assign is lenient at runtime.
        // Deep-ish merge to preserve local defaults in nested objects
        const config = GAME_CONFIG as any;
        const backend = backendConfig as any;
        for (const key in backend) {
            if (
                config[key] &&
                typeof config[key] === "object" &&
                !Array.isArray(config[key])
            ) {
                Object.assign(config[key], backend[key]);
            } else {
                config[key] = backend[key];
            }
        }
        log.log("GAME_CONFIG updated from backend", GAME_CONFIG);
    } catch (e) {
        log.error("Failed to load backend config, using defaults", e);
    }
}
