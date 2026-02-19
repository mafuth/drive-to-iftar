<script lang="ts">
    import {
        score,
        watermelons,
        nitroActive,
        nitroTimer,
        isGameOver,
        isPlaying,
        gameTime,
        totalObjects,
        fps,
        currentSession,
        targetLane,
        assignedLane,
    } from "$lib/stores/game";
    import { GAME_CONFIG } from "$lib/config";
    import { createEventDispatcher, onMount, onDestroy } from "svelte";
    import { fly } from "svelte/transition";

    const dispatch = createEventDispatcher();

    // Nitro Status
    $: canActivateNitro =
        $watermelons >= GAME_CONFIG.player.nitro.watermelonThreshold;
    $: nitroProgress = Math.min(
        100,
        ($watermelons / GAME_CONFIG.player.nitro.watermelonThreshold) * 100,
    );
    $: availableNitros = Math.floor(
        $watermelons / GAME_CONFIG.player.nitro.watermelonThreshold,
    );

    let scoreInterval: any;
    $: if ($isPlaying && !$isGameOver) {
        if (!scoreInterval) {
            scoreInterval = setInterval(() => {
                score.update(
                    (s) => s + ($nitroActive ? 2 : 1) * Math.floor(10),
                ); // Score faster in nitro?
            }, 1000);
        }
    } else {
        clearInterval(scoreInterval);
        scoreInterval = null;
    }

    onDestroy(() => {
        if (scoreInterval) clearInterval(scoreInterval);
    });

    // Reactive Lane Number
    $: currentLaneNumber = Math.round(
        $targetLane + (GAME_CONFIG.lanes.maxLanes + 1) / 2,
    );

    function restart() {
        dispatch("restart");
        isGameOver.set(false);
        isPlaying.set(false);
        score.set(0);
        watermelons.set(0);
        nitroActive.set(false);
    }
</script>

<div
    class="pointer-events-none absolute inset-0 p-6 flex flex-col justify-between z-10"
>
    <!-- Top Bar -->
    <div class="flex justify-between items-start">
        <!-- Score -->
        <div
            class="flex flex-col items-center bg-white/20 backdrop-blur-md p-3 rounded-lg border border-black/10 min-w-24 text-black shadow-lg"
        >
            <div
                class="text-[10px] uppercase tracking-[0.2em] opacity-40 mb-1 font-bold"
            >
                Points
            </div>
            <div class="text-2xl font-bold font-mono">{$score}</div>
        </div>

        {#if $assignedLane !== null}
            <div
                class="flex flex-col items-center bg-amber-500/80 backdrop-blur-md p-3 rounded-lg border border-amber-400/50 min-w-24 ml-4 text-black"
            >
                <div
                    class="text-[10px] uppercase tracking-[0.2em] opacity-80 mb-1 font-bold"
                >
                    Assigned Lane
                </div>
                <div class="text-2xl font-black font-mono">{$assignedLane}</div>
            </div>
        {/if}

        <!-- Power-ups Card -->
        <div class="flex flex-col items-end gap-2">
            <div
                class="backdrop-blur-md bg-white/20 border border-black/10 shadow-lg rounded-xl p-3 text-black flex flex-col gap-3 min-w-[100px]"
            >
                <!-- Watermelons -->
                <div class="flex items-center justify-between gap-3">
                    <div class="text-xs uppercase tracking-widest opacity-60">
                        Watermelons
                    </div>
                    <div class="flex items-center gap-2">
                        <div class="text-sm font-bold font-mono text-green-600">
                            {$watermelons}
                        </div>
                        <div class="text-lg">🍉</div>
                    </div>
                </div>

                <!-- Divider -->
                <div class="h-[1px] bg-black/10 w-full"></div>

                <!-- Nitro -->
                <div class="flex items-center justify-between gap-3">
                    <div class="text-xs uppercase tracking-widest opacity-60">
                        Boost
                    </div>
                    <div class="flex items-center gap-3">
                        {#if availableNitros > 0}
                            <div
                                class="flex items-center gap-1.5"
                                transition:fly={{ x: 10 }}
                            >
                                <div
                                    class="text-sm font-bold font-mono text-pink-600"
                                >
                                    {availableNitros}
                                </div>
                                <div class="text-lg">🥤</div>
                            </div>
                        {/if}

                        <!-- Progress Icon -->
                        <div class="relative w-6 h-8 opacity-80">
                            <!-- Background (Empty) -->
                            <div
                                class="absolute inset-0 flex items-center justify-center text-2xl grayscale brightness-50 opacity-30"
                            >
                                🥤
                            </div>
                            <!-- Fill (Colored revealing from bottom) -->
                            <div
                                class="absolute bottom-0 left-0 right-0 overflow-hidden transition-all duration-300"
                                style="height: {(($watermelons %
                                    GAME_CONFIG.player.nitro
                                        .watermelonThreshold) /
                                    GAME_CONFIG.player.nitro
                                        .watermelonThreshold) *
                                    100}%"
                            >
                                <div
                                    class="absolute bottom-0 left-0 right-0 h-8 flex items-center justify-center text-2xl brightness-110"
                                >
                                    🥤
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {#if $nitroActive}
                <div
                    transition:fly={{ y: 20 }}
                    class="flex flex-col gap-1.5 mt-2 text-center w-full min-w-[120px]"
                >
                    <div
                        class="text-[10px] font-black text-orange-400 tracking-[0.2em] uppercase"
                    >
                        Nitro Active
                    </div>
                    <!-- Progress Bar -->
                    <div
                        class="h-2 w-full bg-white/40 rounded-full overflow-hidden border border-black/10 p-[1px]"
                    >
                        <div
                            class="h-full rounded-full bg-gradient-to-r from-orange-600 via-orange-400 to-yellow-300 shadow-[0_0_10px_rgba(251,146,60,0.5)]"
                            style="width: {$nitroTimer}%"
                        ></div>
                    </div>
                </div>
            {/if}
        </div>
    </div>

    <!-- Dev Mode Time Slider -->
    {#if GAME_CONFIG.development.devMode}
        <div
            class="fixed top-24 left-1/2 -translate-x-1/2 flex flex-col items-center gap-1 bg-black/60 backdrop-blur-md p-3 rounded-xl border border-white/20 z-50 pointer-events-auto"
        >
            <div
                class="text-[10px] font-bold text-white/50 uppercase tracking-widest leading-none mb-1 flex justify-between w-full px-1"
            >
                <span>Time of Day (Dev)</span>
                <span class="text-green-400 opacity-80"
                    >{$fps} FPS | {$totalObjects} Objects</span
                >
            </div>
            <div class="flex items-center gap-3">
                <span
                    class="text-xs text-white tabular-nums w-8 text-center bg-white/10 rounded px-1"
                >
                    {Math.floor($gameTime)}h
                </span>
                <input
                    type="range"
                    min="0"
                    max="23"
                    step="1"
                    bind:value={$gameTime}
                    class="w-32 accent-orange-500 cursor-pointer h-4"
                />
            </div>
        </div>
    {/if}
</div>
