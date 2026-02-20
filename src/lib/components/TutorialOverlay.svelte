<script lang="ts">
    import { onMount } from "svelte";
    import { fade, fly, scale } from "svelte/transition";
    import {
        isTutorial,
        tutorialStep,
        watermelons,
        nitroActive,
        dailyChallenge,
        isPlaying,
    } from "$lib/stores/game";
    import { GAME_CONFIG } from "$lib/config";

    let visible = false;

    $: if ($isTutorial && $isPlaying) {
        visible = true;
    } else {
        visible = false;
        tutorialStep.set(0);
    }

    const steps = [
        {
            title: "Welcome!",
            text: "Use A/D, LEFT/RIGHT arrows, or SWIPE side to side to switch lanes. Survive as long as possible!",
            action: "Got it!",
        },
        {
            title: "Customize Your Ride",
            text: "Before racing, you can change your CHARACTER and VEHICLE in the Start Menu by clicking the arrows or swiping!",
            action: "Cool, let's go!",
        },
        {
            title: "Fuel Up with Watermelons",
            text: "Collect Watermelons to fill your Karaa drink meter. Collect 5 to unlock a boost!",
            action: "I'll find some!",
        },
        {
            title: "Karaa Boost!",
            text: "Your meter is full! Press SPACE, DOWN ARROW or SWIPE DOWN to blast through anything!",
            action: "ACTIVATE KARAA",
        },
        {
            title: "Daily Dates Challenge",
            text: "Every day, collect Dates to reach your Daily Target. Only those who 'break their fast' show up on top rankings!",
            action: "Tell me about Multiplayer",
        },
        {
            title: "Multiplayer Madness!",
            text: "Share a car with others! You're assigned a LANE NUMBER (1 on far left), you can ONLY move into your lane. Plus, it's cross-play, race with anyone on any device with a browser!",
            action: "Ready to Race!",
        },
        {
            title: "You're Ready!",
            text: "Tutorial complete. Obstacles will now appear and points will start counting. Good luck!",
            action: "START RUN",
        },
    ];

    function next() {
        if ($tutorialStep === 2) {
            // Give free watermelons for boost demo
            watermelons.set(GAME_CONFIG.player.nitro.watermelonThreshold);
        }

        if ($tutorialStep < steps.length - 1) {
            tutorialStep.update((n) => n + 1);
        } else {
            finish();
        }
    }

    function prev() {
        if ($tutorialStep > 0) {
            tutorialStep.update((n) => n - 1);
        }
    }

    function finish() {
        isTutorial.set(false);
        tutorialStep.set(0);
        visible = false;
    }

    let lastStep = 0;
    let watermelonsAtStepStart = 0;
    let nitroActiveAtStepStart = false;

    $: if ($tutorialStep !== lastStep) {
        watermelonsAtStepStart = $watermelons;
        nitroActiveAtStepStart = $nitroActive;
        lastStep = $tutorialStep;
    }

    // Auto-advance logic
    $: if ($isTutorial && $tutorialStep === 2) {
        // Advance if they collect watermelons while on this step
        if ($watermelons > watermelonsAtStepStart && $watermelons >= 5) {
            tutorialStep.set(3);
        }
    }
    $: if ($isTutorial && $tutorialStep === 3) {
        // Advance if they activate nitro while on this step
        if ($nitroActive && !nitroActiveAtStepStart) {
            tutorialStep.set(4);
        }
    }
</script>

