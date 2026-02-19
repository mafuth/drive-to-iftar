<script lang="ts">
    import { onMount } from "svelte";
    import { api } from "$lib/api";
    import { currentUser } from "$lib/stores/game";
    import { goto } from "$app/navigation";
    import { loadGameConfig } from "$lib/config";
    import { Logger } from "$lib/utils/logger";

    const log = new Logger("AuthGuard");

    let { children } = $props();
    let loading = $state(true);

    onMount(async () => {
        await loadGameConfig();

        if (!$currentUser) {
            // Check existing session
            try {
                const user = await api.auth.getMe();
                currentUser.set(user);
            } catch (e) {
                log.log("Not logged in, redirecting to home");
                currentUser.set(null);
                goto("/");
                return;
            }
        }

        loading = false;
    });
</script>

{#if loading}
    <div
        class="fixed inset-0 bg-slate-900 flex items-center justify-center z-[100]"
    >
        <div class="flex flex-col items-center gap-4">
            <div
                class="w-12 h-12 border-4 border-amber-400 border-t-transparent rounded-full animate-spin"
            ></div>
            <p
                class="text-white font-black italic uppercase tracking-widest text-sm"
            >
                Loading...
            </p>
        </div>
    </div>
{:else}
    {@render children()}
{/if}
