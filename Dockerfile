FROM centos:7

RUN yum install -y epel-release && \
    yum install -y gcc && \
    yum install -y gcc-c++ && \
    yum install -y git && \
    yum install -y postfix && systemctl enable postfix && \
    yum install -y python36 && \
    yum install -y python36-devel && \
    yum install -y python36-pip && \
    pip3.6 install pip --upgrade

RUN git clone https://github.com/facebookresearch/fastText.git && \
    cd fastText && \
    pip3.6 install .

RUN git clone https://github.com/tkishimoto/gridalert.git && \
    cd gridalert && \
    pip3.6 install -e .
