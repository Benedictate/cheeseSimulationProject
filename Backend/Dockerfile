# Use Node 20 as base
FROM node:20-bullseye

# Install Python 3 and pip
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json first
COPY package*.json ./

# Install Node dependencies
RUN npm install

# Copy the rest of the backend code
COPY . .

# Install Python dependencies
RUN pip3 install simpy

# Expose the backend port
EXPOSE 3001

# Start backend
CMD ["npm", "start"]
