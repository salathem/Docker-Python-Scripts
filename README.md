# README

A simple setup script for running a Python script on a cron job inside a docker container.

1. Replace `src/script.py` with your Python file.
2. Add any requirements for the Python script in `/src/requirements.txt`.
3. Replace `src/crontab/` with your desired cron (see https://crontab.guru/).
4. In the root directory, run 
	* `docker build -t IMAGE_NAME .`
	* `docker run -d --name CONTAINER_NAME IMAGE_NAME` (including any other arguments you might need e.g. environment variables)
	
Ensure `src/script.py` and `src/crontab` have Unix line endings.
For CRON debugging see [this post](https://stackoverflow.com/questions/22743548/cronjob-not-running)  
