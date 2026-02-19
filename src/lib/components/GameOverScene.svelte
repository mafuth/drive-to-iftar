<script lang="ts">
    import { T, useTask } from "@threlte/core";
    import { useGltf } from "@threlte/extras";
    import { ASSETS } from "$lib/utils/assets";
    import {
        selectedCharacter,
        selectedCar,
        isGameOver,
        isPlaying,
        score,
    } from "$lib/stores/game";
    import { GAME_CONFIG } from "$lib/config";

    // Load Assets
    // We need to reactively load the selected models.
    $: charUrl = ASSETS.characters[$selectedCharacter];
    $: carUrl = ASSETS.cars[$selectedCar];

    $: charGltf = useGltf(charUrl);
    $: carGltf = useGltf(carUrl);

    // Debris assets
    // Load a few random debris items
    const debrisTire = useGltf(ASSETS.debris[0]);
    const debrisBumper = useGltf(ASSETS.debris[1]);
    const debrisCone = useGltf(ASSETS.debris[2]);
    const debrisWatermelon = useGltf(ASSETS.collectibles.watermelon);

    function restart() {
        isGameOver.set(false);
        isPlaying.set(false); // Go back to start menu
        score.set(0);
    }

    import { OrbitControls, ContactShadows, Float } from "@threlte/extras";

    // --- Camera ---
    // "Zoomed Out" view but looking LOWER so the car appears HIGHER in the viewport.
    const CAM_POS: [number, number, number] = [12, 8, 12];
    const CAM_LOOK: [number, number, number] = [0, -2, 0];
</script>

<!-- Only render if Game Over -->
{#if $isGameOver}
    <T.PerspectiveCamera
        makeDefault
        position={CAM_POS}
        on:create={({ ref }) => {
            ref.lookAt(...CAM_LOOK);
        }}
    >
        <OrbitControls enableDamping target={CAM_LOOK} />
    </T.PerspectiveCamera>

    <!-- --- Lighting (Same as StartScene) --- -->
    <T.DirectionalLight
        position={[5, 10, 5]}
        intensity={2}
        color="#ffffff"
        castShadow
    />
    <T.DirectionalLight position={[-5, 5, -5]} intensity={1} color="#ffaa00" />
    <T.AmbientLight intensity={0.5} color="#444444" />

    <!-- --- Environment --- -->
    <T.Fog args={["#1a1a1a", 10, 30]} />

    <!-- --- Scene Content (Lifted UP to show text below) --- -->
    <T.Group position={[0, 1.5, 0]}>
        <!-- Crashed Car (Rotated to look broken) -->
        {#if $carGltf}
            <T
                is={$carGltf.scene.clone()}
                position={[0, 0, 0]}
                rotation={[Math.PI / 8, Math.PI + Math.PI / 4, Math.PI / 12]}
                scale={GAME_CONFIG.player.scale}
                castShadow
                receiveShadow
            />
        {/if}

        <!-- Character Removed -->
        <!-- {#if $charGltf}
            <T
                is={$charGltf.scene.clone()}
                position={[2.5, 0.2, 1.5]}
                rotation={[-Math.PI / 2, 0, Math.PI / 4]}
                scale={GAME_CONFIG.menus.gameover.character.scale}
                castShadow
                receiveShadow
            />
        {/if} -->

        <!-- Debris scattered around -->
        <!-- Tire -->
        {#if $debrisTire}
            <T
                is={$debrisTire.scene.clone()}
                position={[-2, 0.2, 2]}
                rotation={[Math.PI / 2, 0, 0]}
                scale={1.5}
                castShadow
                receiveShadow
            />
            <T
                is={$debrisTire.scene.clone()}
                position={[1, 0.2, -2]}
                rotation={[Math.PI / 2, Math.PI, 0]}
                scale={1.5}
                castShadow
                receiveShadow
            />
        {/if}

        <!-- Bumper -->
        {#if $debrisBumper}
            <T
                is={$debrisBumper.scene.clone()}
                position={[2.5, 0.2, 0]}
                rotation={[0, Math.PI / 4, 0]}
                scale={1.5}
                castShadow
                receiveShadow
            />
        {/if}

        <!-- Cones -->
        {#if $debrisCone}
            <T
                is={$debrisCone.scene.clone()}
                position={[-3, 0.2, -1]}
                scale={2}
                castShadow
                receiveShadow
            />
            <T
                is={$debrisCone.scene.clone()}
                position={[3, 0.2, 3]}
                rotation={[Math.PI / 2, 0.5, 0]}
                scale={2}
                castShadow
                receiveShadow
            />
        {/if}

        <!-- Scattered Watermelons -->
        {#if $debrisWatermelon}
            <T
                is={$debrisWatermelon.scene.clone()}
                position={[-1, 0.2, 3]}
                rotation={[Math.PI / 2, Math.PI / 4, 0]}
                scale={1.5}
                castShadow
                receiveShadow
            />
            <T
                is={$debrisWatermelon.scene.clone()}
                position={[4, 0.2, -2]}
                rotation={[Math.PI / 3, Math.PI, Math.PI / 2]}
                scale={1.5}
                castShadow
                receiveShadow
            />
            <T
                is={$debrisWatermelon.scene.clone()}
                position={[-4, 0.2, 1]}
                rotation={[0, Math.PI / 6, 0]}
                scale={1.5}
                castShadow
                receiveShadow
            />
        {/if}
    </T.Group>

    <!-- Floor Shadows -->
    <ContactShadows
        opacity={0.6}
        scale={10}
        blur={2}
        far={2}
        resolution={512}
        color="#000000"
    />
{/if}
