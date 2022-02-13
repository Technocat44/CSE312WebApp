# this is the base image 
FROM python:3

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD [ "python3", "server/server.py"]