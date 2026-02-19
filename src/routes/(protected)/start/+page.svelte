<script lang="ts">
    import { Canvas } from "@threlte/core";
    import StartScene from "$lib/components/StartScene.svelte";
    import StartMenu from "$lib/components/StartMenu.svelte";
    import { isPlaying, isGameOver } from "$lib/stores/game";
    import { onMount } from "svelte";

    onMount(() => {
        isPlaying.set(false);
        isGameOver.set(false);
    });
</script>

<div class="fixed inset-0 w-full h-[100dvh] bg-slate-900 overflow-hidden">
    <Canvas>
        <StartScene />
    </Canvas>

    <StartMenu />
</div>
