FROM python:3.5


RUN apt-get update -y &&\
    apt-get install -y libtool autoconf automake make g++ uuid-dev wget &&\
    cd /tmp &&\
    wget http://download.zeromq.org/zeromq-4.0.4.tar.gz &&\
    tar -xvf zeromq-4.0.4.tar.gz &&\
    cd zeromq-* &&\
    ./configure &&\
    make install &&\
    ldconfig &&\
    cd .. &&\
    rm -rf zeromq* &&\
    apt-get purge -y libtool autoconf automake make g++ uuid-dev wget


RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY . /usr/src/app
RUN pip install -e .

CMD ["wcpy", "--help"]