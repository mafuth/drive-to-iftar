<script lang="ts">
	import "./layout.css";
	import favicon from "$lib/assets/favicon.svg";

	let { children } = $props();
	import MultiplayerManager from "$lib/components/MultiplayerManager.svelte";
	import DevConsole from "$lib/components/DevConsole.svelte";
	import AssetPreloader from "$lib/components/AssetPreloader.svelte";
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>
<AssetPreloader />
<MultiplayerManager />
<DevConsole />
{@render children()}
