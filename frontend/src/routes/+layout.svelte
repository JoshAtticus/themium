<script lang="ts">
    import { LogOut } from 'lucide-svelte';
    import { createEventDispatcher } from 'svelte';

    const dispatcher = createEventDispatcher();

    let themeStyle = '';
    let isCreatingTheme = false;
    let themeResponse = '';
    let errorMessage = '';

    async function createTheme() {
        isCreatingTheme = true;
        errorMessage = '';
        dispatcher('update');

        try {
            const response = await fetch('https://themiumapi.joshatticus.online/generate-theme', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    style: themeStyle
                })
            });

            const responseData = await response.text();
            console.log(responseData); // Log the response data to check for any issues

            try {
                const data = JSON.parse(responseData);
                themeResponse = JSON.stringify(data).replace(/\s+/g, ' ');
            } catch (error) {
                console.error(error);
                errorMessage = "Oops! Something happened with our API, try recreating your requested theme";
            }
        } catch (error) {
            console.error(error);
            errorMessage = "Oops! Something went wrong, please try again later";
        }

        isCreatingTheme = false;
        dispatcher('update');
    }
</script>

<div class="topnav">
    <div class="topnav-inner">
        <a class="left" style="cursor: pointer;" href="/">
            Themium
        </a>
    </div>
</div>

<div style="text-align: center;">
    <br>
    <h1 style="font-size: 72px;">Themium</h1>
    <br>
    <input type="text" placeholder="What do you want to create?" bind:value={themeStyle}>
    <button class="create-button" on:click={createTheme}>Create</button>
    <br>
    {#if isCreatingTheme}
        <p class="creating-text">Creating that theme...</p>
    {/if}
    {#if errorMessage}
        <p class="error-message">{errorMessage}</p>
    {/if}
    {#if themeResponse}
        <div class="response-container">
            <div class="code-block-container">
                <code class="code-block">{themeResponse}</code>
                <button class="create-button copy-button" onclick="navigator.clipboard.writeText('{themeResponse}')">Copy</button>
            </div>
        </div>
    {/if}
</div>
