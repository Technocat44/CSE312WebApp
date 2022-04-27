FROM python:3 
# as base

ENV HOME /root
WORKDIR /root
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install pymongo
RUN pip3 install bcrypt

COPY . .

EXPOSE 8000
# ###########################################################
# FROM base as debug 
# RUN pip install ptvsd

# WORKDIR /root
# CMD python -m ptvsd --host=0.0.0.0 --port 5678 --wait --multiprocess -m python3 server/server.py 
# ########################################################
# FROM base as prod

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.9.0/wait /wait
RUN chmod +x /wait
#TODO: Need to add back the /wait command
CMD /wait && python3 app.py --host=0.0.0.0