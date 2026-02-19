<script lang="ts">
    import { onMount } from "svelte";
    import { api } from "$lib/api";
    import { currentUser } from "$lib/stores/game";
    import { goto, replaceState } from "$app/navigation";
    import { fade } from "svelte/transition";
    import DailyLeaderboard from "$lib/components/DailyLeaderboard.svelte";
    import Leaderboard from "$lib/components/Leaderboard.svelte";
    import HowToPlay from "$lib/components/HowToPlay.svelte";
    import { loadGameConfig, GAME_CONFIG } from "$lib/config";
    import { Logger } from "$lib/utils/logger";
    import { datesConfig, dailyChallenge } from "$lib/stores/game";

    const log = new Logger("Auth");

    let loading = true;
    let showTutorial = false;
    let isNewPlayer = false;

    onMount(async () => {
        await loadGameConfig();
        // Update reactive store for dates
        // Update reactive store for dates
        if (GAME_CONFIG.dates) {
            log.log("Syncing dates config:", GAME_CONFIG.dates);
            datesConfig.set({
                startHour: GAME_CONFIG.dates.startHour ?? 1,
                endHour: GAME_CONFIG.dates.endHour ?? 24,
                target: GAME_CONFIG.dates.target ?? 10,
            });
        } else {
            log.error("GAME_CONFIG.dates is missing!");
        }

        // Fetch Daily Challenge Status
        try {
            const status = await api.game.getChallengeStatus();
            dailyChallenge.set(status);
        } catch (e) {
            log.error("Failed to load challenge status", e);
        }

        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get("code");

        if (code) {
            try {
                const user = await api.auth.login(code);
                currentUser.set(user);
                replaceState("/", {});
            } catch (e) {
                log.error("Login failed", e);
            }
        } else if (!$currentUser) {
            try {
                const user = await api.auth.getMe();
                currentUser.set(user);
            } catch (e) {
                log.log("Dashboard: No active session");
            }
        }
        loading = false;
    });

    // Reactive check for tutorial when user loads
    $: if (!loading && $currentUser) {
        const seen = localStorage.getItem("tutorial_seen");
        isNewPlayer = $currentUser.score === 0;

        if (!seen && (isNewPlayer || $currentUser.is_guest)) {
            // Tiny delay for smooth entrance
            setTimeout(() => {
                showTutorial = true;
            }, 500);
        }
    }

    // ... (rest of script)

    // In layout:
    // User Column: order-2 md:order-1 (Left on Desktop)
    // Leaderboard Column: order-1 md:order-2 (Right on Desktop)
    // This is correct for "Leaderboard on Right" on PC.

    // Add manual trigger to "Welcome Back" section
    // ...

    async function handleLogin() {
        try {
            const config = await api.auth.getAuthConfig();
            const client_id = config.client_id;
            const issuer = config.issuer;
            const redirect_uri = window.location.origin;
            const scope = "openid profile email";

            window.location.href = `${issuer}/oauth/v2/authorize?client_id=${client_id}&redirect_uri=${redirect_uri}&response_type=code&scope=${scope}`;
        } catch (e) {
            console.error("Failed to start login", e);
            alert("Could not load login configuration");
        }
    }

    async function playAsGuest() {
        try {
            const user = await api.auth.guestLogin();
            currentUser.set(user);
        } catch (e) {
            console.error("Guest login failed", e);
            alert("Could not start guest session");
        }
    }

    function logout() {
        localStorage.removeItem("access_token");
        currentUser.set(null);
    }

    function startNewGame() {
        goto("/start");
    }

    let isFullScreen = false;

    function toggleFullScreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
            isFullScreen = true;
        } else if (document.exitFullscreen) {
            document.exitFullscreen();
            isFullScreen = false;
        }
    }

    onMount(() => {
        const handleFullScreenChange = () => {
            isFullScreen = !!document.fullscreenElement;
        };
        document.addEventListener("fullscreenchange", handleFullScreenChange);
        return () => {
            document.removeEventListener(
                "fullscreenchange",
                handleFullScreenChange,
            );
        };
    });
</script>

<div
    class="min-h-[100dvh] bg-slate-900 flex flex-col items-center justify-center p-4 relative overflow-hidden"
