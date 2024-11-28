FROM node:21-alpine AS builder

WORKDIR /frontend
COPY package.json .
COPY package-lock.json .
RUN npm ci
COPY . .
RUN npm run build

FROM node:21-alpine AS production

WORKDIR /frontend
COPY --from=builder /frontend/build ./build
COPY --from=builder /frontend/node_modules ./node_modules
COPY package.json .
CMD ["node", "./build"]