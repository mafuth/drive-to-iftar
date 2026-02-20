<script lang="ts">
    import { onMount } from "svelte";
    import { fade, fly, scale } from "svelte/transition";
    import { ALL_ASSETS } from "$lib/utils/assets";

    let loadedCount = 0;
    let totalCount = ALL_ASSETS.length;
    let isFinished = false;
    let visible = true;

    $: progress = Math.round((loadedCount / totalCount) * 100);

    onMount(async () => {
        const preloadAsset = async (url: string) => {
            try {
                if (
                    url.endsWith(".png") ||
                    url.endsWith(".jpg") ||
                    url.endsWith(".svg")
                ) {
                    const img = new Image();
                    img.src = url;
                    // @ts-ignore
                    if (img.decode) {
                        await img.decode().catch(() => {});
                    }
                } else {
                    // GLB/GLTF - simple fetch to put in cache
                    // @ts-ignore
                    await fetch(url, {
                        mode: "no-cors",
                        // @ts-ignore
                        priority: "low",
                    }).catch(() => {});
                }
            } finally {
                loadedCount++;
            }
        };

        // Batch preloading to avoid overwhelming the network
        const BATCH_SIZE = 5;
        for (let i = 0; i < ALL_ASSETS.length; i += BATCH_SIZE) {
            const batch = ALL_ASSETS.slice(i, i + BATCH_SIZE);
            await Promise.all(batch.map(preloadAsset));
        }

        setTimeout(() => {
            isFinished = true;
            setTimeout(() => {
                visible = false;
            }, 3000);
        }, 800);
    });
</script>

{#if visible}
    <div
        class="fixed top-4 left-1/2 -translate-x-1/2 md:top-auto md:bottom-6 md:right-6 md:left-auto md:translate-x-0 z-[200] pointer-events-none"
        transition:fly={{ y: 20, duration: 500 }}
    >
        <div
            class="bg-black/80 backdrop-blur-xl border border-white/10 rounded-2xl p-4 shadow-2xl flex items-center gap-4 min-w-[240px]"
        >
            {#if !isFinished}
                <div
                    class="relative w-12 h-12 flex items-center justify-center"
                >
                    <svg class="w-full h-full transform -rotate-90">
                        <circle
                            cx="24"
                            cy="24"
                            r="20"
                            stroke="currentColor"
                            stroke-width="4"
                            fill="transparent"
                            class="text-white/10"
                        />
                        <circle
                            cx="24"
                            cy="24"
                            r="20"
                            stroke="currentColor"
                            stroke-width="4"
                            fill="transparent"
                            stroke-dasharray="125.66"
                            stroke-dashoffset={125.66 -
                                (125.66 * progress) / 100}
                            class="text-amber-400 transition-all duration-300"
                        />
                    </svg>
                    <span class="absolute text-[10px] font-bold text-white"
                        >{progress}%</span
                    >
                </div>
                <div class="flex flex-col">
                    <span
                        class="text-xs font-bold text-white uppercase tracking-widest"
                        >Preloading Assets</span
                    >
                    <span class="text-[10px] text-white/50 tracking-wider"
                        >Optimizing experience...</span
                    >
                </div>
            {:else}
                <div
                    class="w-10 h-10 bg-green-500/20 rounded-full flex items-center justify-center text-green-400"
                    transition:scale
                >
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        class="h-6 w-6"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                    >
                        <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="3"
                            d="M5 13l4 4L19 7"
                        />
                    </svg>
                </div>
                <div class="flex flex-col" transition:fade>
                    <span
                        class="text-xs font-bold text-white uppercase tracking-widest"
                        >Game Ready</span
                    >
                    <span class="text-[10px] text-green-400/70 tracking-wider"
                        >All assets pre-loaded!</span
                    >
                </div>
            {/if}
        </div>
    </div>
{/if}
