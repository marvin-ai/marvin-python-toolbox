FROM marvinai/marvin-base

USER root

#ADD http://archive.apache.org/dist/spark/spark-2.1.1/spark-2.1.1-bin-hadoop2.6.tgz /opt/

#Unpack tgzs
#RUN tar -zxvf /opt/spark-2.1.1-bin-hadoop2.6.tgz --directory=/opt/ \
#	&& mv /opt/spark-2.1.1-bin-hadoop2.6 /opt/spark

ENV SPARK_HOME /opt/spark
ENV HADOOP_CONF_DIR /opt/spark/conf

#Add configuration files
ADD hdfs-site.xml /opt/spark/conf
ADD core-site.xml /opt/spark/conf

USER marvin

RUN git clone https://github.com/marvin-ai/marvin-python-toolbox.git \
	&& cd marvin-python-toolbox \
	&& bash -c "source /usr/local/bin/virtualenvwrapper.sh && mkvirtualenv python-toolbox-env \
			&& setvirtualenvproject && make marvin"

ENTRYPOINT bash -c 'source /usr/local/bin/virtualenvwrapper.sh && workon python-toolbox-env && marvin --help' \
	&& "${@}"

CMD /bin/bash
