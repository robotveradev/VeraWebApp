FROM ubuntu:18.04

RUN export DEBIAN_FRONTEND=noninteractive \
&& apt-get update && apt-get install -y locales \
&& echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
&& locale-gen
RUN apt-get update && apt-get install -y --no-install-recommends apt-utils
RUN apt-get install -y software-properties-common \
&& add-apt-repository ppa:ethereum/ethereum \
&& apt-get -y update \
&& apt-get upgrade -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" \
&& apt-get install -y swig git solc libssl-dev openssl screen python3-pip python3-venv mc supervisor libjpeg-dev libmysqlclient-dev

# Install any needed packages specified in requirements.txt
COPY requirements.txt .
RUN pip3 install --trusted-host pypi.python.org -r requirements.txt
COPY . .
RUN python3 ./stopwords.py

# Set the working directory to /app
WORKDIR .

# Copy startup script in PATH
COPY docker-entrypoint.sh /usr/local/bin/

ENTRYPOINT ["docker-entrypoint.sh"]
