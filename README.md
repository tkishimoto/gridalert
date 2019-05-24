gridalert
====

gridalert provide methods to detect, alert and visualize anomaly logs using Machine Learning techniques for (Grid) compuring site operation. 

## Installation (docker build)
Dockerfile is available to build a docker image of the gridalert.

    $ git clone https://github.com/tkishimoto/gridalert.git 
    $ cd gridalert
    $ docker build -t gridalert .  
    $ docker run --rm --name gridalert -p 8080:8080 -v {YOUR_DATA_DIRECTORY}:/root/mnt/ -it gridalert    
   
{YOUR_DATA_DIRECTORY} is a directory path, which contains input data and configuration file described below. Please see contents of the Dockerfile if you want to install the gridalert to physical machines.
## Command line interfaces 
All commands of the gridalert require a configuration file (e.g. conf.ini) for the configparser.

    $ gridalert {text,vector,cluster,plot,cherrypy,html,alert,all} -c conf.ini
    
* text: extract information from text log files, then store it to database.
* vector: vectorize the text logs.
* cluster: perform vector clustering.
* plot: make plots.
* cherrypy: launch cherrypy for visualization.
* html: make static html files (under development).
* alert: alert anomaly events (under development).
* all: do text, vector, cluster, plot, alert.

Please see gridalert/main.py if you want to use gridalert module directly.

## Configuration 
The following is an example of the configuration file. [cluster/xxxx] need to be defined to run the gridalert.

    [DEFAULT]
    base_dir  = /tmp/
    date_start = 2019-01-01 00:00:00
    date_end   = 2030-01-01 00:00:00

    [db]
    path = /root/mnt/database.db

    # Clusters config
    [cluster/lcg-fs_fasttext_isolationforest]
    name = lcg-fs_fasttext_isolationforest
    hosts = lcg-fs1.*
    services = cron,sshd
    text_input = /root/mnt/logwatch/*
    vector_type = fasttext
    cluster_type = isolationforest

    [cluster/lcg-fs_doc2vec_isolationforest]
    name = lcg-fs_doc2vec_isolationforest
    hosts = lcg-fs1.*
    services = cron,sshd
    text_input = /root/mnt/logwatch/*
    vector_type = doc2vec
    cluster_type = isolationforest
