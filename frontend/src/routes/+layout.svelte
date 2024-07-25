<script lang="ts">
    import "../app.css";
    import { fade } from 'svelte/transition';
    
    // Define the type for data
    type Data = {
        currentPath: string;
    };

    // Declare data with the correct type
    export let data: Data;
</script>

{#key data.currentPath}
    <div class="content" in:fade={{ duration: 300, delay: 400 }} out:fade={{ duration: 300 }}>
        <slot />
    </div>
{/key}
