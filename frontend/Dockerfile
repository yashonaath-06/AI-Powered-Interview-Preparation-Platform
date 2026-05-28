# ============================================================
#  Frontend Dockerfile  (development mode for Phase 2)
#  In Phase 15 we'll switch to a multi-stage production build.
# ============================================================
FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

EXPOSE 3000
CMD ["npm", "run", "dev"]
