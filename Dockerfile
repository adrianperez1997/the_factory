FROM ubuntu:bionic

ARG DEBIAN_FRONTEND=noninteractive
RUN apt update &&\
    apt install -y software-properties-common &&\
    apt-add-repository --yes --update ppa:ansible/ansible &&\
    apt install -y ansible &&\
    apt install -y python3-pip &&\
    ansible-galaxy install geerlingguy.docker &&\
    ansible-galaxy install geerlingguy.pip


ADD requirements.txt /
RUN pip3 install -r requirements.txt

RUN mkdir /keys

COPY /keys/* /keys/

COPY /data/* /data/
COPY /web/ /web/

RUN chmod 600 /keys/miclave
RUN chmod 644 /keys/miclave.pub

ADD main.py /
RUN chmod 700 /main.py
RUN python3 /web/manage.py migrate

CMD ["python3", "/web/manage.py", "runserver" ]