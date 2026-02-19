<script lang="ts">
    import { T, useTask } from "@threlte/core";
    import { useGltf } from "@threlte/extras";
    import { ASSETS } from "$lib/utils/assets";
    import {
        speed,
        isGameOver,
        isPlaying,
        totalDistance,
    } from "$lib/stores/game";
    import { GAME_CONFIG } from "$lib/config";
    import { onMount } from "svelte";
    import { derived } from "svelte/store";
    import {
        applyWorldCurvature,
        updateGlobalCurvature,
    } from "$lib/utils/worldBending";
    import { SeededRNG } from "$lib/utils/rng";
    import {
        gameSeed,
        currentHorizonZone,
        worldModelCount,
    } from "$lib/stores/game";
    import { getZone } from "$lib/utils/game-logic";

    // Constants
    const TILE_LENGTH = GAME_CONFIG.world.tileLength;
    const NUM_TILES = GAME_CONFIG.world.numTiles;

    $: updateGlobalCurvature(GAME_CONFIG.world.curvature);

    // Types
    type RoadSegment = {
        id: number;
        index: number;
        z: number;
        zone: string;
        buildings: {
            x: number;
            zOffset: number;
            modelIndex: number;
            rotation: number;
            scale: number;
        }[];
        lights: {
            x: number;
            zOffset: number;
            rotation: number;
        }[];
    };

    // State
    let segments: RoadSegment[] = [];
    let roadModel: any = null;
    let buildingModels: any[] = [];
    let decorationModels: any[] = [];
    let time = 0;

    // Load Assets
    const gltfRoad = useGltf(ASSETS.road.straight);
    const gltfLight = useGltf(ASSETS.road.light);

    // Dynamic Zone Asset Loading
    function loadZoneAssets(paths: string[]) {
        const stores = paths.map((path) => useGltf(path));
        return derived(stores, ($results) => {
            return $results
                .map((result) => {
                    if (result && result.scene) {
                        const scene = result.scene.clone(); // Clone base
                        applyWorldCurvature(scene);
                        return scene;
                    }
                    return null;
                })
                .filter((scene) => scene !== null);
        });
    }

    const loadedCity = loadZoneAssets(ASSETS.zones.city);
    const loadedSuburbs = loadZoneAssets(ASSETS.zones.suburbs);
    const loadedIndustrial = loadZoneAssets(ASSETS.zones.industrial);
    const loadedNature = loadZoneAssets(ASSETS.zones.nature);
    const loadedBridge = loadZoneAssets(ASSETS.zones.bridge);

    let zoneModels = {
        city: [] as any[],
        suburbs: [] as any[],
        industrial: [] as any[],
        nature: [] as any[],
        bridge: [] as any[],
    };

    $: zoneModels.city = $loadedCity;
    $: zoneModels.suburbs = $loadedSuburbs;
    $: zoneModels.industrial = $loadedIndustrial;
    $: zoneModels.nature = $loadedNature;
    $: zoneModels.bridge = $loadedBridge;

    $: if ($gltfRoad) {
        roadModel = $gltfRoad.scene;
        applyWorldCurvature(roadModel);
    }

    let groundModel: any = null;
    let groundNatureModel: any = null;
    // Removed GLTF ground models

    let lightModel: any = null;
    $: if ($gltfLight) {
        lightModel = $gltfLight.scene;
        applyWorldCurvature(lightModel);
    }

    // Deterministic Generation State
    let segmentGenerationIndex = 0;

    function getSegmentRNG(index: number) {
        return new SeededRNG($gameSeed + "" + index * 100); // Spread seeds
    }

    // Reset logic for restarts
    $: if ($isPlaying) {
        // Only trigger reset if we were previously stopped
        // Actually, initSegments handles the empty segments case.
        // We want to force a reset to 0 for multiplayer consistency.
        if (segments.length === 0) {
            segmentGenerationIndex = 0;
            totalDistance.set(0);
            initSegments();
        }
    } else {
        // Clear segments when stopped to trigger clean init on start
        segments = [];
        segmentGenerationIndex = 0;
    }

    function initSegments() {
        segmentGenerationIndex = 0; // Reset on init
        for (let i = 0; i < NUM_TILES; i++) {
            ensureSegment(i, -i * TILE_LENGTH);
        }
        segments = segments; // Trigger update
    }

    function createBuildings(rng: SeededRNG, zone: string, index: number) {
        // --- GLOBAL TRANSITION BUFFER ---
        const localIndex = index % GAME_CONFIG.zones.segmentLength;
        const buffer = GAME_CONFIG.zones.zoneTransitionGap / 2;

        // Skip spawning at the start and end of the zone to prevent overlap between zones
        if (
            localIndex < buffer ||
            localIndex >= GAME_CONFIG.zones.segmentLength - buffer
        ) {
            return [];
        }

        const newBuildings = [];

        // Calculate dynamic offset based on lane count (starts at 3 lanes)
        const roadHalfWidthIncrease = Math.max(
            0,
            ((GAME_CONFIG.lanes.maxLanes - 3) * GAME_CONFIG.lanes.width) / 2,
        );
        const offset = GAME_CONFIG.buildings.offset + roadHalfWidthIncrease;

        const zoneAssets = ASSETS.zones[zone as keyof typeof ASSETS.zones];
        if (!zoneAssets) return [];
        const modelsCount = zoneAssets.length;

        if (modelsCount === 0) return [];

        let currentZ = 0;

        // Custom logic for Nature (Maldives)
        if (zone === "nature") {
            const output = [];
            while (currentZ < TILE_LENGTH) {
                // Higher density, more organic
                // Left Side
                if (rng.chance(GAME_CONFIG.zones.nature.density)) {
                    output.push({
                        x:
                            -offset +
                            rng.range(
                                -GAME_CONFIG.zones.nature.offsetVariance,
                                GAME_CONFIG.zones.nature.offsetVariance,
                            ),
                        zOffset: currentZ + rng.range(-2, 2),
                        modelIndex: rng.rangeInt(0, modelsCount),
                        rotation: rng.range(0, Math.PI * 2),
                        scale: rng.range(
                            GAME_CONFIG.zones.nature.scale.min,
                            GAME_CONFIG.zones.nature.scale.max,
                        ),
                    });
                }
                // Right Side
                if (rng.chance(GAME_CONFIG.zones.nature.density)) {
                    output.push({
                        x:
                            offset +
                            rng.range(
                                -GAME_CONFIG.zones.nature.offsetVariance,
                                GAME_CONFIG.zones.nature.offsetVariance,
                            ),
                        zOffset: currentZ + rng.range(-2, 2),
                        modelIndex: rng.rangeInt(0, modelsCount),
                        rotation: rng.range(0, Math.PI * 2),
                        scale: rng.range(
                            GAME_CONFIG.zones.nature.scale.min,
                            GAME_CONFIG.zones.nature.scale.max,
                        ),
                    });
                }
                currentZ += 5; // Closer spacing
            }
            return output;
        }

        // Custom logic for Bridge (Boats)
        if (zone === "bridge") {
            const output = [];
            const boatConfig = GAME_CONFIG.zones.bridge.boats;
            while (currentZ < TILE_LENGTH) {
                // Left Side
                if (rng.chance(boatConfig.density)) {
                    output.push({
                        x:
                            -boatConfig.offset -
                            rng.range(0, boatConfig.offsetVariance),
                        zOffset: currentZ + rng.range(-10, 10),
                        modelIndex: rng.rangeInt(0, modelsCount),
                        rotation: rng.range(0, Math.PI * 2),
                        scale: rng.range(
                            boatConfig.scale.min,
                            boatConfig.scale.max,
                        ),
                    });
                }
                // Right Side
                if (rng.chance(boatConfig.density)) {
                    output.push({
                        x:
                            boatConfig.offset +
                            rng.range(0, boatConfig.offsetVariance),
                        zOffset: currentZ + rng.range(-10, 10),
                        modelIndex: rng.rangeInt(0, modelsCount),
                        rotation: rng.range(0, Math.PI * 2),
                        scale: rng.range(
                            boatConfig.scale.min,
                            boatConfig.scale.max,
                        ),
                    });
                }
                currentZ += 20; // Sparse boats
            }
            return output;
        }

        // Standard City/Suburbs/Industrial Logic
        while (currentZ < TILE_LENGTH) {
            // Left Side
            if (rng.chance(GAME_CONFIG.buildings.spawnChance)) {
                newBuildings.push({
                    x: -offset,
                    zOffset: currentZ,
                    modelIndex: rng.rangeInt(0, modelsCount),
                    rotation: -Math.PI / 2, // Face Right
                    scale: rng.range(
                        GAME_CONFIG.buildings.scale.min,
                        GAME_CONFIG.buildings.scale.max,
                    ),
                });
            }

            // Right Side
            if (rng.chance(GAME_CONFIG.buildings.spawnChance)) {
                newBuildings.push({
                    x: offset,
                    zOffset: currentZ,
                    modelIndex: rng.rangeInt(0, modelsCount),
                    rotation: Math.PI / 2, // Face Left
                    scale: rng.range(
                        GAME_CONFIG.buildings.scale.min,
                        GAME_CONFIG.buildings.scale.max,
                    ),
                });
            }

            currentZ += 10;
        }

        return newBuildings;
    }

    function createLights(rng: SeededRNG, zone: string, index: number) {
        // --- GLOBAL TRANSITION BUFFER ---
        const localIndex = index % GAME_CONFIG.zones.segmentLength;
        const buffer = GAME_CONFIG.zones.zoneTransitionGap / 2;

        if (
            localIndex < buffer ||
            localIndex >= GAME_CONFIG.zones.segmentLength - buffer
        ) {
            return [];
        }

        if (zone === "nature") return []; // No streetlights in Maldives nature

        const newLights = [];
        // Calculate dynamic offset based on lane count
        const roadHalfWidthIncrease = Math.max(
            0,
            ((GAME_CONFIG.lanes.maxLanes - 3) * GAME_CONFIG.lanes.width) / 2,
        );
        const offset = GAME_CONFIG.lights.offset + roadHalfWidthIncrease;

        const spawnChance = GAME_CONFIG.lights.spawnChance;

        let currentZ = 5;
        while (currentZ < TILE_LENGTH) {
            // Left Side
            if (rng.chance(spawnChance)) {
                newLights.push({
                    x: -offset,
                    zOffset: currentZ,
                    rotation: 0,
                });
            }
            // Right Side
            if (rng.chance(spawnChance)) {
                newLights.push({
                    x: offset,
                    zOffset: currentZ,
                    rotation: Math.PI,
                });
            }
            currentZ += GAME_CONFIG.lights.spawnInterval;
        }
        return newLights;
    }

    function ensureSegment(id: number, z: number) {
        const generationIndex = segmentGenerationIndex++;
        const rng = getSegmentRNG(generationIndex);

        const zoneName = getZone(generationIndex, $gameSeed);

        // Update global zone state for spawners (only if this is the newest segment at horizon)
        // We assume ensureSegment is called for new segments at the front.
        currentHorizonZone.set(zoneName);

        segments.push({
            id,
            index: generationIndex,
            z,
            zone: zoneName, // Store zone for debugging/visuals
            buildings: createBuildings(rng, zoneName, generationIndex),
            lights: createLights(rng, zoneName, generationIndex),
        });
    }

    useTask((delta) => {
        if ($isGameOver || !$isPlaying) return;

        time += delta;

        // Progressive Difficulty
        if ($speed < GAME_CONFIG.player.speed.max) {
            speed.update((s) => s + delta * GAME_CONFIG.player.speed.increment);
        }

        const moveDistance = $speed * delta;
        totalDistance.update((d) => d + moveDistance);

        segments = segments.map((seg) => {
            let newZ = seg.z + moveDistance;

            if (newZ > TILE_LENGTH * 2) {
                const minZ = Math.min(...segments.map((s) => s.z));
                newZ = minZ - TILE_LENGTH + moveDistance;

                // Recycle Logic
                const generationIndex = segmentGenerationIndex++;
                const rng = getSegmentRNG(generationIndex);
                const zoneName = getZone(generationIndex, $gameSeed);

                // Update horizon zone
                currentHorizonZone.set(zoneName);

                seg.zone = zoneName;
                seg.index = generationIndex;
                seg.buildings = createBuildings(rng, zoneName, generationIndex);
                seg.lights = createLights(rng, zoneName, generationIndex);
            }
            return { ...seg, z: newZ };
        });

        segments = segments;

        // Update performance metrics
        let totalModels = segments.length * 3; // 3 road lanes per segment
        segments.forEach((seg) => {
            totalModels += seg.buildings.length;
            totalModels += seg.lights.length;
            totalModels += 1; // Ground box
        });
        worldModelCount.set(totalModels);
    });

    import { tweened } from "svelte/motion";
    import { cubicIn } from "svelte/easing";

    const buildingFallY = tweened(0, { duration: 1000, easing: cubicIn });
    $: if ($isGameOver) {
        buildingFallY.set(-20);
    } else {
        buildingFallY.set(0, { duration: 0 });
    }

    onMount(() => {
        // Init happens once on mount.
        // Note: For full restart support without remount, we might need a reactive reset.
        speed.set(GAME_CONFIG.player.speed.initial);
        // Clean start
        segments = [];
        initSegments();
    });
