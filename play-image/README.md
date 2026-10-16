# play image `crstarhunter.azurecr.io/workadventure:play-elunic-1`

Base: `crstarhunter.azurecr.io/workadventure:play-eleiva` (WorkAdventure v1.27.10 + calendar status extension).

Patches (files under `src/` overwrite the base image sources, front is rebuilt):
- `src/front/Components/MapEditor/ClaimPersonalAreaDialogBox.svelte`: users who already own a desk get a small prompt
  (top right) instead of the bottom popup; the "current desk will be released" warning only shows after clicking.
- `src/pusher/app.ts`: `trust proxy = loopback, uniquelocal`, so `req.secure` is true behind Traefik and the OIDC /
  playUri cookies get the `Secure` flag.

Build (needs ~8 GB heap, sourcemaps off; the ACR build agent runs out of memory):

    docker build -t crstarhunter.azurecr.io/workadventure:play-elunic-1 play-image
    docker push crstarhunter.azurecr.io/workadventure:play-elunic-1

Pushed digest: `sha256:f509e8d5cd0d139e9cc0f30adf28d62d94fe19535ee901071106e33d542ee28a`
