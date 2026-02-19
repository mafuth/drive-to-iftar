<script lang="ts">
	import "./layout.css";
	import favicon from "$lib/assets/favicon.svg";

	let { children } = $props();
	import MultiplayerManager from "$lib/components/MultiplayerManager.svelte";
	import DevConsole from "$lib/components/DevConsole.svelte";
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>
<MultiplayerManager />
<DevConsole />
{@render children()}
