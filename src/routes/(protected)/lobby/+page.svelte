<script lang="ts">
    import { onMount, onDestroy } from "svelte";
    import { goto } from "$app/navigation";
    import {
        currentUser,
        currentSession,
        lane,
        assignedLane,
        gameSeed,
        currentRaceId,
    } from "$lib/stores/game";
    import { api } from "$lib/api";
    import { ASSETS } from "$lib/utils/assets";
    import { GAME_CONFIG } from "$lib/config";
    import { Logger } from "$lib/utils/logger";

    const log = new Logger("Lobby");

    let socket: WebSocket | null = null;
    let players: any[] = [];
    let isHost = false;
    let error = "";

    onMount(async () => {
        if (!$currentUser || !$currentSession) {
            goto("/");
            return;
        }

        isHost = $currentSession.host_id === $currentUser.id;
        players = $currentSession.players.map((p) => ({
            id: p.id,
            username: p.username,
            carIndex: 0,
        }));

        // Connect to WebSocket
        const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        const token = localStorage.getItem("access_token");
        const host = window.location.host;
        const wsUrl = `${protocol}//${host}/api/game/ws/${$currentSession.session_id}?token=${token}`;

        // Note: In dev, Vite proxies /api, but WS might need explicit port or proxy setup.
        // If vite.config.ts proxies ws, fine. If not, might need port 8000.
        // Let's try proxy path first if configured, else direct.
        // Given vite config in Step 206 proxies /api to localhost:8000, we should use that.
        // WS proxying usually requires `ws: true` in vite config.

        socket = new WebSocket(wsUrl);

        socket.onopen = () => {
            log.log("Connected to Lobby");
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === "lobby_update") {
                players = data.players.map((p: any) => ({
                    id: p.id,
                    username: p.username,
                    carIndex: 0, // Car selection sync can be added later if needed
                }));
            }
            if (data.type === "player_joined") {
                // Prevent duplicates
                if (!players.find((p) => p.id === data.user_id)) {
                    players = [
                        ...players,
                        {
                            id: data.user_id,
                            username: data.username,
                            carIndex: data.car_index,
                        },
                    ];
                }
            }
            if (data.type === "game_start") {
                log.log("Game Starting!", data);

                if (data.config) {
                    // Apply full config from backend
                    Object.assign(GAME_CONFIG, data.config);
                    log.log("Multiplayer Config Applied:", GAME_CONFIG);

                    // Reset Lane
                    // Center is 0.
                    // If maxLanes=3, indices are -1, 0, 1.
                    // initialLane in config is 1-based (e.g. 2 for center)
                    const maxLanes = GAME_CONFIG.lanes.maxLanes;
                    const initIndex = GAME_CONFIG.player.initialLane;
                    const centered = initIndex - (maxLanes + 1) / 2;
                    lane.set(centered, { duration: 0 });
                    lane.set(centered, { duration: 0 });

                    // Capture Assigned Lane (Redundancy for Client)
                    if (data.lane_assignments && $currentUser) {
                        const myLane =
                            data.lane_assignments[$currentUser.id.toString()];
                        if (myLane !== undefined) {
                            assignedLane.set(myLane);
                        }
                    }
                }

                if (data.seed) {
                    gameSeed.set(data.seed);
                }

                if (data.race_id) {
                    currentRaceId.set(data.race_id);
                }
                goto("/race");
            }
            if (data.type === "player_disconnected") {
                // Remove player
                players = players.filter((p) => p.id !== data.id);
            }
        };

        socket.onclose = (e) => {
            log.log("Lobby WS Closed", e.code, e.reason);
            if (e.code === 4003) {
                error = "Authentication failed or not in session";
            } else if (e.code !== 1000) {
                error = "Connection lost. Please try re-joining.";
            }
        };

        socket.onerror = (e) => {
            console.error("WS Error", e);
            error = "Connection error occurred";
        };
    });

    onDestroy(() => {
        if (socket) socket.close();
    });

    async function startGame() {
        if (!isHost) return;
        try {
            const res = await api.game.startGame($currentSession!.session_id);

            // Manually apply config/state for Host (Robustness)
            if (res.config) {
                Object.assign(GAME_CONFIG, res.config);
                gameSeed.set(res.seed || GAME_CONFIG.world.seed);

                // Lane assignments
                if (res.lane_assignments && $currentUser) {
                    const myLane =
                        res.lane_assignments[$currentUser.id.toString()];
                    if (myLane !== undefined) {
                        assignedLane.set(myLane);
                    }
                }

                // Reset Lane Position
                const maxLanes = GAME_CONFIG.lanes.maxLanes;
                const initIndex = GAME_CONFIG.player.initialLane;
                const centered = initIndex - (maxLanes + 1) / 2;
                lane.set(centered, { duration: 0 });
            }

            if (res.race_id) {
                currentRaceId.set(res.race_id);
            }

            goto("/race");
        } catch (e) {
            console.error("Start game failed", e);
            error = "Failed to start game";
        }
    }

    function copyInvite() {
        navigator.clipboard.writeText($currentSession?.session_id || "");
        alert("Lobby ID copied!");
    }
