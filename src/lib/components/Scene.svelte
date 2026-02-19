<script lang="ts">
    import { T, useTask } from "@threlte/core";
    import { interactivity } from "@threlte/extras";
    import { cubicOut } from "svelte/easing";
    import { tweened } from "svelte/motion";
    import RoadManager from "./RoadManager.svelte";
    import Player from "./Player.svelte";
    import ObstacleSpawner from "./ObstacleSpawner.svelte";
    import CollectibleSpawner from "./CollectibleSpawner.svelte";

    import RivalCar from "./RivalCar.svelte";
    import Sky from "./Sky.svelte";
    import {
        rivals,
        selectedCar,
        isPlaying,
        isGameOver,
        lane,
        initialLane,
    } from "$lib/stores/game";
    import { GAME_CONFIG } from "$lib/config";

    interactivity();

    // Reset lane to center on mount/remount (e.g. restart)
    lane.set(initialLane, { duration: 0 });

    // Camera Logic (Game Mode Only)
    const cameraPos = tweened(GAME_CONFIG.player.camera.position, {
        duration: 1000,
        easing: cubicOut,
    });

    const cameraLookAt = tweened(GAME_CONFIG.player.camera.lookAt, {
        duration: 1000,
        easing: cubicOut,
    });
</script>

<T.PerspectiveCamera
    makeDefault
    position={$cameraPos}
    fov={GAME_CONFIG.player.camera.fov}
    far={2000}
    on:create={({ ref }) => {
        ref.lookAt(...$cameraLookAt);
    }}
    on:update={({ ref }) => {
        ref.lookAt(...$cameraLookAt);
    }}
>
    <!-- <OrbitControls enableDamping /> -->
</T.PerspectiveCamera>

<Sky />

<!-- Game Components -->
<RoadManager />

{#key $selectedCar}
    <Player />
{/key}

<ObstacleSpawner />
<CollectibleSpawner />

{#each [...$rivals.values()] as rivalData (rivalData.id)}
    <RivalCar data={rivalData} />
{/each}
