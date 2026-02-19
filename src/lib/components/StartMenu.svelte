<script lang="ts">
    import { ASSETS } from "$lib/utils/assets";
    import {
        selectedCharacter,
        selectedCar,
        isPlaying,
        isGameOver,
        score,
        gameSeed,
        selectionDirection,
        currentRaceId,
    } from "$lib/stores/game";
    import { fade } from "svelte/transition";

    let characterIndex = 0;
    let carIndex = 0;

    const characters = ASSETS.characters;
    const cars = ASSETS.cars;

    const characterNames = ["Ahmed", "Sara", "Khalid", "Layla"];

    const carNames = [
        "Sedan Sports",
        "Sport Hatch",
        "Future Racer",
        "Taxi",
        "Police Cruiser",
    ];

    function nextCharacter() {
        selectionDirection.set(-1);
        characterIndex = (characterIndex + 1) % characters.length;
        selectedCharacter.set(characterIndex);
    }

    function prevCharacter() {
        selectionDirection.set(1);
        characterIndex =
            (characterIndex - 1 + characters.length) % characters.length;
        selectedCharacter.set(characterIndex);
    }

    function nextCar() {
        selectionDirection.set(-1);
        carIndex = (carIndex + 1) % cars.length;
        selectedCar.set(carIndex);
    }

    function prevCar() {
        selectionDirection.set(1);
        carIndex = (carIndex - 1 + cars.length) % cars.length;
        selectedCar.set(carIndex);
    }

    import { onMount } from "svelte";
    import { goto, replaceState } from "$app/navigation";

    import { GAME_CONFIG } from "$lib/config";
    import {
        isStarting as isStartingStore,
        currentUser,
        currentSession,
    } from "$lib/stores/game";
    import { api } from "$lib/api";
    import { Logger } from "$lib/utils/logger";

    const log = new Logger("StartMenu");

    let showMultiplayerMenu = false;
    let lobbyIdInput = "";
    async function createLobby() {
        if (!$currentUser) return;
        try {
            const lobby = await api.game.createLobby();
            currentSession.set(lobby);
            showMultiplayerMenu = false;
            goto("/lobby");
        } catch (e) {
            alert("Failed to create lobby");
        }
    }

    async function joinLobby() {
        if (!$currentUser) return;
        if (!lobbyIdInput) return alert("Enter Lobby ID");
        try {
            const lobby = await api.game.joinLobby(lobbyIdInput, carIndex);
            currentSession.set(lobby);
            showMultiplayerMenu = false;
            goto("/lobby");
        } catch (e) {
            alert("Failed to join lobby");
        }
    }

    async function startSinglePlayer() {
        // Trigger transition animation
        isStartingStore.set(true);

        // Wait for animation to finish
        await new Promise((resolve) => setTimeout(resolve, 1000));

        // Seed is managed via config.ts or backend for consistency
        // But we want to ensure backend tracking if logged in
        if ($currentUser) {
            try {
                // We can pass current config or let backend generate it.
                // Race page logic loads config locally if !session.
                // BUT now we want strict tracking.
                // Let's call startSinglePlayer, get race_id.
                // Race page should probably use THAT config? or re-fetch?
                // Simpler: Race page fetches config. We just notify backend "Game Started".
                // But backend needs config to store in Race table.
                const startRes = await api.game.startSinglePlayer(GAME_CONFIG); // Send current local default or let backend override?
                // Actually Race page fetches fresh config.
                // Ideally StartMenu fetches config -> starts game -> navigates.
                // Let's stick to Race page fetching for now to minimize refactor risk,
                // but we need to pass race_id.

                // Let's rely on Race page to fetch config,
                // BUT we need race_id for score submission.
                // If we call startSinglePlayer HERE, we get a race_id AND session_id.
                currentRaceId.set(startRes.race_id);

                // Store Session so MultiplayerManager connects to WS
                // Even for single player, we now use WS for sync
                currentSession.set({
                    session_id: startRes.session_id,
                    host_id: $currentUser.id,
                    players: [
                        {
                            id: $currentUser.id,
                            username: $currentUser.username || "Guest",
                        },
                    ],
                });
            } catch (e) {
                console.error("Failed to track single player game", e);
            }
        }

        // Seed is managed via config.ts to ensure multiplayer sync
        gameSeed.set(GAME_CONFIG.world.seed);
        // currentSession.set(null); // REMOVED: We now WANT session for single player

        isPlaying.set(true);
        isGameOver.set(false);
        score.set(0);
        // We set isStarting to false after navigation in the store reset logic or here
        // Actually, we should set it false so that if we come back it's not stuck
        isStartingStore.set(false);
        goto("/race");
    }

    let touchStartX = 0;
    let hasSwiped = false;

    function handleSwipeStart(e: TouchEvent) {
        touchStartX = e.touches[0].clientX;
        hasSwiped = false;
    }

    function handleSwipeMove(e: TouchEvent) {
        if ($isStartingStore || hasSwiped) return;

        const currentX = e.touches[0].clientX;
        const diffX = currentX - touchStartX;

        // Threshold for selection change
        if (Math.abs(diffX) > 40) {
            hasSwiped = true;
            // Set direction: Negative for Left/Next, Positive for Right/Prev
            selectionDirection.set(diffX < 0 ? -1 : 1);

            // Determine zone: Car (Left 60%) or Driver (Right 40%)
            // Based on where the touch STARTED
            const isDriverZone = touchStartX > window.innerWidth * 0.6;

            if (isDriverZone) {
                if (diffX < 0) nextCharacter();
                else prevCharacter();
            } else {
                if (diffX < 0) nextCar();
                else prevCar();
            }
        }
    }