</script>

{#each segments as segment (segment.id)}
    <T.Group position.z={segment.z}>
        <!-- Road Tiles Tiled along Z -->
        {#if roadModel}
            <!--
               Tile the road along Z to fill the gap.
               Rotation is [0, PI/2, 0].
               Local X axis aligns with Global Z.
               Scale X is 1.5. Base model size ~2 units? No, roughly 1 unit usually.
               If gap is visible with spacing 3, and Scale X is 1.5.
               Let's try spacing 1.5 to overlap/connect.
               Also tiling count needs to increase to fill 30 units. 30/1.5 = 20 tiles.
            -->
            {#each Array(20) as _, i}
                <T.Group position.z={i * 1.5}>
                    <!-- Dynamic Lanes -->
                    {@const maxLanes = GAME_CONFIG.lanes.maxLanes}
                    {@const start = -(maxLanes - 1) / 2}
                    {#each Array(maxLanes) as _, laneIndex}
                        <T
                            is={roadModel.clone()}
                            position={[
                                (start + laneIndex) * GAME_CONFIG.lanes.width,
                                0,
                                0,
                            ]}
                            scale={GAME_CONFIG.world.roadScale}
                            rotation={GAME_CONFIG.world.roadRotation}
                        />
                    {/each}
                </T.Group>
            {/each}

            <!-- Primitive Ground (BoxGeometry) - Once per segment -->
            <T.Mesh
                position={[0, GAME_CONFIG.world.ground.yOffset, 15]}
                on:create={({ ref }) => applyWorldCurvature(ref)}
            >
                <!-- High depth segments for smooth curving -->
                <T.BoxGeometry
                    args={[
                        GAME_CONFIG.world.ground.width,
                        GAME_CONFIG.world.ground.height,
                        TILE_LENGTH,
                        1,
                        1,
                        64,
                    ]}
                />
                <T.MeshStandardMaterial
                    color={segment.zone === "nature"
                        ? GAME_CONFIG.world.ground.color.nature
                        : segment.zone === "bridge"
                          ? GAME_CONFIG.world.ground.color.bridge
                          : GAME_CONFIG.world.ground.color.city}
                />
            </T.Mesh>
        {/if}

        <!-- Buildings (Boats in Bridge Zone) -->
        {#each segment.buildings as b}
            {#if zoneModels[segment.zone as keyof typeof zoneModels] && zoneModels[segment.zone as keyof typeof zoneModels][b.modelIndex]}
                <!-- Performance Optimization: Only render boats if they are close to the camera (Z distance check) -->
                <!-- Bridge zone is heavy, cull distant boats -->
                {#if segment.zone !== "bridge" || Math.abs(segment.z + b.zOffset) < 150}
                    <T
                        is={zoneModels[segment.zone as keyof typeof zoneModels][
                            b.modelIndex
                        ].clone()}
                        position={[
                            b.x,
                            (segment.zone === "bridge"
                                ? GAME_CONFIG.zones.bridge.boats.yOffset +
                                  Math.sin(
                                      time *
                                          GAME_CONFIG.zones.bridge.boats.bobbing
                                              .speed +
                                          b.x +
                                          b.zOffset,
                                  ) *
                                      GAME_CONFIG.zones.bridge.boats.bobbing
                                          .amplitude
                                : 0) + $buildingFallY,
                            b.zOffset,
                        ]}
                        rotation.y={b.rotation}
                        scale={[b.scale, b.scale, b.scale]}
                    />
                {/if}
            {/if}
        {/each}

        <!-- Lights -->
        <!-- Lights (Skip in Bridge Zone) -->
        {#if lightModel && segment.zone !== "bridge"}
            {#each segment.lights as l}
                <T
                    is={lightModel.clone()}
                    position={[l.x, 0, l.zOffset]}
                    rotation.x={GAME_CONFIG.lights.rotation[0]}
                    rotation.y={(l.x > 0 ? -Math.PI / 2 : Math.PI / 2) +
                        GAME_CONFIG.lights.rotation[1]}
                    rotation.z={GAME_CONFIG.lights.rotation[2]}
                    scale={[
                        GAME_CONFIG.lights.scale,
                        GAME_CONFIG.lights.scale,
                        GAME_CONFIG.lights.scale,
                    ]}
                />
            {/each}
        {/if}
    </T.Group>
{/each}
