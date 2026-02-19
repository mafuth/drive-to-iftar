<script lang="ts">
    import { onMount } from "svelte";
    import { api } from "$lib/api";
    import { currentUser } from "$lib/stores/game";
    import { goto, replaceState } from "$app/navigation";
    import { fade } from "svelte/transition";
    import Leaderboard from "$lib/components/Leaderboard.svelte";
    import HowToPlay from "$lib/components/HowToPlay.svelte";
    import { loadGameConfig } from "$lib/config";
    import { Logger } from "$lib/utils/logger";

    const log = new Logger("Auth");

    let loading = true;
    let showTutorial = false;
    let isNewPlayer = false;

    onMount(async () => {
        await loadGameConfig();

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
</script>

<div
    class="min-h-[100dvh] bg-slate-900 flex flex-col items-center justify-center p-4 relative overflow-hidden"
>
    <!-- Background Decor (Optional) -->
    <div class="absolute inset-0 opacity-10 pointer-events-none"></div>

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
            <div class="text-center">
                <h1
                    class="text-4xl md:text-6xl font-black italic tracking-tighter text-white drop-shadow-[0_5px_15px_rgba(0,0,0,0.5)]"
                >
                    DRIVE TO IFTAR
                </h1>
                <div
                    class="h-1 w-24 bg-amber-400 mx-auto mt-2 rounded-full shadow-[0_0_10px_#fbbf24]"
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

                        {#if $currentUser.is_guest}
                            <div
                                class="bg-amber-500/10 border border-amber-500/20 text-amber-500 text-xs p-3 rounded-lg flex items-center gap-2"
                            >
                                <span class="text-lg">⚠️</span>
                                <div>
                                    playing as Guest. Score won't persist.
                                </div>
                            </div>
                        {/if}
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
                <div class="w-full order-2 md:order-1">
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
                <p
                    class="text-amber-500/70 text-xs text-center mt-2 px-2 font-mono"
                >
                    Your score won't appear on the leaderboard and multiplayer
                    will not be available in guest player mode.
                </p>
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
