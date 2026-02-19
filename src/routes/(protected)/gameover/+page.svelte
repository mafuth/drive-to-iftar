<script lang="ts">
    import { Canvas } from "@threlte/core";
    import GameOverScene from "$lib/components/GameOverScene.svelte";
    import {
        isPlaying,
        isGameOver,
        score,
        currentUser,
        currentSession,
        assignedLane,
        gameSeed,
        currentRaceId,
    } from "$lib/stores/game";
    import { GAME_CONFIG } from "$lib/config";
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import { fade } from "svelte/transition";
    import { api } from "$lib/api";

    onMount(() => {
        isPlaying.set(false);
        // isGameOver should be true from the store, or we force it?
        // If we force it true, GameOverScene (if it checks it) will show.
        isGameOver.set(true);
    });

    $: isHost = $currentSession && $currentUser?.id === $currentSession.host_id;

    async function handleRetry() {
        if ($currentSession) {
            try {
                // Host calls retry endpoint
                await api.game.retryGame($currentSession.session_id);
            } catch (e) {
                console.error("Retry failed", e);
            }
        } else {
            // Single player retry: Fetch new config/seed from backend
            try {
                const res = await api.game.startSinglePlayer();
                if (res.config) {
                    Object.assign(GAME_CONFIG, res.config);
                    gameSeed.set(GAME_CONFIG.world.seed);
                }
                currentRaceId.set(res.race_id);
                restart();
            } catch (e) {
                console.error("Single player retry failed", e);
                // Fallback to simple restart if API fails
                restart();
            }
        }
    }

    function restart() {
        isGameOver.set(false);
        score.set(0);
        assignedLane.set(null);
        isPlaying.set(true); // Ensure playing is true for race page
        goto("/race");
    }

    function menu() {
        goto("/");
    }
</script>

<div class="fixed inset-0 w-full h-[100dvh] bg-slate-900 overflow-hidden">
    <Canvas>
        <GameOverScene />
    </Canvas>

    <!-- UI Overlay -->
    <div
        class="absolute inset-0 flex flex-col items-center justify-end pointer-events-none z-50 pb-24"
    >
        <div class="pointer-events-auto text-center" transition:fade>
            <h1
                class="text-6xl md:text-8xl font-black text-red-600 drop-shadow-lg italic mb-4"
            >
                CRASHED!
            </h1>

            <div class="text-4xl font-mono font-bold text-white mb-8">
                SCORE: {$score}
            </div>

            <div class="flex gap-4 justify-center">
                <button
                    on:click={menu}
                    class="px-8 py-4 bg-slate-800 text-white font-bold rounded-full hover:bg-slate-700 transition-all border border-white/10"
                >
                    MENU
                </button>

                {#if !$currentSession || isHost}
                    <button
                        on:click={handleRetry}
                        class="px-12 py-4 bg-gradient-to-r from-orange-500 to-red-600 text-white font-black text-xl rounded-full shadow-lg hover:scale-105 transition-all"
                    >
                        {$currentSession ? "RETRY SESSION" : "RETRY"}
                    </button>
                {:else}
                    <button
                        disabled
                        class="px-12 py-4 bg-slate-700 text-white/50 font-black text-xl rounded-full shadow-lg cursor-not-allowed border border-white/5"
                    >
                        WAITING FOR HOST
                    </button>
                {/if}
            </div>
        </div>
    </div>
</div>
