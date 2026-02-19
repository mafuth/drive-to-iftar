<script lang="ts">
    import { T } from "@threlte/core";
    import { useGltf } from "@threlte/extras";
    import { ASSETS } from "$lib/utils/assets";
    import { LANE_X_POSITIONS, totalDistance } from "$lib/stores/game";
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
    $: laneX =
        LANE_X_POSITIONS[String(data.lane) as keyof typeof LANE_X_POSITIONS];

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
