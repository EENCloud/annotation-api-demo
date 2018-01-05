FROM fedora:20

RUN yum clean metadata && yum install -y \
 vim \
 tagflow-1.3.15 \
 python-pip \
 && yum clean all \
 && mkdir /code \
 && pip install requests

WORKDIR /code

ADD gps.py gpsparse.py eenclient.py gps.txt /code/

CMD ["bash"]