# Use a minimal Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy and install dependencies from requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set a default command. This is optional but can be useful
# for showing a help message or running a default command
# if the user just runs "docker-compose up".
CMD ["/bin/bash"]