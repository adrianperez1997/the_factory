FROM ubuntu:bionic

ARG DEBIAN_FRONTEND=noninteractive
RUN apt update &&\
    apt install -y software-properties-common &&\
    apt-add-repository --yes --update ppa:ansible/ansible &&\
    apt install -y ansible

RUN mkdir /keys

ADD hosts /etc/ansible/
ADD /keys/miclave /keys/

ADD requirements.txt /
ADD setup.yml /
ADD main3.py /


#RUN pip3 install -r requirements.txt
#CMD ["ansible', '-m','ping','localhost']
CMD [ "python3", "./main3.py" ]