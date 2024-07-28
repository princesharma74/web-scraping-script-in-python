FROM selenium/standalone-chrome:latest
WORKDIR /app
USER root
RUN apt-get update && apt-get install -y python3 python3-pip cron
COPY . /app
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN chmod +x /app/send_email/sql_helper.py
COPY cron_job.d /etc/cron.d/cron_job
RUN chmod 0644 /etc/cron.d/cron_job
RUN touch /var/log/cron.log
RUN crontab /etc/cron.d/cron_job
RUN cron
ENV PYTHONUNBUFFERED=1
ENV PIP_ROOT_USER_ACTION=ignore
