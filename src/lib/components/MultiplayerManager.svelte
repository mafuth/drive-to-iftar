<script lang="ts">
    import { onMount, onDestroy } from "svelte";
    import {
        totalDistance,
        lane,
        targetLane,
        assignedLane,
        rivals,
        selectedCar,
        isPlaying,
        gameSeed,
        currentUser,
        currentSession,
        isGameOver,
        score,
        currentRaceId,
        watermelons,
        nitroActive,
        nitroTrigger,
        collectEvent,
    } from "$lib/stores/game";
    import { get } from "svelte/store";
    import { GAME_CONFIG } from "$lib/config";
    import { api } from "$lib/api";
    import { Logger } from "$lib/utils/logger";

    const log = new Logger("Multiplayer");

    let socket: WebSocket | null = null;
    let reconnectTimeout: any;
    let lastSentTargetLane: number | null = null;
    let lastSentNitroTrigger = 0;
    let lastProcessedCollectTimestamp = 0;
    let submitted = false;

    // Movement Sync: Send when target changes
    $: if ($isPlaying && socket && socket.readyState === WebSocket.OPEN) {
        if ($targetLane !== lastSentTargetLane) {
            lastSentTargetLane = $targetLane;
            socket.send(
                JSON.stringify({
                    type: "move",
                    lane: $targetLane,
                    distance: $totalDistance,
                }),
            );
        }
    }

    // Crash Sync: Notify others when we crash
    $: if (
        $isGameOver &&
        socket &&
        socket.readyState === WebSocket.OPEN &&
        !submitted
    ) {
        submitted = true;
        socket.send(JSON.stringify({ type: "crash", score: $score }));
    }

    // Nitro Sync: Notify others when we trigger nitro
    $: if (
        $isPlaying &&
        socket &&
        socket.readyState === WebSocket.OPEN &&
        $nitroTrigger > lastSentNitroTrigger
    ) {
        lastSentNitroTrigger = $nitroTrigger;
        socket.send(JSON.stringify({ type: "nitro" }));
    }

    // Collect Sync: Notify others when we collect something
    $: if (
        $isPlaying &&
        socket &&
        socket.readyState === WebSocket.OPEN &&
        $collectEvent.timestamp > lastProcessedCollectTimestamp
    ) {
        lastProcessedCollectTimestamp = $collectEvent.timestamp;
        socket.send(
            JSON.stringify({
                type: "collect",
                amount: $collectEvent.amount,
                points: $collectEvent.points,
            }),
        );
    }

    function connect() {
        const session = get(currentSession);
        const user = get(currentUser);

        if (!session || !user) return;

        const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        const host = window.location.host;
        const token = localStorage.getItem("access_token");
        const wsUrl = `${protocol}//${host}/api/game/ws/${session.session_id}?token=${token}`;

        try {
            socket = new WebSocket(wsUrl);

            socket.onopen = () => {
                log.log("Connected to Multiplayer Server");
            };

            socket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.type === "ping") return; // Keep logs clean
                log.log("Message received:", data);
                const localUser = get(currentUser);

                if (data.type === "init") {
                    if (data.seed) gameSeed.set(data.seed);
                }

                if (data.type === "lobby_update") {
                    // Sync players in lobby
                    if (data.players) {
                        rivals.update((currentRivals) => {
                            data.players.forEach((p: any) => {
                                if (p.id !== localUser?.id) {
                                    if (!currentRivals.has(p.id.toString())) {
                                        currentRivals.set(p.id.toString(), {
                                            id: p.id.toString(),
                                            lane: 0, // Initial, will be updated on game_start
                                            distance: 0,
                                            carIndex: 0, // TODO: Sync car index
                                            lastUpdate: Date.now(),
                                        });
                                    }
                                }
                            });
                            return currentRivals;
                        });
                    }
                }

                if (data.type === "game_start") {
                    if (data.config) {
                        Object.assign(GAME_CONFIG, data.config);
                        gameSeed.set(GAME_CONFIG.world.seed);

                        const maxLanes = GAME_CONFIG.lanes.maxLanes;
                        const initIndex = GAME_CONFIG.player.initialLane;
                        const centered = initIndex - (maxLanes + 1) / 2;

                        lane.set(centered, { duration: 0 });
                        targetLane.set(centered);

                        // Capture Assigned Lane
                        if (data.lane_assignments && localUser) {
                            const myLane =
                                data.lane_assignments[localUser.id.toString()];
                            if (myLane !== undefined) {
                                assignedLane.set(myLane);
                            }
                        }

                        // Update Rivals Lanes
                        if (data.lane_assignments) {
                            rivals.update((currentRivals) => {
                                for (const [
                                    userId,
                                    laneIndex,
                                ] of Object.entries(data.lane_assignments)) {
                                    if (
                                        localUser &&
                                        userId !== localUser.id.toString()
                                    ) {
                                        // Convert 1-based index to centered 0-based index
                                        const maxLanes =
                                            GAME_CONFIG.lanes.maxLanes;
                                        const centered =
                                            (laneIndex as number) -
                                            (maxLanes + 1) / 2;

                                        const rival = currentRivals.get(userId);
                                        if (rival) {
                                            rival.lane = centered;
                                        } else {
                                            // Create if missing
                                            currentRivals.set(userId, {
                                                id: userId,
                                                lane: centered,
                                                distance: 0,
                                                carIndex: 0,
                                                lastUpdate: Date.now(),
                                            });
                                        }
                                    }
                                }
                                return currentRivals;
                            });
                        }
                    }
                    if (data.race_id) {
                        currentRaceId.set(data.race_id);
                    }

                    // For retries: Ensure we transition to race page
                    if (!get(isPlaying)) {
                        import("$app/navigation").then(({ goto }) => {
                            submitted = false; // Reset submission flag
                            isPlaying.set(true);
                            isGameOver.set(false);
                            goto("/race");
                        });
                    }
                }

                if (data.type === "move") {
                    if (localUser && data.user_id !== localUser.id) {
                        // Shared Control: Remote moves update LOCAL targetLane
                        lastSentTargetLane = data.lane;
                        targetLane.set(data.lane);

                        // Also update distance for consistency if needed,
                        // but usually distance is driven by local loop.
                        // We might want to sync distance if one client lags?
                        // For now, let's trust the shared control input.
                    }
                }

                if (data.type === "crash") {
                    if (!get(isGameOver)) {
                        isGameOver.set(true);
                        isPlaying.set(false);
                    }
                }

                if (data.type === "nitro") {
                    if (!get(nitroActive)) {
                        // Charge watermelons on remote side too to keep stores in sync
                        watermelons.update((n) =>
                            Math.max(
                                0,
                                n -
                                    GAME_CONFIG.player.nitro
                                        .watermelonThreshold,
                            ),
                        );
                        lastSentNitroTrigger++; // Increment both to keep in sync and prevent rebroadcast
                        nitroTrigger.update((n) => n + 1);
                    }
                }

                if (data.type === "collect") {
                    // Update local stores based on remote collection
                    watermelons.update((w) => w + (data.amount || 1));
                    score.update((s) => s + (data.points || 0));
                }

                if (data.type === "player_disconnected") {
                    rivals.update((m) => {
                        const newMap = new Map(m);
                        if (data.id) newMap.delete(data.id.toString());
                        return newMap;
                    });
                }
            };

            socket.onclose = (e) => {
                log.log("Multiplayer Disconnected", e.code, e.reason);
                socket = null;
                if (get(currentSession)) {
                    reconnectTimeout = setTimeout(connect, 3000);
                }
            };

            socket.onerror = (err) => {
                log.error("WebSocket Error", err);
            };
        } catch (e) {
            reconnectTimeout = setTimeout(connect, 3000);
        }
    }

    $: if ($currentSession && !socket) {
        connect();
    }

    onDestroy(() => {
        if (reconnectTimeout) clearTimeout(reconnectTimeout);
        socket?.close();
    });
</script>
