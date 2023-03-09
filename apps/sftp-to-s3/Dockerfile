#-- Builder image
FROM node:16-alpine AS builder
ARG NPM_CONFIG_REGISTRY
ARG NPM_CONFIG__AUTH
ENV NPM_CONFIG_ALWAYS_AUTH=true
WORKDIR /build
COPY package.json package-lock.json /build/
RUN npm install

#-- Deployment image
FROM node:16-alpine as deployment
WORKDIR /app
COPY index.js /app/
COPY --from=builder /build/node_modules /app/node_modules
ENTRYPOINT ["node", "index.js"]
