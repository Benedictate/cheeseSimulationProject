# Use Node.js base image (includes npm)
FROM node:20

# Install Python (Debian base is used by default for node:20)
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy package manifests and install Node dependencies
COPY package*.json ./
RUN npm install

# Copy Node.js source
COPY src ./src

# Copy Python simulation files
COPY Main.py ./
COPY __init__.py ./
COPY helpers ./helpers
COPY Machines ./Machines

# Expose backend port
EXPOSE 3001

# Start Node.js app
CMD ["npm", "start"]