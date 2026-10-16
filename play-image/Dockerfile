# elunic WorkAdventure play image: play-eleiva (v1.27.10 + calendar status extension) + elunic patches.
# The base image ships without dev dependencies, so they are installed for the front build and pruned again.
FROM crstarhunter.azurecr.io/workadventure:play-eleiva
USER root
WORKDIR /usr/src
RUN npm ci --include=dev --ignore-scripts
COPY src/ /usr/src/play/src/
RUN cd play && GENERATE_SOURCEMAP=false NODE_OPTIONS=--max-old-space-size=8192 npm run build \
 && cd /usr/src && npm prune --omit=dev --ignore-scripts \
 && chown -R node:node /usr/src/play /usr/src/node_modules
WORKDIR /usr/src/play
USER node
