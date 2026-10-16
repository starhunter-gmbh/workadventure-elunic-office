<script lang="ts">
    // elunic patch: users who already own a desk get a small, unobtrusive prompt (top right) instead of the
    // big bottom popup; the "your current desk will be released" warning only appears after clicking claim.
    import { onMount } from "svelte";
    import { mapEditorAskToClaimPersonalAreaStore } from "../../Stores/MapEditorStore";
    import LL from "../../../i18n/i18n-svelte";
    import { gameManager } from "../../Phaser/Game/GameManager";
    import { localUserStore } from "../../Connection/LocalUserStore";
    import PopUpContainer from "../PopUp/PopUpContainer.svelte";
    import Input from "../Input/Input.svelte";

    let name = "";
    let hasOwnArea = false;
    let confirmRelease = false;
    const mapEditorModeManager = gameManager.getCurrentGameScene().getMapEditorModeManager();

    // function to check key press and if it is enter key then click on yes button
    function emitKeypressEvents(event: KeyboardEvent) {
        if (event.key === "Enter") {
            const claimPersonalAreaButton = document.querySelector("[data-testid=claimPersonalAreaButton]");
            claimPersonalAreaButton?.dispatchEvent(new MouseEvent("click"));
        }
    }

    function close() {
        mapEditorAskToClaimPersonalAreaStore.set(undefined);
    }

    function claim() {
        mapEditorModeManager.claimPersonalArea(name);
    }

    onMount(() => {
        // set name to current user name
        name = gameManager.getCurrentGameScene().CurrentPlayer.playerName;

        const userUUID = localUserStore.getLocalUser()?.uuid;
        if (userUUID === undefined) {
            console.error("Unable to claim the area, your UUID is undefined");
            return;
        }
        const gameMapFrontWrapper = gameManager.getCurrentGameScene().getGameMapFrontWrapper();
        hasOwnArea =
            gameMapFrontWrapper.areasManager
                ?.getAreasByPropertyType("personalAreaPropertyData")
                .some((area) =>
                    area.areaData.properties.some(
                        (property) => property.type === "personalAreaPropertyData" && property.ownerId === userUUID
                    )
                ) ?? false;
    });
</script>

{#if hasOwnArea}
    <div class="absolute top-20 right-4 w-72 pointer-events-auto z-[150] rounded-lg bg-contrast/80 backdrop-blur p-3 text-sm text-white">
        {#if confirmRelease}
            <p class="m-0 mb-2">Du hast schon einen Platz. Er wird frei, wenn du diesen übernimmst.</p>
            <div class="flex flex-row gap-2">
                <button type="button" class="btn btn-outline btn-sm w-full" on:click|preventDefault={close}
                    >{$LL.area.personalArea.buttons.no()}</button
                >
                <button
                    data-testid="claimPersonalAreaButton"
                    type="button"
                    class="btn btn-secondary btn-sm w-full"
                    on:click={claim}>{$LL.area.personalArea.buttons.yes()}</button
                >
            </div>
        {:else}
            <div class="flex flex-row items-center gap-2">
                <span class="grow">Diesen Platz übernehmen?</span>
                <button type="button" class="btn btn-secondary btn-sm" on:click={() => (confirmRelease = true)}
                    >Übernehmen</button
                >
                <button type="button" class="btn btn-outline btn-sm" aria-label="close" on:click|preventDefault={close}
                    >✕</button
                >
            </div>
        {/if}
    </div>
{:else}
    <div class="absolute w-fit bottom-0 left-0 right-0 pb-4 pointer-events-auto z-[150] m-auto hover:animate-none">
        <PopUpContainer extraClasses="w-fit">
            <p class="m-0 mt-2">{$LL.area.personalArea.claimDescription()}</p>
            <Input
                id="claimPersonalAreaInput"
                type="text"
                label="Your Name"
                bind:value={name}
                onKeyDown={emitKeypressEvents}
            />
            <div slot="buttons" class="flex flex-row justify-content-center w-full gap-2">
                <button type="button" class="btn btn-outline w-full hover:bg-contrast-600/50" on:click|preventDefault={close}
                    >{$LL.area.personalArea.buttons.no()}
                </button>
                <button data-testid="claimPersonalAreaButton" type="button" class="btn btn-secondary w-full" on:click={claim}
                    >{$LL.area.personalArea.buttons.yes()}
                </button>
            </div>
        </PopUpContainer>
    </div>
{/if}
