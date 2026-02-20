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
        score as gameScore,
        watermelons,
        collectibleCount,
        totalDistance,
        gameSeed,
        collectEvent,
        isTutorial,
        tutorialStep,
    } from "$lib/stores/game";
    import { Logger } from "$lib/utils/logger";

    const log = new Logger("Collectibles");
    import { GAME_CONFIG } from "$lib/config";
    import { applyWorldCurvature } from "$lib/utils/worldBending";
    import { SeededRNG } from "$lib/utils/rng";

    type Collectible = {
        id: number | string;
        z: number;
        lane: number;
        model: any;
        rotationOffset: number;
    };

    let collectibles: Collectible[] = [];
    let watermelonModel: any = null;

    const gltf = useGltf(ASSETS.collectibles.watermelon);

    $: if ($gltf && !watermelonModel) {
        watermelonModel = $gltf.scene;
        applyWorldCurvature(watermelonModel);
    }

    let lastSpawnDistance = 0;
    const COLLECTIBLE_GAP = 25; // Spawn check every 25m

    useTask((delta) => {
        if ($isGameOver || !$isPlaying) return;

        // Deterministic Spawning based on distance
        if ($totalDistance - lastSpawnDistance > COLLECTIBLE_GAP) {
            const spawnDist =
                Math.floor($totalDistance / COLLECTIBLE_GAP) * COLLECTIBLE_GAP;
            lastSpawnDistance = spawnDist;

            // Tutorial Logic: Only spawn watermelons during step 2 (Fuel Up)
            if ($isTutorial && $tutorialStep !== 2) return;

            const rng = new SeededRNG($gameSeed + "_col_" + spawnDist);
            if (rng.chance(GAME_CONFIG.collectibles.spawn.chance)) {
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

        // Update global performance metrics
        collectibleCount.set(collectibles.length);
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
        if (!watermelonModel || $isGameOver) return;

        const maxLanes = GAME_CONFIG.lanes.maxLanes;
        const start = -(maxLanes - 1) / 2;
        const lanes = Array.from({ length: maxLanes }, (_, i) => start + i);

        // Deterministic lane selection
        const randomLane = lanes[rng.rangeInt(0, lanes.length)];

        collectibles.push({
            id: "col_" + distance,
            z: GAME_CONFIG.collectibles.spawnDistance,
            lane: randomLane,
            model: watermelonModel,
            rotationOffset: rng.next() * Math.PI,
        });
        collectibles = collectibles;
    }

    function checkCollision() {
        if ($isGameOver) return;
        const playerZ = -2; // Matches Player.svelte
        const collisionThreshold =
            (GAME_CONFIG.collectibles.hitbox.depth +
                GAME_CONFIG.player.hitbox.depth) /
            2;
        const currentLane = $lane;

        let collectedIds: (number | string)[] = [];

        for (const c of collectibles) {
            if (
                Math.abs(c.lane - currentLane) < 0.6 &&
                Math.abs(c.z - playerZ) < collisionThreshold
            ) {
                gameScore.update((s) => s + GAME_CONFIG.collectibles.points);
                watermelons.update((w) => w + 1);
                collectedIds.push(c.id);
                log.log("Collected watermelon!");

                // Broadcast collection in multiplayer
                collectEvent.set({
                    amount: 1,
                    points: GAME_CONFIG.collectibles.points,
                    timestamp: Date.now(),
                });
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
        position.y={1.5 + Math.sin(time * 5 + c.rotationOffset) * 0.3 + $fallY}
        position.z={c.z}
    >
        <T
            is={watermelonModel.clone()}
            rotation.y={time * 2 + c.rotationOffset + $fallY}
            rotation.x={Math.PI / 4}
            scale={GAME_CONFIG.collectibles.scale}
        />

        {#if GAME_CONFIG.development.devMode && GAME_CONFIG.development.showHitboxes}
            <T.Mesh>
                <T.BoxGeometry
                    args={[
                        GAME_CONFIG.collectibles.hitbox.width,
                        GAME_CONFIG.collectibles.hitbox.height,
                        GAME_CONFIG.collectibles.hitbox.depth,
                    ]}
                />
                <T.MeshBasicMaterial
                    color="#00ff00"
                    wireframe
                    transparent
                    opacity={0.5}
                />
            </T.Mesh>
        {/if}
    </T.Group>
{/each}
