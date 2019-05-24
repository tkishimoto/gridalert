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

    $ gridalert all -c conf.ini
