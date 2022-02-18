
# this is the base image 
FROM python:3

ENV HOME /root
WORKDIR /root
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8000

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait

CMD [ "/wait", "python3", "server/server.py", "--host=0.0.0.0"]