FROM marvinai/marvin-base

USER root

#ADD http://archive.apache.org/dist/spark/spark-2.1.1/spark-2.1.1-bin-hadoop2.6.tgz /opt/

COPY spark-2.1.1-bin-hadoop2.6.tgz /opt/

#Unpack tgzs
RUN tar -zxvf /opt/spark-2.1.1-bin-hadoop2.6.tgz --directory=/opt \
	&& mv /opt/spark-2.1.1-bin-hadoop2.6 /opt/spark 

#Add configuration files
ADD hdfs-site.xml /opt/spark/conf
ADD core-site.xml /opt/spark/conf
ADD hive-site.xml /opt/spark/conf
ADD yarn-site.xml /opt/spark/conf

ADD engine.tar /opt/engine

COPY virtualenv_entrypoint.sh /

RUN chown marvin:marvin -R /opt/engine \
	&& apt-get install -y pkg-config \
	&& pip install -U setuptools \
	&& chown marvin:marvin /virtualenv_entrypoint.sh

USER marvin

ENV SPARK_HOME /opt/spark
ENV HADOOP_CONF_DIR /opt/spark/conf
ENV MARVIN_HOME /opt/engine

RUN cd /opt/engine \
        && bash -c 'source /usr/local/bin/virtualenvwrapper.sh && mkvirtualenv engine-env && setvirtualenvproject'

ENTRYPOINT "/virtualenv_entrypoint.sh"
CMD ["workon engine-env"]
#workon engine-env && marvin engine-httpserver