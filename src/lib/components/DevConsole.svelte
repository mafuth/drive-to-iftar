<script lang="ts">
    import { onMount, onDestroy } from "svelte";
    import { GAME_CONFIG } from "$lib/config";
    import { slide } from "svelte/transition";

    type LogEntry = {
        type: "log" | "warn" | "error" | "info";
        message: string;
        timestamp: number;
        count: number;
    };

    let logs: LogEntry[] = [];
    let isOpen = false;
    let container: HTMLDivElement | null = null;

    const originalLog = console.log;
    const originalWarn = console.warn;
    const originalError = console.error;
    const originalInfo = console.info;

    function formatMessage(args: any[]): string {
        return args
            .map((arg) => {
                if (typeof arg === "object") {
                    try {
                        return JSON.stringify(arg, null, 2);
                    } catch (e) {
                        return "[Circular]";
                    }
                }
                return String(arg);
            })
            .join(" ");
    }

    function addLog(type: LogEntry["type"], ...args: any[]) {
        if (!GAME_CONFIG.development.devMode) return;

        const message = formatMessage(args);
        const lastLog = logs[logs.length - 1];

        if (lastLog && lastLog.message === message && lastLog.type === type) {
            lastLog.count++;
            logs = [...logs];
        } else {
            logs = [
                ...logs,
                { type, message, timestamp: Date.now(), count: 1 },
            ].slice(-100);
        }

        if (container) {
            setTimeout(() => {
                if (container) container.scrollTop = container.scrollHeight;
            }, 10);
        }
    }

    onMount(() => {
        console.log = (...args) => {
            originalLog(...args);
            addLog("log", ...args);
        };
        console.warn = (...args) => {
            originalWarn(...args);
            addLog("warn", ...args);
        };
        console.error = (...args) => {
            originalError(...args);
            addLog("error", ...args);
        };
        console.info = (...args) => {
            originalInfo(...args);
            addLog("info", ...args);
        };
    });

    onDestroy(() => {
        console.log = originalLog;
        console.warn = originalWarn;
        console.error = originalError;
        console.info = originalInfo;
    });

    function clearLogs() {
        logs = [];
    }

    function formatTime(ts: number) {
        return new Date(ts).toLocaleTimeString([], {
            hour12: false,
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
        });
    }

    function getLogClass(type: string) {
        const base = "flex gap-2 border-b border-white/5 pb-1";
        if (type === "warn") return `${base} text-yellow-400`;
        if (type === "error") return `${base} text-red-400`;
        if (type === "info") return `${base} text-blue-400`;
        return `${base} text-white/80`;
    }
</script>

{#if GAME_CONFIG.development.devMode}
    <div
        class="fixed bottom-0 left-0 right-0 z-[9999] pointer-events-none font-mono"
    >
        <button
            on:click={() => (isOpen = !isOpen)}
            class="pointer-events-auto absolute bottom-4 right-4 bg-black/80 text-white p-2 rounded-lg border border-white/20 text-[10px] font-bold uppercase shadow-2xl transition-all hover:bg-white hover:text-black"
        >
            {isOpen ? "Close Console" : "Open Console"}
            {#if !isOpen && logs.length > 0}
                <span class="ml-1 px-1 bg-red-600 rounded-full"
                    >{logs.length}</span
                >
            {/if}
        </button>

        {#if isOpen}
            <div
                transition:slide={{ axis: "y" }}
                class="pointer-events-auto w-full h-64 bg-black/95 backdrop-blur-xl border-t border-white/10 flex flex-col shadow-2xl"
            >
                <div
                    class="flex justify-between items-center px-4 py-2 border-b border-white/5 bg-white/5"
                >
                    <span class="text-[10px] text-white/40 uppercase font-black"
                        >Console</span
                    >
                    <button
                        on:click={clearLogs}
                        class="text-[10px] text-red-500 hover:underline uppercase font-bold"
                        >Clear</button
                    >
                </div>

                <div
                    bind:this={container}
                    class="flex-1 overflow-y-auto p-2 text-[10px] flex flex-col gap-1"
                >
                    {#each logs as log}
                        {@const parts = log.message.match(/^\[(.*?)\]\s*(.*)/)}
                        <div class={getLogClass(log.type)}>
                            <span class="opacity-30 shrink-0"
                                >[{formatTime(log.timestamp)}]</span
                            >
                            {#if parts}
                                <span
                                    class="bg-white/10 px-1 rounded-sm text-amber-500 font-black shrink-0"
                                >
                                    {parts[1]}
                                </span>
                                <span class="break-all whitespace-pre-wrap"
                                    >{parts[2]}</span
                                >
                            {:else}
                                <span class="break-all whitespace-pre-wrap"
                                    >{log.message}</span
                                >
                            {/if}
                            {#if log.count > 1}
                                <span
                                    class="bg-white/10 px-1 rounded text-[8px]"
                                    >{log.count}</span
                                >
                            {/if}
                        </div>
                    {/each}
                </div>
            </div>
        {/if}
    </div>
{/if}

<style>
    div::-webkit-scrollbar {
        display: none;
    }
    div {
        -ms-overflow-style: none;
        scrollbar-width: none;
    }
</style>
