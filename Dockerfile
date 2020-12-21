FROM python:3.8.1

WORKDIR /app
ADD requirements.txt /app/
RUN pip install -r /app/requirements.txt
ENV PYTHONUNBUFFERED 0
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /
RUN chmod +x /wait-for-it.sh