FROM ubuntu:16.04

MAINTAINER {{mantainer.email}}

ENV SLEEP_MILLIS 0

USER root

##############################################################
# Define all environment variables to be used 
##############################################################

ENV MARVIN_HOME=/opt/marvin
ENV MARVIN_DATA_PATH=/marvin-data
ENV MARVIN_ENGINE_HOME=$MARVIN_HOME/engine
ENV MARVIN_ENGINE_ENV=marvin-engine-env
ENV WORKON_HOME=$MARVIN_HOME/.virtualenvs
ENV SPARK_HOME=/opt/spark
ENV SPARK_CONF_DIR=$SPARK_HOME/conf
ENV HADOOP_CONF_DIR=$SPARK_CONF_DIR
ENV YARN_CONF_DIR=$SPARK_CONF_DIR


##############################################################
# Create all folders needed 
##############################################################

RUN mkdir -p $MARVIN_HOME && \
    mkdir -p $MARVIN_DATA_PATH && \
    mkdir -p $MARVIN_ENGINE_HOME && \
    mkdir -p /var/log/marvin/engines && \
    mkdir -p /var/run/marvin/engines


##############################################################
# Install the system dependencies for default installation 
##############################################################

RUN apt-get update -y && \
    apt-get install -y build-essential && \
    apt-get install -y maven git python cmake software-properties-common curl libstdc++6 && \
    apt-get install -y git && \
    apt-get install -y wget && \
    apt-get install -y python2.7-dev && \
    apt-get install -y python-pip && \
    apt-get install -y ipython && \
    apt-get install -y libffi-dev && \
    apt-get install -y libssl-dev && \
    apt-get install -y libxml2-dev && \
    apt-get install -y libxslt1-dev && \
    apt-get install -y libpng12-dev && \
    apt-get install -y libfreetype6-dev && \
    apt-get install -y python-tk && \
    apt-get install -y libsasl2-dev && \
    apt-get install -y python-pip && \
    apt-get install -y graphviz && \
    pip install --upgrade pip && \
    apt-get clean

RUN pip install virtualenvwrapper

# Install Oracle JDK
RUN add-apt-repository ppa:webupd8team/java -y && \
    apt-get -qq update && \
    echo debconf shared/accepted-oracle-license-v1-1 select true | debconf-set-selections && \
    echo debconf shared/accepted-oracle-license-v1-1 seen true | debconf-set-selections && \
    apt-get install -y oracle-java8-installer    


##############################################################
# Install Apache Spark
#
# Uncomment if you are using spark, note that is needed the 
# spark configuration files to the think works correctly.
##############################################################

# RUN curl https://d3kbcqa49mib13.cloudfront.net/spark-2.1.1-bin-hadoop2.6.tgz -o /tmp/spark-2.1.1-bin-hadoop2.6.tgz && \
#    tar -xf /tmp/spark-2.1.1-bin-hadoop2.6.tgz -C /opt/ && \
#    ln -s /opt/spark-2.1.1-bin-hadoop2.6 /opt/spark

# Add the b2w datalake config for Spark
# ADD spark-conf.tar $SPARK_CONF_DIR
RUN mkdir -p $SPARK_CONF_DIR

##############################################################
# Create the virtualenv configuration
##############################################################

RUN /bin/bash -c "cd $MARVIN_ENGINE_HOME && \
    source /usr/local/bin/virtualenvwrapper.sh && \
    mkvirtualenv $MARVIN_ENGINE_ENV"


##############################################################
#        <CUSTOM ENGINE INSTALLATION PROCEDURE HERE>         #
##############################################################


##############################################################
# Copy and Install the marvin engine inside virtualenv
##############################################################

ADD build/engine.tar $MARVIN_ENGINE_HOME

ADD build/marvin-engine-executor-assembly.jar $MARVIN_DATA_PATH 

RUN /bin/bash -c "source /usr/local/bin/virtualenvwrapper.sh && \
    workon $MARVIN_ENGINE_ENV && \
    cd $MARVIN_ENGINE_HOME && \
    pip install . --process-dependency-links"


##############################################################
# Starts the engine http server
##############################################################

EXPOSE 8000

CMD /bin/bash -c "source /usr/local/bin/virtualenvwrapper.sh && \
    workon $MARVIN_ENGINE_ENV && \
    cd $MARVIN_ENGINE_HOME && \
    marvin engine-httpserver -h 0.0.0.0 -p 8000"