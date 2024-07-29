# FROM selenium/standalone-chrome:latest
FROM seleniarm/standalone-chromium:latest
WORKDIR /app
USER root
RUN apt-get update && apt-get install -y python3 python3-pip
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt --break-system-packages
# RUN chmod +x /app/send_email/sql_helper.py
ENV PYTHONUNBUFFERED=1
ENV PIP_ROOT_USER_ACTION=ignore
