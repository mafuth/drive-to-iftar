<script lang="ts">
    import { T, useTask } from "@threlte/core";
    import { useGltf } from "@threlte/extras";
    import { ASSETS } from "$lib/utils/assets";
    import {
        speed,
        isPlaying,
        isGameOver,
        lane,
        LANE_X_POSITIONS,
        score,
        nitroActive,
        totalDistance,
        currentHorizonZone,
        gameSeed,
        obstacleCount,
        isTutorial,
        isMuted,
    } from "$lib/stores/game";
    import { Logger } from "$lib/utils/logger";
    const log = new Logger("Obstacles");
    import { GAME_CONFIG } from "$lib/config";
    import { onMount } from "svelte";
    import { browser } from "$app/environment";
    import { derived } from "svelte/store";
    import { SeededRNG } from "$lib/utils/rng";
    import { applyWorldCurvature } from "$lib/utils/worldBending";

    // Types
    type Obstacle = {
        id: string;
        z: number;
        lane: number; // -1, 0, 1
        modelIndex: number;
        zone: string; // Add zone to type
        speedOffset: number; // Some vary in speed?
        speed: number;
        playedSound: boolean;
    };

    let obstacles: Obstacle[] = [];
    // Store models by zone
    let trafficModels: Record<string, any[]> = {
        city: [],
        suburbs: [],
        industrial: [],
        nature: [],
    };

    // Load Traffic Assets per Zone
    function loadTrafficZone(paths: string[]) {
        const stores = paths.map((path) => useGltf(path));
        return derived(stores, ($results) => {
            return $results
                .map((result) => {
                    if (result && result.scene) {
                        const scene = result.scene.clone();
                        applyWorldCurvature(scene);
                        return scene;
                    }
                    return null;
                })
                .filter((scene) => scene !== null);
        });
    }

    const cityTraffic = loadTrafficZone(ASSETS.traffic.city);
    const suburbsTraffic = loadTrafficZone(ASSETS.traffic.suburbs);
    const industrialTraffic = loadTrafficZone(ASSETS.traffic.industrial);
    const natureTraffic = loadTrafficZone(ASSETS.traffic.nature);

    $: trafficModels.city = $cityTraffic;
    $: trafficModels.suburbs = $suburbsTraffic;
    $: trafficModels.industrial = $industrialTraffic;
    $: trafficModels.nature = $natureTraffic;

    let lastSpawnDistance = 0;
    const SPAWN_GAP = 30; // Spawn every 30m

    let hornAudio: HTMLAudioElement | null = null;

    // Reset logic: ensure clean state on mount or when game restarts
    onMount(() => {
        // Preload horn audio for low-latency playback
        if (browser && ASSETS.sounds.horn) {
            hornAudio = new Audio(ASSETS.sounds.horn);
            hornAudio.preload = "auto";
            hornAudio.load();
        }

        console.log("!!! OBSTACLE SPAWNER MOUNTED !!!", {
            proximityDistance: GAME_CONFIG.obstacles.proximitySoundDistance,
            isMuted: $isMuted,
            isTutorial: $isTutorial,
        });
        obstacles = [];
        lastSpawnDistance = 0;
    });

    $: if (!$isPlaying) {
        obstacles = [];
        lastSpawnDistance = 0;
    }

    useTask((delta) => {
        if ($isGameOver || !$isPlaying) return;

        // Deterministic Spawning
        // If we've traveled enough since last spawn
        if ($totalDistance - lastSpawnDistance > SPAWN_GAP) {
            // Important: snap to the grid to keep it perfectly deterministic
            const spawnDist =
                Math.floor($totalDistance / SPAWN_GAP) * SPAWN_GAP;
            lastSpawnDistance = spawnDist;

            // Re-enforce tutorial check here to avoid even calling the function
            if (!$isTutorial) {
                spawnObstacle(spawnDist);
            }
        }

        // Move Obstacles
        // Obstacles move towards player (positive Z) relative to player?
        // No, in this game:
        // Player is at Z=2. Road moves backward (Z increases).
        // Obstacles are on the road. So they should move with the road?
        // If they are static on road, they move at $speed.
        // If they are moving cars, they might move slower/faster than road.
        // Let's assume they are "traffic" moving in same direction as player but slower.
        // Player needs to overtake them?
        // If player speed > obstacle speed, obstacle moves towards player (Z increases).
        // If traffic is oncoming, it moves towards player fast (Speed + TrafficSpeed).

        // Let's implement ONCOMING traffic for 3-lane runner usually.
        // Or overtaking. Let's do overtaking (like simple infinite runner).
        // If overtaking: Obstacles spawn ahead (negative Z) and move towards camera (positive Z).

        const moveDist = $speed * delta;
        // const playerSpeed = $speed; // Player speed

        const playerZ = -2; // Matches Player.svelte visual position
        const currentLane = $lane; // Use floating point lane or round?

        obstacles = obstacles.map((obs) => {
            let playedSound = obs.playedSound;

            // Trigger proximity sound (horn) using Sound Hitbox approach
            const soundBoxDepth = GAME_CONFIG.obstacles.proximitySoundDistance;
            const soundBoxZStart = playerZ;
            const soundBoxZEnd = playerZ - soundBoxDepth;

            const obsDepth = GAME_CONFIG.obstacles.hitbox.depth;
            const obsZStart = obs.z + obsDepth / 2;
            const obsZEnd = obs.z - obsDepth / 2;

            if (
                !playedSound &&
                !$nitroActive &&
                Math.abs(obs.lane - currentLane) < 0.6 &&
                obsZStart > soundBoxZEnd &&
                obsZEnd < soundBoxZStart
            ) {
                if (hornAudio) {
                    // Reset and play for zero latency
                    hornAudio.currentTime = 0;
                    hornAudio.volume = 1.0;
                    hornAudio.play().catch((e) => {
                        log.error("Horn audio failed to play:", e);
                    });
                }
                playedSound = true;
            }
            return { ...obs, z: obs.z + moveDist, playedSound };
        });

        // Remove passed obstacles
        obstacles = obstacles.filter((obs) => obs.z < 20); // Increased limit as they might drift back

        // Collision Detection
        checkCollision();

        // Update global performance metrics
        obstacleCount.set(obstacles.length);
    });

    import { tweened } from "svelte/motion";
    import { cubicIn } from "svelte/easing";

    // --- Animation Stores ---
    const fallY = tweened(0, { duration: 1000, easing: cubicIn });
    const fallRotation = tweened(0, { duration: 1000, easing: cubicIn });

    $: if ($isGameOver) {
        fallY.set(-20);
        fallRotation.set(Math.PI * 2);
    } else {
        fallY.set(0, { duration: 0 });
        fallRotation.set(0, { duration: 0 });
    }

    function spawnObstacle(distance: number) {
        if ($isGameOver || $isTutorial) return; // Don't spawn during fall or tutorial
        const zone = $currentHorizonZone;
        const availableModels =
            trafficModels[zone] && trafficModels[zone].length > 0
                ? trafficModels[zone]
                : trafficModels["city"]; // Fallback

        if (!availableModels || availableModels.length === 0) return;

        // Use deterministic RNG based on distance and seed
        const rng = new SeededRNG($gameSeed + "_obs_" + distance);

        const maxLanes = GAME_CONFIG.lanes.maxLanes;
        const start = -(maxLanes - 1) / 2;
        const lanes = Array.from({ length: maxLanes }, (_, i) => start + i);

        // Pick random lane
        const randomLane = lanes[rng.rangeInt(0, lanes.length)];

        obstacles.push({
            id: distance + "_" + randomLane, // Unique ID for deterministic spawning
            z: GAME_CONFIG.obstacles.spawnDistance, // Spawn far ahead under curve
            lane: randomLane,
            modelIndex: rng.rangeInt(0, availableModels.length),
            // Store which list it belongs to? No, just the index and we need to know the zone OR we clone it here?
            // Actually, if we store index, we need to know WHICH zone list to pick from when rendering.
            // But the obstacle moves, so it retains its "type".
            // Problem: Rendering loop iterates obstacles and uses `obstacleModels[obs.modelIndex]`.
            // We need to store value (clone) or zone+index.
            // Storing the zone is easiest.
            zone: zone, // Add zone property to Obstacle type
            speedOffset: 0,
            speed: 10, // Fixed slow speed for now
            playedSound: false,
        });

        // Force Svelte update
        obstacles = obstacles;
    }

    function checkCollision() {
        if (!$isPlaying || $isGameOver || $isTutorial) return; // No collision in menu, game over, or tutorial
        const playerZ = -2; // Matches Player.svelte visual position
        const collisionThreshold =
            (GAME_CONFIG.obstacles.hitbox.depth +
                GAME_CONFIG.player.hitbox.depth) /
            2;

        const currentLane = $lane; // Use floating point lane or round?
        // Player lane is tweened. Collision should be forgiving or precise?
        // Usually precise: Math.abs(obs.lane - currentLane) < 0.5?
        // Let's use strict lane checking for now.
        // But with tweened float, rounding is best for "in the lane".
        // Wait, currentLane is -1.5? Math.round(-1.5) = -1.
        // We need to check minimal distance.

        for (const obs of obstacles) {
            // Lane collision: check if cars are in same lane
            // Since lanes can be 0.5, we check bounds.
            if (Math.abs(obs.lane - currentLane) < 0.6) {
                // Slightly generous lateral
                if (Math.abs(obs.z - playerZ) < collisionThreshold) {
                    if ($nitroActive) {
                        // Crash through! Maybe add effect/sound later
                        log.log("Nitro Smash!");
                        // Remove obstacle visually? Or send it flying?
                        // For now just ignore collision.
                    } else {
                        log.log("Collision!");
                        if (GAME_CONFIG.development.collisionEnabled) {
                            isGameOver.set(true);
                            isPlaying.set(false);
                        }
                    }
                }
            }
        }
    }