>
    <!-- Background Decor (Optional) -->
    <div class="absolute inset-0 opacity-10 pointer-events-none"></div>

    <!-- Full Screen Toggle -->
    <!-- Full Screen Toggle -->
    <button
        class="fixed top-4 right-4 md:top-6 md:right-6 z-[100] p-3 text-white/50 hover:text-white bg-black/20 hover:bg-black/40 backdrop-blur-sm rounded-full transition-all border border-white/5"
        on:click={toggleFullScreen}
        aria-label="Toggle Fullscreen"
    >
        {#if isFullScreen}
            <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="1.5"
                stroke="currentColor"
                class="w-6 h-6 md:w-7 md:h-7"
            >
                <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M9 9V4.5M9 9H4.5M9 9L3.75 3.75M9 15v4.5M9 15H4.5M9 15l-5.25 5.25M15 9h4.5M15 9V4.5M15 9l5.25-5.25M15 15h4.5M15 15v4.5M15 15l5.25 5.25"
                />
            </svg>
        {:else}
            <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="1.5"
                stroke="currentColor"
                class="w-6 h-6 md:w-7 md:h-7"
            >
                <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M3.75 3.75v4.5m0-4.5h4.5m-4.5 0L9 9M3.75 20.25v-4.5m0 4.5h4.5m-4.5 0L9 15M20.25 3.75h-4.5m4.5 0v4.5m0-4.5L15 9M20.25 20.25h-4.5m4.5 0v-4.5m0 4.5L15 15"
                />
            </svg>
        {/if}
    </button>

    {#if loading}
        <div class="text-white/50 animate-pulse text-xl">
            Loading Dashboard...
        </div>
    {:else if $currentUser}
        <!-- Dashboard View -->
        <!-- Dashboard View -->
        <div
            class="flex flex-col items-center gap-8 w-full max-w-5xl z-10"
            transition:fade
        >
            <!-- Title -->
            <div class="text-left w-full md:text-center">
                <h1
                    class="text-4xl md:text-6xl font-black italic tracking-tighter text-white drop-shadow-[0_5px_15px_rgba(0,0,0,0.5)]"
                >
                    DRIVE TO IFTAR
                </h1>
                <div
                    class="h-1 w-24 bg-amber-400 md:mx-auto mt-2 rounded-full shadow-[0_0_10px_#fbbf24]"
                ></div>
            </div>

            <div
                class="w-full grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8 items-start"
            >
                <!-- Left Column: User & Actions -->
                <div
                    class="flex flex-col gap-4 md:gap-6 w-full order-1 md:order-2"
                >
                    <!-- User Profile Card -->
                    <div
                        class="bg-white/10 backdrop-blur-md border border-white/10 rounded-2xl p-5 md:p-6 flex flex-col gap-4"
                    >
                        <div class="flex items-center gap-4">
                            {#if $currentUser.profile_photo}
                                <img
                                    src={$currentUser.profile_photo}
                                    alt="Profile"
                                    class="w-14 h-14 md:w-16 md:h-16 rounded-full border-2 border-amber-400"
                                />
                            {:else}
                                <div
                                    class="w-14 h-14 md:w-16 md:h-16 rounded-full border-2 border-amber-400 bg-amber-500/20 flex items-center justify-center text-amber-500 font-bold text-xl md:text-2xl"
                                >
                                    {$currentUser.username
                                        ?.charAt(0)
                                        .toUpperCase() || "G"}
                                </div>
                            {/if}
                            <div class="flex-1">
                                <div
                                    class="text-white/50 text-xs md:text-sm uppercase tracking-wider flex items-center justify-between"
                                >
                                    <div class="flex items-center gap-2">
                                        <span>Welcome Back</span>
                                        {#if $currentUser.rank}
                                            <span
                                                class="text-amber-400 font-bold"
                                                >• RANK #{$currentUser.rank}</span
                                            >
                                        {/if}
                                    </div>
                                </div>
                                <h1
                                    class="text-2xl md:text-3xl font-black italic text-white leading-none break-all flex items-baseline gap-1"
                                >
                                    <span
                                        >{$currentUser.username?.split(
                                            "#",
                                        )[0] || "Guest Driver"}</span
                                    >
                                    {#if $currentUser.username?.includes("#")}
                                        <span
                                            class="text-white/30 text-sm md:text-base not-italic font-mono"
                                            >#{$currentUser.username.split(
                                                "#",
                                            )[1]}</span
                                        >
                                    {/if}
                                </h1>
                            </div>
                        </div>

                        <!-- How to Play Button (Prominent) -->
                        <button
                            on:click={() => (showTutorial = true)}
                            class="w-full py-3 bg-white/10 hover:bg-white/20 border border-white/20 rounded-xl flex items-center justify-center gap-2 text-xs md:text-sm text-white font-bold uppercase tracking-wider transition-all shadow-lg hover:scale-[1.02] active:scale-95"
                        >
                            <span class="text-amber-400 text-lg">?</span>
                            <span>How To Play</span>
                        </button>
                    </div>

                    <!-- Actions -->
                    <button
                        on:click={startNewGame}
                        class="group relative py-5 md:py-6 bg-amber-400 hover:bg-white text-black font-black italic text-3xl md:text-4xl tracking-tighter uppercase transition-all duration-300 hover:scale-[1.02] active:scale-95 shadow-[0_10px_30px_rgba(251,191,36,0.3)] hover:shadow-[0_10px_40px_rgba(255,255,255,0.4)] rounded-xl flex items-center justify-center gap-3 md:gap-4"
                    >
                        <span>Start Race</span>
                        <span
                            class="group-hover:translate-x-2 transition-transform"
                            >→</span
                        >
                    </button>

                    <button
                        on:click={logout}
                        class="py-3 md:py-4 bg-white/5 hover:bg-white/10 text-white/50 hover:text-white font-bold uppercase tracking-wider rounded-xl transition-all border border-white/10 text-sm md:text-base"
                    >
                        Logout
                    </button>
                </div>

                <!-- Right Column: Leaderboard -->
                <div class="w-full order-2 md:order-1 flex flex-col gap-6">
                    <DailyLeaderboard />
                    <Leaderboard />
                </div>
            </div>
        </div>
    {:else}
        <!-- Login View -->
        <div
            class="w-full max-w-md z-10 flex flex-col items-center gap-8"
            transition:fade
        >
            <div class="text-center">
                <h1
                    class="text-5xl md:text-7xl font-black italic tracking-tighter text-white drop-shadow-[0_5px_15px_rgba(0,0,0,0.5)] mb-2"
                >
                    DRIVE TO IFTAR
                </h1>
                <div
                    class="h-1 w-24 bg-amber-400 mx-auto rounded-full shadow-[0_0_10px_#fbbf24]"
                ></div>
            </div>

            <div
                class="w-full bg-white/10 backdrop-blur-md border border-white/10 rounded-2xl p-8 flex flex-col gap-4 shadow-2xl"
            >
                <button
                    on:click={handleLogin}
                    class="w-full py-4 bg-white text-black font-bold uppercase tracking-wider rounded-xl hover:bg-gray-200 transition-all shadow-lg"
                >
                    Login
                </button>

                <div class="flex items-center gap-4 opacity-50">
                    <div class="h-[1px] bg-white flex-1"></div>
                    <span class="text-white text-xs uppercase">or</span>
                    <div class="h-[1px] bg-white flex-1"></div>
                </div>

                <button
                    on:click={playAsGuest}
                    class="w-full py-3 bg-white/5 hover:bg-white/10 text-white font-bold uppercase tracking-wider rounded-xl border border-white/10 transition-all"
                >
                    Continue as Guest
                </button>
            </div>
        </div>
    {/if}

    <HowToPlay
        bind:show={showTutorial}
        {isNewPlayer}
        on:close={() => (showTutorial = false)}
    />

    <!-- Footer / Credits -->
    <a
        href="https://github.com/mafuth/drive-to-iftar"
        target="_blank"
        rel="noopener noreferrer"
        class="mt-8 relative md:fixed md:bottom-4 md:right-4 md:mt-0 z-50 flex items-center gap-2 px-3 py-1.5 bg-black/40 hover:bg-black/60 backdrop-blur-md border border-white/10 rounded-full text-white/50 hover:text-white transition-all text-xs font-mono uppercase tracking-wider group"
    >
        <svg
            class="w-4 h-4 opacity-70 group-hover:opacity-100 transition-opacity"
            fill="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
        >
            <path
                fill-rule="evenodd"
                d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
                clip-rule="evenodd"
            />
        </svg>
        <span>Source</span>
    </a>
</div>
