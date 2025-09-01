# Use an official Node runtime as a parent image
FROM node:20

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY src/routes/package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY src/routes ./

# Expose the port the app runs on
EXPOSE 3001

# Start the Node.js app
CMD ["npm", "start"]