</script>

{#each obstacles as obs (obs.id)}
    {@const modelList = trafficModels[obs.zone] || trafficModels["city"]}
    {#if modelList && modelList[obs.modelIndex]}
        <T.Group
            position.x={obs.lane * GAME_CONFIG.lanes.width}
            position.y={0.5 + $fallY}
            position.z={obs.z}
        >
            <T
                is={modelList[obs.modelIndex].clone()}
                rotation.x={GAME_CONFIG.obstacles.rotation[0] + $fallRotation}
                rotation.y={GAME_CONFIG.obstacles.rotation[1]}
                rotation.z={GAME_CONFIG.obstacles.rotation[2] + $fallRotation}
                scale={GAME_CONFIG.obstacles.scale}
            />

            <!-- Collision Box Visualizer -->
            {#if GAME_CONFIG.development.devMode && GAME_CONFIG.development.showHitboxes}
                <T.Mesh position.y={GAME_CONFIG.obstacles.hitbox.height / 2}>
                    <T.BoxGeometry
                        args={[
                            GAME_CONFIG.obstacles.hitbox.width,
                            GAME_CONFIG.obstacles.hitbox.height,
                            GAME_CONFIG.obstacles.hitbox.depth,
                        ]}
                    />
                    <T.MeshBasicMaterial
                        color="#ff0000"
                        wireframe
                        transparent
                        opacity={0.5}
                    />
                </T.Mesh>
            {/if}
        </T.Group>
    {/if}
{/each}
