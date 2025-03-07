# Use an official Node.js runtime as a parent image
FROM node:16-slim AS build

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json for efficient dependency installation
COPY package*.json ./

# Install dependencies (only production dependencies)
RUN npm install --production

# Copy the rest of the application code
COPY . .

# Build the React app (production build)
RUN npm run build

# Use a smaller image to run the app
FROM node:16-slim

# Set the working directory in the container
WORKDIR /app

# Copy the built app from the build stage
COPY --from=build /app/build /app/build

# Install serve to serve the React app (a minimal static file server)
RUN npm install -g serve

# Expose port 3000 (React default port)
EXPOSE 3000

# Run the React app using the 'serve' package (for production)
CMD ["serve", "-s", "build", "-l", "3000"]
