<script lang="ts">
    import { Canvas } from "@threlte/core";
    import Scene from "$lib/components/Scene.svelte";
    import HUD from "$lib/components/HUD.svelte";
    import MultiplayerManager from "$lib/components/MultiplayerManager.svelte";
    import { Logger } from "$lib/utils/logger";
    const log = new Logger("Race");
    import {
        isPlaying,
        isGameOver,
        score,
        watermelons,
        nitroActive,
        currentRaceId,
    } from "$lib/stores/game";
    import { onMount } from "svelte";
    import { fade } from "svelte/transition";
    import { browser } from "$app/environment";
    import { goto } from "$app/navigation";
    import { api } from "$lib/api";

    let showFadeOverlay = true;

    onMount(() => {
        isPlaying.set(true);
        isGameOver.set(false);
        score.set(0);
        watermelons.set(0);
        nitroActive.set(false);

        // Hide overlay to fade in
        setTimeout(() => {
            showFadeOverlay = false;
        }, 100);
    });

    $: if ($isGameOver) {
        handleGameOver();
    }

    async function handleGameOver() {
        if ($currentRaceId) {
            log.log(
                "Submitting score for race",
                $currentRaceId,
                "Score:",
                $score,
            );
            try {
                await api.game.submitScore($currentRaceId, $score);
            } catch (e) {
                console.error("Score submission failed", e);
            }
        } else {
            console.warn("No currentRaceId found, score not submitted");
        }
        goto("/gameover");
    }
</script>

<div class="h-screen w-full bg-black">
    {#if showFadeOverlay}
        <div
            transition:fade={{ duration: 1000 }}
            class="fixed inset-0 z-[100] bg-slate-950 pointer-events-none"
        ></div>
    {/if}

    {#if browser}
        <Canvas>
            <Scene />
        </Canvas>
    {/if}

    <HUD />
</div>
