FROM python:3.11
WORKDIR /app
ADD . /app
ADD ./.aws/credentials /root/.aws/credentials
RUN apt-get update && apt-get install -y supervisor
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
EXPOSE 8000 27017 27016 27015 587 25
CMD python ./app.py
#CMD ["supervisord", "-n"]