FROM python:3.10

# Update apt-get package list, grab pre-requisites 'cron' & 'vim'
RUN apt-get update && apt-get -y install cron vim

# Set the working directory for following commands in this docker container to '/app'
WORKDIR /app

COPY src/crontab /etc/cron.d/crontab
COPY src ./

RUN apt-get install python3-pip -y

# Make the crontab executable
RUN chmod 0644 /etc/cron.d/crontab

# Set the cron job
RUN crontab /etc/cron.d/crontab

# Install requirements
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

# Create empty log (TAIL needs this)
RUN touch /tmp/out.log

# Run cron and tail the log
CMD cron && tail -f /tmp/out.log