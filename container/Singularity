Bootstrap: docker
From: centos:7

%post
    yum install -y epel-release 
    yum install -y gcc 
    yum install -y gcc-c++ 
    yum install -y postfix && systemctl enable postfix 
    yum install -y logwatch 
    yum install -y git 
    yum install -y python36 
    yum install -y python36-devel 
    yum install -y python36-pip 
    pip3.6 install pip --upgrade

    git clone https://github.com/facebookresearch/fastText.git 
    cd fastText 
    pip3.6 install .

    git clone https://github.com/tkishimoto/gridalert.git 
    cd gridalert 
    pip3.6 install -e . 
    cp logwatch/conf/logfiles/* /etc/logwatch/conf/logfiles/ 
    cp logwatch/conf/services/* /etc/logwatch/conf/services/ 
    cp logwatch/scripts/services/* /etc/logwatch/scripts/services/