</script>

{#if !$isStartingStore}
    <div
        class="absolute inset-0 z-10 flex flex-col items-center justify-between p-4 md:p-8 pointer-events-none select-none overflow-hidden"
        transition:fade
    >
        <!-- Top Section -->
        <!-- Back Button -->
        <button
            on:click={() => goto("/")}
            class="absolute left-4 top-4 md:left-8 md:top-8 p-3 text-white/50 hover:text-white transition-all hover:scale-110 active:scale-90 pointer-events-auto z-50 flex items-center gap-2 group"
            title="Back to Dashboard"
        >
            <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="2.5"
                stroke="currentColor"
                class="w-6 h-6 md:w-8 md:h-8"
            >
                <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18"
                />
            </svg>
            <span
                class="hidden md:block text-xs font-bold uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-opacity"
                >Dashboard</span
            >
        </button>

        <!-- Top Section -->
        <div class="mt-4 md:mt-8 text-center pointer-events-auto relative">
            <h1
                class="text-3xl md:text-6xl font-black italic tracking-tighter text-white drop-shadow-[0_5px_15px_rgba(0,0,0,0.5)]"
            >
                DRIVE TO IFTAR
            </h1>
            <div
                class="h-1 w-16 md:w-24 bg-amber-400 mx-auto mt-2 rounded-full shadow-[0_0_10px_#fbbf24]"
            ></div>
        </div>

        <!-- Middle: Swipe Capture Zone (Mobile) -->
        <div
            class="flex-1 w-full pointer-events-auto md:pointer-events-none"
            on:touchstart={handleSwipeStart}
            on:touchmove={handleSwipeMove}
        ></div>

        <!-- Bottom Section -->
        <div
            class="w-full max-w-4xl flex flex-col items-center pointer-events-auto pb-4 md:pb-0"
        >
            <!-- Mobile Selection Info (Non-interactive) -->
            <div
                class="md:hidden flex flex-col items-center mb-6 text-white/70 font-mono text-[10px] uppercase tracking-[0.2em] gap-1.5"
            >
                <div class="flex items-center gap-2">
                    DRIVER:
                    <span class="text-amber-400 font-bold"
                        >{characterNames[characterIndex]}</span
                    >
                </div>
                <div class="flex items-center gap-2">
                    VEHICLE:
                    <span class="text-amber-400 font-bold"
                        >{carNames[carIndex]}</span
                    >
                </div>
                <div
                    class="mt-4 px-3 py-1 bg-white/5 rounded-full text-[8px] text-white/30 tracking-[0.4em] font-bold"
                >
                    SWIPE MODELS TO CHANGE
                </div>
            </div>

            <!-- Selection Row -->
            <div class="hidden md:flex justify-center items-end gap-12 mb-8">
                <!-- Character Selection -->
                <div class="flex flex-col items-center gap-2">
                    <span
                        class="text-white/40 font-mono text-[9px] tracking-[0.3em] uppercase"
                        >Driver</span
                    >
                    <div class="flex items-center gap-4">
                        <button
                            class="w-10 h-10 rounded-full border border-white/10 flex items-center justify-center text-white hover:bg-white/10 active:scale-90 transition-all"
                            on:click={prevCharacter}>&lt;</button
                        >
                        <div
                            class="w-48 text-center text-white font-black italic text-2xl tracking-tight uppercase"
                        >
                            {characterNames[characterIndex]}
                        </div>
                        <button
                            class="w-10 h-10 rounded-full border border-white/10 flex items-center justify-center text-white hover:bg-white/10 active:scale-90 transition-all"
                            on:click={nextCharacter}>&gt;</button
                        >
                    </div>
                </div>

                <!-- Spacer -->
                <div class="h-12 w-[1px] bg-white/10"></div>

                <!-- Car Selection -->
                <div class="flex flex-col items-center gap-2">
                    <span
                        class="text-white/40 font-mono text-[9px] tracking-[0.3em] uppercase"
                        >Vehicle</span
                    >
                    <div class="flex items-center gap-4">
                        <button
                            class="w-10 h-10 rounded-full border border-white/10 flex items-center justify-center text-white hover:bg-white/10 active:scale-90 transition-all"
                            on:click={prevCar}>&lt;</button
                        >
                        <div
                            class="w-48 text-center text-white font-black italic text-2xl tracking-tight uppercase"
                        >
                            {carNames[carIndex]}
                        </div>
                        <button
                            class="w-10 h-10 rounded-full border border-white/10 flex items-center justify-center text-white hover:bg-white/10 active:scale-90 transition-all"
                            on:click={nextCar}>&gt;</button
                        >
                    </div>
                </div>
            </div>

            <!-- Start Buttons -->
            <div
                class="mb-4 flex flex-col gap-3 md:gap-4 items-center w-full md:w-auto px-4 md:px-0"
            >
                <button
                    on:click={startSinglePlayer}
                    class="group relative w-full md:w-auto px-8 md:px-20 py-4 md:py-6 bg-amber-400 hover:bg-white text-black font-black italic text-2xl md:text-4xl tracking-tighter uppercase transition-all duration-300 hover:scale-105 active:scale-95 shadow-[0_10px_30px_rgba(251,191,36,0.3)] hover:shadow-[0_10px_40px_rgba(255,255,255,0.4)]"
                >
                    Single Player
                </button>

                {#if $currentUser && !$currentUser.is_guest}
                    <button
                        on:click={() => (showMultiplayerMenu = true)}
                        class="group relative w-full md:w-auto px-8 md:px-20 py-3 md:py-4 bg-white/10 hover:bg-white/20 text-white font-black italic text-xl md:text-2xl tracking-tighter uppercase transition-all duration-300 hover:scale-105 active:scale-95 border-2 border-white/20"
                    >
                        Multiplayer
                    </button>
                {/if}
            </div>
        </div>
    </div>
{/if}

{#if showMultiplayerMenu}
    <div
        class="fixed inset-0 z-50 flex flex-col justify-end md:items-center md:justify-center bg-black/80 backdrop-blur-sm p-4 md:p-0"
        transition:fade={{ duration: 200 }}
        on:click|self={() => (showMultiplayerMenu = false)}
    >
        <div
            class="w-full max-w-md bg-[#1a1a2e] border border-white/20 rounded-2xl md:rounded-2xl p-5 md:p-8 flex flex-col gap-4 md:gap-6 shadow-2xl animate-in slide-in-from-bottom-10 md:slide-in-from-bottom-0 md:zoom-in-95 duration-300 mb-4 md:mb-0"
        >
            <h2
                class="text-xl md:text-2xl font-black italic text-white uppercase tracking-wider text-center"
            >
                Multiplayer Lobby
            </h2>

            {#if $currentUser}
                <div
                    class="flex items-center gap-3 md:gap-4 bg-white/5 p-3 md:p-4 rounded-xl border border-white/5 overflow-hidden"
                >
                    {#if $currentUser.profile_photo}
                        <img
                            src={$currentUser.profile_photo}
                            alt="Profile"
                            class="w-10 h-10 md:w-12 md:h-12 rounded-full border-2 border-amber-400 flex-shrink-0 object-cover"
                        />
                    {:else}
                        <div
                            class="w-10 h-10 md:w-12 md:h-12 rounded-full border-2 border-amber-400 bg-amber-500/20 flex items-center justify-center text-amber-500 font-bold flex-shrink-0"
                        >
                            {$currentUser.username?.charAt(0).toUpperCase() ||
                                "?"}
                        </div>
                    {/if}
                    <div class="flex-1 min-w-0">
                        <div
                            class="text-[10px] md:text-xs text-white/50 uppercase tracking-widest"
                        >
                            Logged in as
                        </div>
                        <div
                            class="font-bold text-amber-400 text-base md:text-lg truncate"
                            title={$currentUser.username || $currentUser.email}
                        >
                            {$currentUser.username || $currentUser.email}
                        </div>
                    </div>
                </div>

                <div class="flex flex-col gap-3">
                    <button
                        on:click={createLobby}
                        class="w-full py-3 md:py-4 bg-amber-400 hover:bg-white text-black font-black uppercase tracking-wider rounded-xl transition-all shadow-lg text-sm md:text-base"
                    >
                        Create Lobby
                    </button>

                    <div class="flex gap-2 w-full">
                        <input
                            type="text"
                            bind:value={lobbyIdInput}
                            placeholder="Enter Lobby ID"
                            class="flex-1 w-full min-w-0 px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white focus:outline-none focus:border-amber-400 font-mono text-center uppercase placeholder:text-white/20 text-sm md:text-base"
                        />
                        <button
                            on:click={joinLobby}
                            class="px-5 md:px-6 py-3 bg-white/10 hover:bg-white/20 text-white font-bold uppercase rounded-xl border border-white/20 transition-all text-sm md:text-base whitespace-nowrap"
                        >
                            Join
                        </button>
                    </div>
                </div>
            {/if}

            <button
                on:click={() => (showMultiplayerMenu = false)}
                class="w-full py-2 text-white/30 hover:text-white uppercase tracking-widest text-xs md:text-sm transition-colors"
            >
                Cancel
            </button>
        </div>
    </div>
{/if}
