<script lang="ts">
    import { T, useTask } from "@threlte/core";
    import { useGltf, Float, ContactShadows } from "@threlte/extras";
    import { ASSETS } from "$lib/utils/assets";
    import {
        selectedCharacter,
        selectedCar,
        selectionDirection,
        isStarting,
    } from "$lib/stores/game";
    import { GAME_CONFIG } from "$lib/config";
    import { tweened } from "svelte/motion";
    import { cubicInOut, cubicOut, cubicIn } from "svelte/easing";
    import { onMount } from "svelte";

    // --- Animation Stores ---
    const carZ = tweened(0, { duration: 600, easing: cubicInOut });
    const carY = tweened(0.1, { duration: 1000, easing: cubicIn }); // Changed to cubicIn for gravity feel
    const carFallRotation = tweened(0, { duration: 1000, easing: cubicIn });
    const charOpacity = tweened(1, { duration: 500, easing: cubicOut });

    let currentCarIdx = $selectedCar;
    let prevCarIdx = $selectedCar;
    let isCarTransitioning = false;

    let currentCharIdx = $selectedCharacter;
    let prevCharIdx = $selectedCharacter;
    let isCharTransitioning = false;

    // --- Race Start Logic ---
    $: if ($isStarting) {
        charOpacity.set(0);
        carY.set(-10);
    }

    // --- Car Logic ---
    $: if ($selectedCar !== currentCarIdx && !isCarTransitioning) {
        handleCarChange($selectedCar);
    }

    async function handleCarChange(newIdx: number) {
        isCarTransitioning = true;
        const direction = $selectionDirection; // -1 for Left (Next), 1 for Right (Prev)

        // Swiping Left (Next) -> Car drives BACK (+Z)
        // Swiping Right (Prev) -> Car drives AWAY (-Z)
        const exitZ = direction === -1 ? 15 : -15;
        const entryZ = direction === -1 ? -15 : 15;

        // 1. Drive current car out
        await carZ.set(exitZ);

        // 2. Switch models and teleport new car to opposite side
        prevCarIdx = currentCarIdx;
        currentCarIdx = newIdx;
        carZ.set(entryZ, { duration: 0 });

        // 3. Drive new car in
        await carZ.set(0);
        isCarTransitioning = false;
    }

    // --- Character Logic ---
    $: if ($selectedCharacter !== currentCharIdx && !isCharTransitioning) {
        handleCharChange($selectedCharacter);
    }

    async function handleCharChange(newIdx: number) {
        isCharTransitioning = true;
        // 1. Fade current out
        await charOpacity.set(0);

        // 2. Switch
        prevCharIdx = currentCharIdx;
        currentCharIdx = newIdx;

        // 3. Fade new in
        await charOpacity.set(1);
        isCharTransitioning = false;
    }

    // --- Assets ---
    $: carUrl = ASSETS.cars[currentCarIdx] || ASSETS.cars[0];
    $: charUrl = ASSETS.characters[currentCharIdx] || ASSETS.characters[0];
    $: prevCarUrl = ASSETS.cars[prevCarIdx] || ASSETS.cars[0];
    $: prevCharUrl = ASSETS.characters[prevCharIdx] || ASSETS.characters[0];

    $: carGltf = useGltf(carUrl);
    $: charGltf = useGltf(charUrl);
    $: prevCarGltf = useGltf(prevCarUrl);
    $: prevCharGltf = useGltf(prevCharUrl);

    // Helper to set opacity on a model
    function setModelOpacity(model: any, opacityValue: number) {
        if (!model) return;
        model.traverse((node: any) => {
            if (node.isMesh) {
                node.material.transparent = true;
                node.material.opacity = opacityValue;
                node.material.needsUpdate = true;
            }
        });
    }

    $: if ($charGltf) {
        setModelOpacity($charGltf.scene, $charOpacity);
    }

    // --- Camera ---
    const CAM_POS: [number, number, number] = [12, 8, 12];
    const CAM_LOOK: [number, number, number] = [0, 0, 0];

    import { OrbitControls } from "@threlte/extras";
</script>

<T.PerspectiveCamera
    makeDefault
    position={CAM_POS}
    on:create={({ ref }) => {
        ref.lookAt(...CAM_LOOK);
    }}
>
    <OrbitControls enableDamping />
</T.PerspectiveCamera>

<!-- Lighting -->
<T.DirectionalLight
    position={[5, 10, 5]}
    intensity={2}
    color="#ffffff"
    castShadow
/>
<T.DirectionalLight position={[-5, 5, -5]} intensity={1} color="#ffaa00" />
<T.AmbientLight intensity={0.5} color="#444444" />

<T.Fog args={["#1a1a1a", 10, 30]} />

<!-- Subjects -->
<T.Group position={[0, 0.1, 0]}>
    <!-- Car -->
    {#if $carGltf}
        {#if !$isStarting}
            <Float speed={2} rotationIntensity={0.05} floatIntensity={0.1}>
                <T.Group position.z={$carZ} position.y={$carY - 0.1}>
                    <T
                        is={$carGltf.scene}
                        scale={GAME_CONFIG.player.scale}
                        castShadow
                        receiveShadow
                    />
                </T.Group>
            </Float>
        {:else}
            <T.Group
                position.z={$carZ}
                position.y={$carY - 0.1}
                rotation.x={$carFallRotation}
            >
                <T
                    is={$carGltf.scene}
                    scale={GAME_CONFIG.player.scale}
                    castShadow
                    receiveShadow
                />
            </T.Group>
        {/if}
    {/if}

    <!-- Driver -->
    {#if $charGltf}
        <T
            is={$charGltf.scene}
            position={[2.5, 0, 0]}
            rotation={[0, Math.PI / 2, 0]}
            scale={1.9}
            castShadow
            receiveShadow
        />
    {/if}
</T.Group>

<!-- Floor Shadows -->
<ContactShadows
    opacity={0.6 * $charOpacity}
    scale={10}
    blur={2}
    far={2}
    resolution={512}
    color="#000000"
/>
