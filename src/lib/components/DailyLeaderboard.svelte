<script lang="ts">
    import { onMount, onDestroy } from "svelte";
    import { api } from "$lib/api";
    import { fade } from "svelte/transition";
    import { dailyChallenge, datesConfig } from "$lib/stores/game";
    import { GAME_CONFIG } from "$lib/config";

    let leaderboard: {
        username: string;
        dates: number;
        photo: string | null;
    }[] = [];
    let loading = true;
    let now = new Date();
    let refreshInterval: any;
    let countdownInterval: any;

    async function loadLeaderboard() {
        try {
            leaderboard = await api.game.getChallengeLeaderboard();
        } catch (e) {
            console.error("Failed to load daily leaderboard", e);
        } finally {
            loading = false;
        }
    }

    // Reactive Countdown Logic
    $: timeRemaining = (() => {
        // Force dependency on now, dailyChallenge, and datesConfig
        const currentTime = now;
        const active = $dailyChallenge.active;
        const startHour = $datesConfig.startHour || 5;
        const endHour = $datesConfig.endHour || 18;

        // Maldives Time is UTC + 5
        const utc =
            currentTime.getTime() + currentTime.getTimezoneOffset() * 60000;
        const mvtDate = new Date(utc + 5 * 3600000);

        let targetHour = active ? endHour : startHour;

        const targetDate = new Date(mvtDate.getTime());
        targetDate.setHours(targetHour, 0, 0, 0);

        let diff = targetDate.getTime() - mvtDate.getTime();

        // Handle target in the past (move to tomorrow)
        if (diff < 0) {
            targetDate.setDate(targetDate.getDate() + 1);
            diff = targetDate.getTime() - mvtDate.getTime();
        }

        const hours = Math.floor(diff / 3600000);
        const mins = Math.floor((diff % 3600000) / 60000);

        const hText = hours === 1 ? "hour" : "hours";
        const mText = mins === 1 ? "minute" : "minutes";

        const timeStr = `${hours} ${hText} ${mins} ${mText}`;
        return active ? `Ends in ${timeStr}` : `Starting in ${timeStr}`;
    })();

    onMount(() => {
        loadLeaderboard();
        refreshInterval = setInterval(loadLeaderboard, 30000);
        countdownInterval = setInterval(() => {
            now = new Date();
        }, 60000);
    });

    onDestroy(() => {
        if (refreshInterval) clearInterval(refreshInterval);
        if (countdownInterval) clearInterval(countdownInterval);
    });
</script>

<div
    class="w-full bg-white/10 backdrop-blur-md border border-white/10 rounded-2xl p-6 flex flex-col gap-4 h-full"
>
    <div class="flex items-center justify-between">
        <h2
            class="text-white font-bold uppercase tracking-wider flex items-center gap-2"
        >
            <img
                src="/kenney_food-kit/Previews/coconut.png"
                alt="Date"
                class="w-6 h-6 object-contain"
            />
            Today's Top Dates Collectors
        </h2>
        {#if $dailyChallenge.active}
            <div
                class="text-[10px] text-green-400 font-bold px-2 py-0.5 bg-green-900/40 rounded border border-green-500/20 uppercase tracking-wide animate-pulse"
            >
                Live
            </div>
        {:else}
            <div
                class="text-[10px] text-white/40 font-bold px-2 py-0.5 bg-black/20 rounded border border-white/5 uppercase tracking-wide"
            >
                Closed
            </div>
        {/if}
    </div>

    {#if loading}
        <div
            class="flex-1 flex items-center justify-center text-white/30 text-sm animate-pulse"
        >
            Loading...
        </div>
    {:else if leaderboard.length === 0}
        <div
            class="flex-1 flex flex-col items-center justify-center text-white/30 text-sm gap-2"
        >
            <span>No dates collected today yet.</span>
            <span class="text-xs">Be the first!</span>
        </div>
    {:else}
        <div
            class="flex flex-col gap-2 overflow-y-auto pr-1 max-h-[400px] scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent"
        >
            {#each leaderboard as entry, i}
                <div
                    class="flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors"
                >
                    <div
                        class="text-amber-500 font-black italic text-lg w-6 text-center"
                    >
                        #{i + 1}
                    </div>

                    {#if entry.photo}
                        <img
                            src={entry.photo}
                            alt={entry.username}
                            class="w-8 h-8 rounded-full border border-white/10"
                        />
                    {:else}
                        <div
                            class="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-xs font-bold text-white/70"
                        >
                            {entry.username.charAt(0).toUpperCase()}
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
                    </div>

                    <div
                        class="flex items-center gap-1.5 text-amber-400 font-mono font-bold text-lg"
                    >
                        {entry.dates}
                        <span class="text-xs opacity-50">dates</span>
                    </div>
                </div>
            {/each}
        </div>
    {/if}

    <div
        class="text-[10px] text-white/30 text-center uppercase tracking-widest mt-auto pt-2"
    >
        {timeRemaining}
    </div>
</div>
