# Use the official Selenium standalone Chrome container
FROM selenium/standalone-chrome:103.0.5060.53

# Install Python and pip
USER root
RUN apt-get update && apt-get install -y python3 python3-pip

# Install Selenium and Flask for Python
RUN pip3 install selenium flask bs4

# Ensure that the cache directory exists and has the correct permissions
RUN mkdir -p /home/seluser/.cache/selenium && chown -R seluser:seluser /home/seluser/.cache

# Set the working directory
WORKDIR /home/selenium

# Copy your Flask app and other necessary files
COPY . .

# Expose the port your Flask app runs on
EXPOSE 3000

# Run the Flask app
CMD ["python3", "app.py"]
