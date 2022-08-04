# Start from the python 3.10 image
FROM python:3.10

# Make a directory at /app
RUN mkdir /app
# Copy all the files in the repo in /app
COPY . /app
# Define /app as the working directory
WORKDIR /app

# install python dependencies
RUN pip install -r requirements.txt

# Update the system
RUN apt update -y && apt upgrade
# Install TOR
RUN apt install tor -y
# Set the Control port to allow ip renew
RUN echo "ControlPort 9051" >> /etc/tor/torrc

# Change your password here! (with: tor --hash-password "your password here")
ENV TOR_PASSWORD="16:6710B9B3468CA479608B0F46A6AF973EF7009ECD1698BD79F39283E2C4"

# Set the password for IP renew
RUN echo "HashedControlPassword $TOR_PASSWORD" >> /etc/tor/torrc

# Start tor and run the requests
CMD service tor start; python ip_renew.py