</script>

<div
    class="w-full h-screen bg-black text-white flex flex-col items-center justify-end md:justify-center p-8"
>
    <div
        class="max-w-lg w-full bg-white/10 rounded-xl p-8 backdrop-blur-md border border-white/20"
    >
        <h1 class="text-3xl font-black italic uppercase text-center mb-2">
            Lobby
        </h1>
        <div
            class="text-center text-amber-400 font-mono tracking-widest text-xl mb-8 flex gap-2 justify-center items-center"
        >
            ID: {$currentSession?.session_id}
            <button
                on:click={copyInvite}
                class="p-1 hover:bg-white/20 rounded"
                aria-label="Copy Lobby ID"
                title="Copy Lobby ID"
            >
                <svg
                    class="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    ><path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                    ></path></svg
                >
            </button>
        </div>

        <div class="bg-black/50 rounded-lg p-4 mb-8 min-h-[200px]">
            <h3 class="text-white/50 text-xs uppercase tracking-widest mb-4">
                Players
            </h3>
            <div class="flex flex-col gap-2">
                {#each players as player}
                    <div class="flex items-center gap-3 p-2 bg-white/5 rounded">
                        <div
                            class="w-8 h-8 bg-amber-400 rounded-full flex items-center justify-center text-black font-bold"
                        >
                            {player.username
                                ? player.username
                                      .split("#")[0]
                                      .charAt(0)
                                      .toUpperCase()
                                : "?"}
                        </div>
                        <div class="flex items-baseline gap-1 overflow-hidden">
                            <span class="font-bold truncate"
                                >{player.username.split("#")[0]}</span
                            >
                            <span class="text-white/30 text-[10px]"
                                >#{player.username.split("#")[1] ||
                                    player.id}</span
                            >
                        </div>
                    </div>
                {/each}
            </div>
        </div>

        {#if error}
            <div class="text-red-500 text-center mb-4">{error}</div>
        {/if}

        <div class="flex gap-4">
            <button
                on:click={() => goto("/")}
                class="flex-1 py-3 bg-white/10 hover:bg-white/20 rounded font-bold uppercase transition-all"
            >
                Leave
            </button>

            {#if isHost}
                <button
                    on:click={startGame}
                    class="flex-1 py-3 bg-amber-400 hover:bg-white text-black rounded font-bold uppercase transition-all shadow-[0_0_15px_rgba(251,191,36,0.3)] hover:shadow-[0_0_20px_rgba(251,191,36,0.5)]"
                >
                    Start Race
                </button>
            {:else}
                <div
                    class="flex-1 py-3 bg-white/5 text-white/50 rounded font-bold uppercase text-center cursor-not-allowed"
                >
                    Waiting for Host...
                </div>
            {/if}
        </div>
    </div>
</div>
