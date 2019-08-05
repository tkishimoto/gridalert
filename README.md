gridalert
====

gridalert provide methods to detect, alert and visualize anomaly logs using Machine Learning techniques for (Grid) compuring site operation. 

## Installation (docker build)
Dockerfile is available to build a docker image of the gridalert.

    $ git clone https://github.com/tkishimoto/gridalert.git 
    $ cd gridalert/container
    $ docker build -t gridalert .  
    $ docker run --rm --name gridalert -p 8080:8080 -v {YOUR_DATA_DIRECTORY}:/root/mnt/ -it gridalert    
   
{YOUR_DATA_DIRECTORY} is a directory path, which contains input data. Please see contents of the Dockerfile if you want to install the gridalert to physical machines.
## Command line interfaces 
All commands of the gridalert require a configuration file (e.g. conf.ini) for the configparser. Details of the configuration file are shown in the next section.

    $ gridalert {text, vector, cluster, scan, plot, cherrypy, alert} -c mnt/conf.ini

* text: extract information from text log files, then store it to database.

A program need to be developed to parse text logs. template/messages_template.py is an example to parse the /var/log/messages files. execute() method recieves a path to text log, and returns a list of data with the following format.

    list  = [data0, data1, data2, ...]
    dataX = [host,     # host name
             date,     # timestamp ('%Y-%m-%d %H:%M:%S')
             service,  # service name (e.g. sshd) 
             metadata, # additional information if needed
             data      # log message, 
             label     # label of data for supervised ML

A logwatch script for Disk Pool Manager(DPM) is available in the logwatch directory. Text analysis programs for the logwatch are also available in the template directory. The following configurations are required for the built in analysis for the DPM.

    [cluster/YOUR_CLUSTER_NAME]    
    text_type = logwatchfine
    services = dmlite-httpd,dmlite-xrootd,dmlite-other  
    
* vector: vectorize the text logs.
* cluster: perform vector clustering.
* scan: scan hyper parameters for vector and cluster
* plot: make plots.
* cherrypy: launch cherrypy for visualization.
* alert: alert anomaly events.

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
