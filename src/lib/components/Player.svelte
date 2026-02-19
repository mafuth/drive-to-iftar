<script lang="ts">
    import { T, useTask } from "@threlte/core";
    import { useGltf } from "@threlte/extras";
    import { ASSETS } from "$lib/utils/assets";
    import {
        lane,
        targetLane,
        assignedLane,
        LANE_X_POSITIONS,
        isPlaying,
        isGameOver,
        selectedCar,
        currentSession,
        watermelons,
        nitroActive,
        speed,
        nitroTimer,
        nitroTrigger,
    } from "$lib/stores/game";
    import { GAME_CONFIG } from "$lib/config";
    import { onMount, onDestroy } from "svelte";
    import { tweened } from "svelte/motion";
    import { Vector3 } from "three";
    import { cubicIn, cubicOut } from "svelte/easing";

    const carUrl = ASSETS.cars[$selectedCar];
    const gltf = useGltf(carUrl);

    let carModel: any;
    $: if ($gltf) {
        carModel = $gltf.scene;
    }

    // Smoothly follow target lane
    $: lane.set($targetLane);

    // Nitro Logic
    let preNitroSpeed = GAME_CONFIG.player.speed.initial;

    function activateNitro() {
        if ($nitroActive) return;

        // In multiplayer, everything is shared.
        // We charge watermelons and increment the trigger.
        // The trigger will be picked up by MultiplayerManager to broadcast.
        if ($watermelons >= GAME_CONFIG.player.nitro.watermelonThreshold) {
            watermelons.update(
                (n) => n - GAME_CONFIG.player.nitro.watermelonThreshold,
            );
            nitroTrigger.update((n) => n + 1);
        }
    }

    // Shared action triggered by nitroTrigger (local or remote)
    function performNitroAction() {
        if ($nitroActive) return;

        nitroActive.set(true);
        preNitroSpeed = $speed;
        speed.update((s) => s + GAME_CONFIG.player.nitro.speedBoost);

        const { flyHeight, flySpeed, tiltNitro, tiltEnding, duration } =
            GAME_CONFIG.player.nitro;
        nitroTimer.set(100, { duration: 0 });
        nitroTimer.set(0, { duration });

        carY.set(flyHeight);
        carPitch.set(-0.25, { duration: flySpeed / 2 });

        setTimeout(() => {
            if ($nitroActive) carPitch.set(tiltNitro, { duration: flySpeed });
        }, flySpeed / 2);

        setTimeout(() => {
            if ($nitroActive) carPitch.set(tiltEnding, { duration: 800 });
        }, duration - 1200);

        setTimeout(() => {
            nitroActive.set(false);
            speed.set(preNitroSpeed);
            carY.set(0);
            carPitch.set(0.15, { duration: 300 });
            setTimeout(() => carPitch.set(0), 400);
        }, duration);
    }

    // Reactive trigger for Nitro action
    $: if ($nitroTrigger) {
        performNitroAction();
    }

    // Input Handling
    function handleKeydown(e: KeyboardEvent) {
        if ($isGameOver || !$isPlaying) return;

        if (e.key === "ArrowLeft" || e.key === "ArrowRight") {
            if ($currentSession && $assignedLane !== null) {
                moveToMyLane();
            } else {
                changeLane(e.key === "ArrowLeft" ? -1 : 1);
            }
        }
        if (e.key === "ArrowDown") activateNitro();
    }

    let touchStartX = 0;
    let touchStartY = 0;
    let hasSwipedThisTouch = false;

    function handleTouchStart(e: TouchEvent) {
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
        hasSwipedThisTouch = false;
    }

    function handleTouchMove(e: TouchEvent) {
        if ($isGameOver || !$isPlaying || hasSwipedThisTouch) return;

        const currentX = e.touches[0].clientX;
        const currentY = e.touches[0].clientY;
        const diffX = currentX - touchStartX;
        const diffY = currentY - touchStartY;
        const threshold = 30;

        if (Math.abs(diffX) > Math.abs(diffY)) {
            if (Math.abs(diffX) > threshold) {
                if ($currentSession && $assignedLane !== null) {
                    moveToMyLane();
                } else {
                    changeLane(diffX > 0 ? 1 : -1);
                }
                hasSwipedThisTouch = true;
                e.preventDefault();
            }
        } else if (diffY > threshold) {
            activateNitro();
            hasSwipedThisTouch = true;
            e.preventDefault();
        }
    }

    function moveToMyLane() {
        if ($assignedLane === null) return;
        const maxLanes = GAME_CONFIG.lanes.maxLanes;
        const internal = $assignedLane - (maxLanes + 1) / 2;
        targetLane.set(internal);
    }

    function changeLane(direction: number) {
        const maxLanes = GAME_CONFIG.lanes.maxLanes;
        const maxIndex = (maxLanes - 1) / 2;
        const minIndex = -maxIndex;
        targetLane.update((l) => {
            const nextLane = l + direction;
            return Math.max(minIndex, Math.min(maxIndex, nextLane));
        });
    }

    // Animation Stores
    const playerFallY = tweened(0, { duration: 1000, easing: cubicIn });
    const playerFallRot = tweened(0, { duration: 1000, easing: cubicIn });
    const carY = tweened(0, {
        duration: GAME_CONFIG.player.nitro.flySpeed,
        easing: cubicOut,
    });
    const carPitch = tweened(0, {
        duration: GAME_CONFIG.player.nitro.flySpeed,
        easing: cubicOut,
    });
    const carZ = tweened(8, { duration: 1000, easing: cubicOut });

    $: if ($isGameOver) {
        setTimeout(() => {
            playerFallY.set(-20);
            playerFallRot.set(Math.PI * (Math.random() > 0.5 ? 2 : -2));
        }, 400);
    } else {
        playerFallY.set(0, { duration: 0 });
        playerFallRot.set(0, { duration: 0 });
    }

    let lastLane = 0;
    let bankZ = 0;

    useTask(() => {
        const laneDelta = $lane - lastLane;
        const targetBank =
            -laneDelta * 20 * GAME_CONFIG.player.bankingIntensity;
        bankZ += (targetBank - bankZ) * 0.15;
        lastLane = $lane;
    });

    onMount(() => {
        window.addEventListener("keydown", handleKeydown);
        window.addEventListener("touchstart", handleTouchStart, {
            passive: false,
        });
        window.addEventListener("touchmove", handleTouchMove, {
            passive: false,
        });
        carZ.set(-2);
    });

    onDestroy(() => {
        if (typeof window !== "undefined") {
            window.removeEventListener("keydown", handleKeydown);
            window.removeEventListener("touchstart", handleTouchStart);
            window.removeEventListener("touchmove", handleTouchMove);
        }
    });
</script>

{#if carModel}
    <T.Group
        position.x={$lane * GAME_CONFIG.lanes.width}
        position.y={0.5 + $playerFallY + $carY}
        position.z={$carZ}
    >
        <T
            is={carModel}
            rotation.x={$playerFallRot + $carPitch}
            rotation.y={Math.PI}
            rotation.z={$playerFallRot + bankZ}
            scale={GAME_CONFIG.player.scale}
        />

        {#if GAME_CONFIG.development.devMode && GAME_CONFIG.development.showHitboxes}
            <T.Mesh position.y={GAME_CONFIG.player.hitbox.height / 2}>
                <T.BoxGeometry
                    args={[
                        GAME_CONFIG.player.hitbox.width,
                        GAME_CONFIG.player.hitbox.height,
                        GAME_CONFIG.player.hitbox.depth,
                    ]}
                />
                <T.MeshBasicMaterial
                    color="#0000ff"
                    wireframe
                    transparent
                    opacity={0.5}
                />
            </T.Mesh>
        {/if}
    </T.Group>
{/if}
