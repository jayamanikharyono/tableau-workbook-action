# Container image that runs your code
FROM python:3.6

# Install Deps
ADD requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copies your code file from your action repository to the filesystem path `/` of the container
RUN mkdir /action
COPY main.py /action/main.py
COPY tableau_api.py /action/tableau_api.py
COPY util.py /action/util.py
COPY entrypoint.sh /entrypoint.sh

# Code file to execute when the docker container starts up (`entrypoint.sh`)
RUN chmod +x entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
