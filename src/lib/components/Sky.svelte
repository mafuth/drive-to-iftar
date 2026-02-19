<script lang="ts">
    import { T, useTask } from "@threlte/core";
    import { GAME_CONFIG } from "$lib/config";
    import { gameTime, fps } from "$lib/stores/game";
    import { derived } from "svelte/store";

    type SkyStage = "day" | "sunset" | "night";

    const skyState = derived(gameTime, ($time) => {
        let stage: SkyStage = "day";
        if ($time >= 17 && $time < 19) stage = "sunset";
        else if ($time >= 19 || $time < 7) stage = "night";

        return {
            stage,
            config: GAME_CONFIG.world.sky[stage],
            time: $time,
        };
    });

    // FPS Counter (Must be inside Canvas/Threlte context)
    let frameCount = 0;
    let lastFpsUpdate = 0;

    useTask((delta) => {
        if (!GAME_CONFIG.development.devMode) return;

        frameCount++;
        const now = performance.now();
        if (now - lastFpsUpdate > 500) {
            // Update every 0.5s
            const currentFps = Math.round(
                (frameCount * 1000) / (now - lastFpsUpdate),
            );
            fps.set(currentFps);
            frameCount = 0;
            lastFpsUpdate = now;
        }
    });
</script>

<!-- Sky Background Color -->
<T.Color attach="background" args={[$skyState.config.fog]} />

<!-- Fog Integration -->
<T.Fog
    args={[
        $skyState.config.fog,
        GAME_CONFIG.world.fog.near,
        GAME_CONFIG.world.fog.far,
    ]}
    attach="fog"
/>

<!-- Environmental Lighting -->
<T.AmbientLight
    intensity={$skyState.stage === "night" ? 0.3 : 1.0}
    color={$skyState.config.ambient}
/>

<T.DirectionalLight
    position={[-10, 20, 10]}
    intensity={$skyState.config.intensity}
    color={$skyState.config.directional}
    castShadow
/>