{#if visible}
    <div
        class="fixed inset-0 z-[300] pointer-events-none flex items-center justify-center p-6"
        transition:fade
    >
        <!-- Dark Overlay for focus -->
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>

        <div
            class="relative w-full max-w-[85%] md:max-w-md bg-zinc-900/95 border border-white/10 rounded-[1.5rem] md:rounded-[2rem] p-4 md:p-8 shadow-2xl pointer-events-auto flex flex-col items-center text-center gap-3 md:gap-6"
            transition:fly={{ y: 40, duration: 600 }}
        >
            <!-- Step Indicator -->
            <div class="flex gap-1 md:gap-2 mb-0.5 md:mb-2">
                {#each steps as _, i}
                    <div
                        class="h-1 w-4 md:w-8 rounded-full transition-colors duration-500 {i <=
                        $tutorialStep
                            ? 'bg-amber-400'
                            : 'bg-white/10'}"
                    ></div>
                {/each}
            </div>

            <div class="space-y-1.5 md:space-y-3">
                <h2
                    class="text-lg md:text-3xl font-black text-white uppercase italic tracking-tighter"
                >
                    {steps[$tutorialStep].title}
                </h2>
                <p
                    class="text-xs md:text-lg text-white/70 leading-relaxed font-medium px-1 md:px-2"
                >
                    {steps[$tutorialStep].text}
                </p>
            </div>

            {#if $tutorialStep === 1}
                <div
                    class="flex items-center gap-2 md:gap-4 py-1 md:py-4"
                    in:scale
                >
                    <div
                        class="w-10 h-10 md:w-16 md:h-16 bg-amber-500/20 rounded-xl md:rounded-2xl flex items-center justify-center border border-amber-500/30 text-amber-500"
                    >
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            class="h-6 w-6 md:h-10 md:w-10"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                        >
                            <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                            />
                        </svg>
                    </div>
                    <div class="text-left">
                        <div
                            class="text-[8px] md:text-xs text-amber-500 font-bold uppercase tracking-wider"
                        >
                            Start Menu
                        </div>
                        <div
                            class="text-base md:text-xl font-black text-white italic"
                        >
                            Select Driver & Car
                        </div>
                    </div>
                </div>
            {:else if $tutorialStep === 2}
                <!-- Visual cue for watermelons -->
                <div
                    class="flex items-center gap-2 md:gap-4 py-1 md:py-4"
                    in:scale
                >
                    <img
                        src="/kenney_food-kit/Previews/watermelon.png"
                        alt="Watermelon"
                        class="w-10 h-10 md:w-16 md:h-16 animate-bounce"
                    />
                    <div class="text-left">
                        <div
                            class="text-[8px] md:text-xs text-green-400 font-bold uppercase tracking-wider"
                        >
                            Target
                        </div>
                        <div class="text-lg md:text-2xl font-black text-white">
                            5 Watermelons
                        </div>
                    </div>
                </div>
            {:else if $tutorialStep === 3}
                <div
                    class="flex items-center gap-2 md:gap-4 py-1 md:py-4"
                    in:scale
                >
                    <div
                        class="w-10 h-10 md:w-16 md:h-16 bg-blue-500 rounded-xl md:rounded-2xl flex items-center justify-center shadow-[0_0_20px_rgba(59,130,246,0.5)] animate-pulse"
                    >
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            class="h-6 w-6 md:h-10 md:w-10 text-white"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                        >
                            <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="3"
                                d="M13 10V3L4 14h7v7l9-11h-7z"
                            />
                        </svg>
                    </div>
                    <div
                        class="text-left text-blue-400 font-bold uppercase tracking-wider text-xs md:text-base"
                    >
                        Take a Karaa Boost
                    </div>
                </div>
            {:else if $tutorialStep === 4}
                <div
                    class="flex items-center gap-2 md:gap-4 py-1 md:py-4"
                    in:scale
                >
                    <img
                        src="/kenney_food-kit/Previews/coconut.png"
                        alt="Date"
                        class="w-10 h-10 md:w-16 md:h-16"
                    />
                    <div class="text-left">
                        <div
                            class="text-[8px] md:text-xs text-amber-500 font-bold uppercase tracking-wider"
                        >
                            Daily Goal
                        </div>
                        <div class="text-lg md:text-2xl font-black text-white">
                            Collect Dates
                        </div>
                    </div>
                </div>
            {:else if $tutorialStep === 5}
                <div
                    class="flex items-center gap-2 md:gap-4 py-1 md:py-4"
                    in:scale
                >
                    <div
                        class="w-10 h-10 md:w-16 md:h-16 bg-purple-500/20 rounded-xl md:rounded-2xl flex items-center justify-center border border-purple-500/30 text-purple-400"
                    >
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            class="h-6 w-6 md:h-10 md:w-10"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                        >
                            <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
                            />
                        </svg>
                    </div>
                    <div class="text-left">
                        <div
                            class="text-[8px] md:text-xs text-purple-400 font-bold uppercase tracking-wider"
                        >
                            Multiplayer
                        </div>
                        <div
                            class="text-base md:text-xl font-black text-white italic"
                        >
                            Assigned Lanes
                        </div>
                    </div>
                </div>
            {/if}
            <div class="flex w-full gap-2 md:gap-3 mt-1 md:mt-2">
                {#if $tutorialStep > 0}
                    <button
                        on:click={prev}
                        class="flex-1 py-3 md:py-5 bg-white/5 hover:bg-white/10 text-white font-bold uppercase tracking-wider rounded-xl md:rounded-2xl border border-white/10 transition-all active:scale-95 text-[10px] md:text-sm"
                    >
                        Back
                    </button>
                {/if}
                <button
                    on:click={next}
                    class="{$tutorialStep > 0
                        ? 'flex-[2]'
                        : 'w-full'} py-3 md:py-5 bg-amber-400 hover:bg-amber-300 text-black font-black uppercase tracking-widest rounded-xl md:rounded-2xl transition-all shadow-[0_10px_20px_rgba(251,191,36,0.3)] active:scale-95 text-xs md:text-base px-2"
                >
                    {steps[$tutorialStep].action}
                </button>
            </div>
        </div>
    </div>
{/if}

<style>
    /* Prevent interaction with game while tutorial is showing if needed */
    /* .pointer-events-auto { pointer-events: auto; } */
</style>
