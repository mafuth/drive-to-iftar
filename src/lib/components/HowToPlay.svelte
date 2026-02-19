<script lang="ts">
    import { createEventDispatcher, onMount } from "svelte";
    import { fade, scale } from "svelte/transition";

    export let show = false;
    export let isNewPlayer = false;

    const dispatch = createEventDispatcher();
    let dontShowAgain = false;

    function close() {
        if (dontShowAgain) {
            localStorage.setItem("tutorial_seen", "true");
        }
        dispatch("close");
    }

    onMount(() => {
        const seen = localStorage.getItem("tutorial_seen");
        if (seen) {
            dontShowAgain = true;
        }
    });
</script>

{#if show}
    <div
        class="fixed inset-0 z-[200] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
        transition:fade
        on:click|self={close}
    >
        <div
            class="w-full max-w-lg max-h-[95vh] overflow-y-auto bg-[#1a1a2e] border border-white/20 rounded-2xl p-6 md:p-8 flex flex-col gap-6 shadow-2xl relative"
            transition:scale={{ start: 0.95, duration: 200 }}
        >
            <button
                class="absolute top-4 right-4 text-white/50 hover:text-white hover:bg-white/10 w-10 h-10 rounded-full flex items-center justify-center transition-all bg-white/5"
                on:click={close}
                aria-label="Close"
                title="Close"
            >
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-5 w-5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                >
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2.5"
                        d="M6 18L18 6M6 6l12 12"
                    />
                </svg>
            </button>

            <h2
                class="text-3xl font-black italic text-white uppercase tracking-wider text-center"
            >
                How To Play
            </h2>

            <div class="flex flex-col gap-6">
                <!-- Controls -->
                <div class="bg-white/5 p-4 rounded-xl border border-white/10">
                    <h3
                        class="text-amber-400 font-bold uppercase tracking-wider mb-2 text-sm"
                    >
                        Controls
                    </h3>
                    <div class="grid grid-cols-2 gap-4">
                        <div class="flex flex-col items-center gap-2">
                            <span class="text-white/50 text-xs uppercase"
                                >Mobile</span
                            >
                            <div
                                class="flex items-center gap-2 text-white font-mono text-sm"
                            >
                                <span>👈 Swipe 👉</span>
                            </div>
                            <span class="text-white text-sm">Change Lanes</span>

                            <div
                                class="flex items-center gap-2 text-white font-mono text-sm mt-2"
                            >
                                <span>👇 Swipe Down</span>
                            </div>
                            <span class="text-orange-400 text-sm font-bold"
                                >Nitro Boost</span
                            >
                        </div>
                        <div class="flex flex-col items-center gap-2">
                            <span class="text-white/50 text-xs uppercase"
                                >Desktop</span
                            >
                            <div
                                class="flex items-center gap-2 text-white font-mono text-sm"
                            >
                                <span
                                    class="border border-white/20 px-2 py-1 rounded"
                                    >←</span
                                >
                                <span>or</span>
                                <span
                                    class="border border-white/20 px-2 py-1 rounded"
                                    >→</span
                                >
                            </div>
                            <span class="text-white text-sm">Arrow Keys</span>

                            <div
                                class="flex items-center gap-2 text-white font-mono text-sm mt-2"
                            >
                                <span
                                    class="border border-white/20 px-2 py-1 rounded"
                                    >↓</span
                                >
                            </div>
                            <span class="text-orange-400 text-sm font-bold"
                                >Nitro Boost</span
                            >
                        </div>
                    </div>
                </div>

                <!-- Goal -->
                <div class="bg-white/5 p-4 rounded-xl border border-white/10">
                    <h3
                        class="text-amber-400 font-bold uppercase tracking-wider mb-2 text-sm"
                    >
                        Objective
                    </h3>
                    <ul
                        class="text-white/80 text-sm space-y-2 list-disc list-inside"
                    >
                        <li>Dodging traffic and obstacles is key!</li>
                        <li>
                            Collect <span class="text-green-400 font-bold"
                                >Watermelons 🍉</span
                            > for points & boost.
                        </li>
                        <li>
                            Fill the bar to unlock <span
                                class="text-orange-400 font-bold"
                                >Nitro Boost 🥤</span
                            >.
                        </li>
                    </ul>
                </div>

                <!-- Multiplayer -->
                <div
                    class="bg-amber-500/10 p-4 rounded-xl border border-amber-500/20"
                >
                    <h3
                        class="text-amber-400 font-bold uppercase tracking-wider mb-2 text-sm flex items-center gap-2"
                    >
                        <span>Multiplayer Mode</span>
                        <span
                            class="text-[10px] bg-amber-500 text-black px-1.5 py-0.5 rounded-full font-black"
                            >NEW</span
                        >
                    </h3>
                    <ul class="text-white/90 text-sm space-y-2">
                        <li class="flex items-start gap-2">
                            <span class="text-amber-400 mt-1">•</span>
                            <span
                                ><strong>Shared Car:</strong> Everyone controls the
                                same vehicle!</span
                            >
                        </li>
                        <li class="flex items-start gap-2">
                            <span class="text-amber-400 mt-1">•</span>
                            <span
                                ><strong>Assigned Lanes:</strong> You are assigned
                                a unique lane (see HUD).</span
                            >
                        </li>
                        <li class="flex items-start gap-2">
                            <span class="text-amber-400 mt-1">•</span>
                            <span
                                ><strong>Locked Control:</strong> You can only
                                move the car into <em>your</em> assigned lane.</span
                            >
                        </li>
                        <li class="flex items-start gap-2">
                            <span class="text-amber-400 mt-1">•</span>
                            <span
                                ><strong>Host Retry:</strong> Only the session host
                                can restart the race after a crash.</span
                            >
                        </li>
                    </ul>
                </div>

                <!-- Footer / Action -->
                <div class="flex flex-col items-center gap-4 mt-2">
                    <label
                        class="flex items-center gap-3 text-white/70 text-sm cursor-pointer select-none group"
                    >
                        <div
                            class="relative w-5 h-5 flex items-center justify-center rounded border border-white/30 bg-white/5 group-hover:border-amber-400 transition-colors"
                        >
                            <input
                                type="checkbox"
                                bind:checked={dontShowAgain}
                                class="peer appearance-none absolute inset-0 w-full h-full cursor-pointer opacity-0"
                            />
                            <svg
                                class="w-3 h-3 text-amber-400 opacity-0 peer-checked:opacity-100 transition-opacity"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                                stroke-width="4"
                            >
                                <path
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    d="M5 13l4 4L19 7"
                                />
                            </svg>
                        </div>
                        <span class="group-hover:text-white transition-colors"
                            >Don't show this again</span
                        >
                    </label>

                    <button
                        on:click={close}
                        class="w-full py-3 bg-white text-black font-bold uppercase tracking-wider rounded-xl hover:bg-gray-200 transition-all shadow-lg"
                    >
                        {isNewPlayer ? "Let's Race!" : "Got it!"}
                    </button>
                </div>
            </div>
        </div>
    </div>
{/if}
