FROM debian:jessie

RUN echo "deb http://http.debian.net/debian jessie-backports main" >> /etc/apt/sources.list \
	&& apt-get update \
	&& apt-get install -y software-properties-common curl wget \
	&& apt-get install -yt jessie-backports openjdk-8-jdk \
	&& apt-get install -y git \
	&& apt-get -qy install python2.7-dev python-pip ipython libsasl2-dev gcc \
	&& apt-get -qy install libffi-dev \
	&& apt-get -qy install libssl-dev \
	&& apt-get -qy install libxml2-dev libxslt1-dev \
	&& apt-get -qy install libpng12-dev libfreetype6-dev \
	&& apt-get -qy install python-tk

#Engines will run using the user marvin
RUN useradd --create-home -s /bin/bash -G sudo marvin

##Install virtualenv
ENV WORKON_HOME /home/marvin/.virtualenvs
RUN pip install -q virtualenvwrapper \
	&& echo 'source /usr/local/bin/virtualenvwrapper.sh' >> /home/marvin/.profile

#Take ownership of needed folders
RUN chown -R marvin:marvin /opt

USER marvin
WORKDIR /home/marvin
