# this is the base image 
FROM python:3

# create and cd into this root directory
WORKDIR /app
ENV HOME /app

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD [ "python3", "app.py" ]