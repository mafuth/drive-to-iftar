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
        targetLane,
        assignedLane,
        score as gameScore,
        collectibleCount,
        totalDistance,
        gameSeed,
        collectEvent,
        dailyChallenge,
        isTutorial,
    } from "$lib/stores/game";
    import { Logger } from "$lib/utils/logger";

    const log = new Logger("Dates");
    import { GAME_CONFIG } from "$lib/config";
    import { applyWorldCurvature } from "$lib/utils/worldBending";
    import { SeededRNG } from "$lib/utils/rng";
    import { api } from "$lib/api";

    type Collectible = {
        id: number | string;
        z: number;
        lane: number;
        model: any;
        rotationOffset: number;
    };

    let collectibles: Collectible[] = [];
    let dateModel: any = null;

    const gltf = useGltf(ASSETS.collectibles.date);

    $: if ($gltf && !dateModel) {
        dateModel = $gltf.scene;
        applyWorldCurvature(dateModel);
    }

    let lastSpawnDistance = 0;
    // Use a smaller hardcoded gap, like watermelons (25), to ensure frequent checks
    const SPAWN_INTERVAL = 30;

    useTask((delta) => {
        if ($isGameOver || !$isPlaying) return;

        // Deterministic Spawning based on distance
        if ($totalDistance - lastSpawnDistance > SPAWN_INTERVAL) {
            const spawnDist =
                Math.floor($totalDistance / SPAWN_INTERVAL) * SPAWN_INTERVAL;
            lastSpawnDistance = spawnDist;

            const rng = new SeededRNG($gameSeed + "_date_" + spawnDist);
            // @ts-ignore
            if (
                !$isTutorial &&
                $dailyChallenge.active &&
                rng.chance(GAME_CONFIG.dates.spawn.chance)
            ) {
                spawnCollectible(spawnDist, rng);
            }
        }

        const moveDist = $speed * delta;

        collectibles = collectibles.map((c) => {
            return { ...c, z: c.z + moveDist };
        });

        // Cleanup
        collectibles = collectibles.filter((c) => c.z < 10);

        checkCollision();
    });

    import { tweened } from "svelte/motion";
    import { cubicIn } from "svelte/easing";

    const fallY = tweened(0, { duration: 1000, easing: cubicIn });

    $: if ($isGameOver) {
        fallY.set(-20);
    } else {
        fallY.set(0, { duration: 0 });
    }

    function spawnCollectible(distance: number, rng: SeededRNG) {
        if (!dateModel || $isGameOver) return;

        const maxLanes = GAME_CONFIG.lanes.maxLanes;
        const start = -(maxLanes - 1) / 2;
        const lanes = Array.from({ length: maxLanes }, (_, i) => start + i);

        // Deterministic lane selection
        const randomLane = lanes[rng.rangeInt(0, lanes.length)];

        collectibles.push({
            id: "date_" + distance,
            // @ts-ignore
            z: GAME_CONFIG.dates.spawnDistance,
            lane: randomLane,
            model: dateModel,
            rotationOffset: rng.next() * Math.PI,
        });
        collectibles = collectibles;
    }

    function checkCollision() {
        if ($isGameOver) return;
        const playerZ = -2; // Matches Player.svelte
        const collisionThreshold =
            // @ts-ignore
            (GAME_CONFIG.dates.hitbox.depth + GAME_CONFIG.player.hitbox.depth) /
            2;
        const currentLane = $lane;

        let collectedIds: (number | string)[] = [];

        for (const c of collectibles) {
            if (
                Math.abs(c.lane - currentLane) < 0.6 &&
                Math.abs(c.z - playerZ) < collisionThreshold
            ) {
                // @ts-ignore
                gameScore.update((s) => s + GAME_CONFIG.dates.points);
                dailyChallenge.update((c) => ({
                    ...c,
                    collected: c.collected + 1,
                }));
                collectedIds.push(c.id);
                log.log("Collected date!");

                // Broadcast collection in multiplayer
                collectEvent.set({
                    amount: 1,
                    // @ts-ignore
                    points: GAME_CONFIG.dates.points,
                    timestamp: Date.now(),
                });

                // Update Daily Challenge in backend
                api.game
                    .collectDate(1)
                    .catch((err) =>
                        console.error("Failed to sync date collection", err),
                    );
            }
        }

        if (collectedIds.length > 0) {
            collectibles = collectibles.filter(
                (c) => !collectedIds.includes(c.id),
            );
        }
    }

    let time = 0;
    useTask((delta) => {
        time += delta;
    });
</script>

{#each collectibles as c (c.id)}
    <T.Group
        position.x={c.lane * GAME_CONFIG.lanes.width}
        position.y={1.5 + Math.sin(time * 3 + c.rotationOffset) * 0.2 + $fallY}
        position.z={c.z}
    >
        <T
            is={dateModel.clone()}
            rotation.y={time * 1.5 + c.rotationOffset + $fallY}
            rotation.x={Math.PI / 6}
            scale={GAME_CONFIG.dates.scale}
        />

        {#if GAME_CONFIG.development.devMode && GAME_CONFIG.development.showHitboxes}
            <T.Mesh>
                <T.BoxGeometry
                    args={[
                        GAME_CONFIG.dates.hitbox.width,
                        GAME_CONFIG.dates.hitbox.height,
                        GAME_CONFIG.dates.hitbox.depth,
                    ]}
                />
                <T.MeshBasicMaterial
                    color="#8B4513"
                    wireframe
                    transparent
                    opacity={0.5}
                />
            </T.Mesh>
        {/if}
    </T.Group>
{/each}
