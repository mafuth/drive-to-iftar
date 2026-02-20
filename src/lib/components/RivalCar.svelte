<script lang="ts">
    import { T } from "@threlte/core";
    import { useGltf } from "@threlte/extras";
    import { ASSETS } from "$lib/utils/assets";
    import { totalDistance } from "$lib/stores/game";
    import { GAME_CONFIG } from "$lib/config";
    import { applyWorldCurvature } from "$lib/utils/worldBending";
    import { onDestroy } from "svelte";

    export let data: {
        id: string;
        lane: number;
        distance: number;
        carIndex: number;
    };

    // Find car asset
    const carPaths = Object.values(ASSETS.cars);
    const carPath = carPaths[data.carIndex] || carPaths[0];
    const gltf = useGltf(carPath);

    let model: any = null;
    $: if ($gltf) {
        model = $gltf.scene.clone();
        applyWorldCurvature(model);
    }

    // Relative Z position:
    // Player is at Z=2.
    // If rival is 10m ahead, their Z should be 2 - 10 = -8.
    $: relativeZ = 2 - ($totalDistance - data.distance);

    // Dynamic X calculation based on lane index (0-based from DB/Backend)
    // We need to center it relative to the road.
    // Backend assigns 1-based index (1, 2, ...).
    // Wait, backend assigns logic uses 1-based index in `game.py`: `available_lanes = list(range(1, max_lanes + 1))`
    // But `data.lane` comes from `targetLane`, which is CENTERED index (force-centered in frontend store).
    // Let's verify `MultiplayerManager`.
    // Receiver: `targetLane.set(data.lane)`.
    // Sender: `socket.send({ lane: $targetLane })`.
    // So `data.lane` IS the centered index (e.g. -0.5, 0.5).
    // So we just multiply by width.
    $: laneX = data.lane * GAME_CONFIG.lanes.width;

    // Visibility check
    $: isVisible = relativeZ > -100 && relativeZ < 20;
</script>

{#if isVisible && model}
    <T
        is={model}
        position.x={laneX}
        position.y={0.2}
        position.z={relativeZ}
        rotation.y={Math.PI}
        scale={0.5}
    />
{/if}
