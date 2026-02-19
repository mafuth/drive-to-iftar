<script lang="ts">
    import { T, useTask } from "@threlte/core";
    import { useGltf } from "@threlte/extras";
    import { ASSETS } from "$lib/utils/assets";
    import { selectedCharacter } from "$lib/stores/game";

    // Reactive loading
    $: charUrl = ASSETS.characters[$selectedCharacter];
    $: gltf = useGltf(charUrl);

    export let position: [number, number, number] = [0, 0, 0];
    export let rotation: [number, number, number] = [0, 0, 0];
    export let scale: number = 1;

    useTask((delta) => {
        // Simple idle rotation or bobbing?
        // rotation[1] += delta * 0.5; // Rotate slowly
    });
</script>

{#if $gltf}
    <T is={$gltf.scene.clone()} {position} {rotation} {scale} />
{/if}
