# Use the official Bun image for development
FROM oven/bun:1

WORKDIR /app

# Copy package files first for caching bun install
COPY package.json bun.lock* ./

# Install all dependencies (dev + prod)
RUN bun install --frozen-lockfile

# Copy all source files
COPY . .

# Expose default Vite port (adjust if you use a different one)
EXPOSE 5173

# Run Vite dev server, similar to your npm run dev
CMD ["bun", "run", "dev"]
