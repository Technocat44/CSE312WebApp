FROM python:3

ENV HOME /root
WORKDIR /root
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8080

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.9.0/wait /wait
RUN chmod +x /wait
#TODO: Need to add back the /wait command
CMD /wait && python3 server/server.py --host=0.0.0.0