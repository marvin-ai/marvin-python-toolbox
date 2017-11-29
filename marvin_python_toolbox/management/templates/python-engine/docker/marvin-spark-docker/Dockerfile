FROM marvinai/marvin-base

USER root

ADD http://archive.apache.org/dist/spark/spark-2.1.1/spark-2.1.1-bin-hadoop2.6.tgz /opt/

#Unpack tgzs
RUN ls -l /opt \
	&& mv /opt/spark-2.1.1-bin-hadoop2.6 /opt/spark 

#Add configuration files
ADD spark-conf/* /opt/spark/conf/

ADD engine.tar /opt/engine

COPY virtualenv_entrypoint.sh /opt/engine

RUN chown marvin:marvin -R /opt/engine

USER marvin

ENV SPARK_HOME /opt/spark
ENV HADOOP_CONF_DIR /opt/spark/conf
ENV MARVIN_HOME /opt/engine

RUN cd /opt/engine \
        && bash -c 'source /usr/local/bin/virtualenvwrapper.sh && mkvirtualenv engine-env && setvirtualenvproject && make marvin'

ENTRYPOINT "/opt/engine/virtualenv_entrypoint.sh"
