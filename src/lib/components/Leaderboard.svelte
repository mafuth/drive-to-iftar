<script lang="ts">
    import { onMount } from "svelte";
    import { api } from "$lib/api";
    import { fade } from "svelte/transition";

    let leaderboard: { username: string; score: number; photo: string }[] = [];
    let loading = true;

    onMount(async () => {
        try {
            const data = await api.game.getLeaderboard();
            // Sort by score desc just in case
            leaderboard = data.sort((a, b) => b.score - a.score);
        } catch (e) {
            console.error("Failed to load leaderboard", e);
        } finally {
            loading = false;
        }
    });
</script>

<div
    class="bg-black/80 backdrop-blur-md border border-white/10 rounded-2xl p-5 md:p-6 w-full max-w-md shadow-2xl"
>
    <h2
        class="text-xl md:text-2xl font-black italic text-white uppercase tracking-wider mb-4 md:mb-6 text-center text-amber-500 drop-shadow-sm"
    >
        Leaderboard
    </h2>

    {#if loading}
        <div class="text-white/50 text-center py-8 animate-pulse">
            Loading drivers...
        </div>
    {:else if leaderboard.length === 0}
        <div class="text-white/50 text-center py-8">
            No records yet. Be the first!
        </div>
    {:else}
        <div class="flex flex-col gap-3 max-h-[400px] overflow-y-auto pr-1">
            {#each leaderboard as entry, i}
                <div
                    class="flex items-center gap-3 md:gap-4 p-3 rounded-xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors shrink-0"
                    in:fade={{ delay: i * 50 }}
                >
                    <div
                        class="font-mono text-amber-500 font-bold text-base md:text-lg w-6"
                    >
                        {i + 1}
                    </div>

                    {#if entry.photo}
                        <img
                            src={entry.photo}
                            alt={entry.username}
                            class="w-8 h-8 md:w-10 md:h-10 rounded-full border border-white/20"
                        />
                    {:else}
                        <div
                            class="w-8 h-8 md:w-10 md:h-10 rounded-full border border-white/20 bg-white/10 flex items-center justify-center text-xs text-white/50"
                        >
                            {entry.username?.charAt(0).toUpperCase() || "?"}
                        </div>
                    {/if}

                    <div class="flex-1 min-w-0">
                        <div class="flex items-baseline gap-1 overflow-hidden">
                            <span class="text-white font-bold truncate text-sm">
                                {(entry.username || "Anonymous").split("#")[0]}
                            </span>
                            <span class="text-white/30 text-[10px]">
                                #{(entry.username || "").split("#")[1] || "?"}
                            </span>
                        </div>
                        <div
                            class="text-white/40 text-[10px] md:text-xs uppercase tracking-wider"
                        >
                            Score
                        </div>
                    </div>

                    <div
                        class="font-mono text-xl md:text-2xl text-white font-black"
                    >
                        {entry.score}
                    </div>
                </div>
            {/each}
        </div>
    {/if}
</div>
