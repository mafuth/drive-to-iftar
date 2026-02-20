<script lang="ts">
    import { Canvas } from "@threlte/core";
    import Scene from "$lib/components/Scene.svelte";
    import HUD from "$lib/components/HUD.svelte";
    import MultiplayerManager from "$lib/components/MultiplayerManager.svelte";
    import TutorialOverlay from "$lib/components/TutorialOverlay.svelte";
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
    import { onMount, onDestroy } from "svelte";
    import { fade } from "svelte/transition";
    import { browser } from "$app/environment";
    import { goto } from "$app/navigation";
    import { api } from "$lib/api";
    import { ASSETS } from "$lib/utils/assets";
    import { isMuted } from "$lib/stores/game";

    let showFadeOverlay = true;
    let bgMusic: HTMLAudioElement | null = null;

    $: if (bgMusic) {
        bgMusic.muted = $isMuted;
    }

    onMount(() => {
        isGameOver.set(false);
        isPlaying.set(true);
        score.set(0);
        watermelons.set(0);
        nitroActive.set(false);

        // Background Music setup
        if (browser && ASSETS.music.length > 0) {
            const randomTrack =
                ASSETS.music[Math.floor(Math.random() * ASSETS.music.length)];
            bgMusic = new Audio(randomTrack);
            bgMusic.loop = true;
            bgMusic.volume = 0.2;
            bgMusic.play().catch((e) => {
                log.warn(
                    "Auto-play blocked, music will start after interaction",
                    e,
                );
            });
        }

        // Hide overlay to fade in
        setTimeout(() => {
            showFadeOverlay = false;
        }, 100);
    });

    onDestroy(() => {
        if (bgMusic) {
            bgMusic.pause();
            bgMusic = null;
        }
    });

    $: if ($isGameOver) {
        handleGameOver();
    }

    async function handleGameOver() {
        if (bgMusic) {
            // Fade out music
            const fadeInterval = setInterval(() => {
                if (bgMusic && bgMusic.volume > 0.05) {
                    bgMusic.volume -= 0.05;
                } else {
                    bgMusic?.pause();
                    clearInterval(fadeInterval);
                }
            }, 50);
        }

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

    <TutorialOverlay />
    <HUD />
</div>
