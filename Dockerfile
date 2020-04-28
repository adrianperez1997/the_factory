FROM ubuntu:bionic

ARG DEBIAN_FRONTEND=noninteractive
RUN apt update &&\
    apt install -y software-properties-common &&\
    apt-add-repository --yes --update ppa:ansible/ansible &&\
    apt install -y ansible &&\
    apt install -y python3-pip


ADD requirements.txt /
RUN pip3 install -r requirements.txt

RUN mkdir /keys

ADD hosts /etc/ansible/
ADD /keys/miclave /keys/
RUN chmod 600 /keys/miclave

ADD setup.yml /
ADD main3.py /

#CMD ["ansible', '-m','ping','localhost']
CMD [ "python3", "./main3.py" ]