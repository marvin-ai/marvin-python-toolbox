[![Build Status](https://travis-ci.org/marvin-ai/marvin-python-toolbox.svg)](https://travis-ci.org/marvin-ai/marvin-python-toolbox) [![codecov](https://codecov.io/gh/marvin-ai/marvin-python-toolbox/branch/master/graph/badge.svg)](https://codecov.io/gh/marvin-ai/marvin-python-toolbox)

# Marvin Toolbox v0.0.1

![](https://images-americanas.b2w.io/img/_staging/marvin/marvin.png)

# Quick Start

## Review

**Marvin** is an open source Artificial Intelligence platform that focus on help data science team members, in an easy way, to deliver complex solutions supported by a high-scale, low-latency, language agnostic and standardized architecture while simplifying the process of exploitation and modeling.

## Getting Started
* [Installing Marvin (Ubuntu and MacOS user)](#installing-marvin-as-ubuntu-and-macos-user)
* [Installing Marvin (Others SOs)](#installing-marvin-with-others-sos)
* [Creating a new engine](#creating-a-new-engine)
* [Working in an existing engine](#working-in-an-existing-engine)
* [Command line interface](#command-line-interface)
* [Running a example engine](#running-a-example-engine)

### Installing Marvin as Ubuntu and MacOS user
Take the following steps to install Marvin Toolbox:
1. Libsasl2-dev, Python-pip and Graphviz installation
```
Ubuntu: 
$ sudo apt-get install libsasl2-dev python-pip graphviz -y

MacOS: 
$ sudo easy_install pip
$ brew install openssl graphviz
```
2. VirtualEnvWrapper Installation
```
$ sudo pip install --upgrade pip
$ sudo pip install virtualenvwrapper
```
3. Spark installation
```
$ curl https://d3kbcqa49mib13.cloudfront.net/spark-2.1.1-bin-hadoop2.6.tgz -o /tmp/spark-2.1.1-bin-hadoop2.6.tgz

$ sudo tar -xf /tmp/spark-2.1.1-bin-hadoop2.6.tgz -C /opt/
$ sudo ln -s /opt/spark-2.1.1-bin-hadoop2.6 /opt/spark

$ echo "export SPARK_HOME=/opt/spark" >> $HOME/.bash_profile
```
4. Set environment variables
```
$ echo "export WORKON_HOME=$HOME/.virtualenvs" >> $HOME/.bash_profile
$ echo "export MARVIN_HOME=$HOME/marvin" >> $HOME/.bash_profile
$ echo "export MARVIN_DATA_PATH=$HOME/marvin/data" >> $HOME/.bash_profile
$ echo "source virtualenvwrapper.sh" >> $HOME/.bash_profile

$ source ~/.bash_profile
````

5. Clone and install python-toolbox

```
$ mkdir $MARVIN_HOME
$ mkdir $MARVIN_DATA_PATH
$ cd $MARVIN_HOME

$ git clone https://github.com/marvin-ai/marvin-python-toolbox.git
$ cd marvin-python-toolbox

$ mkvirtualenv python-toolbox-env
$ setvirtualenvproject

$ make marvin
````

6. Test the installation
```
$ marvin test
```
### Installing Marvin with Others SOs
Take the following steps to install Marvin Toolbox using Vagrant:
1. Install requirements
- [Virtual box](http://www.virtualbox.org) (Version 5.1 +)
- [Vagrant](http://www.vagrantup.com) (Version 1.9.2 or +)


2. Clone repository and start provision
```
$ git clone https://github.com/marvin-ai/marvin-vagrant-dev.git
$ cd marvin-vagrant-dev
```

3. Prepare dev (engine creation) box
```
$ vagrant up dev
$ vagrant ssh dev
```
Wait for provision process and follow interactive configuration script after access the dev box using vagrant ssh command.

4. The marvin source projects will be on your home folder, to compile and use the marvin toolbox
```
$ workon python-toolbox-env
$ make marvin
```
### Creating a new engine
1. To create a new engine
```
workon python-toolbox-env
marvin engine-generate
```
Respond the interactive prompt and wait for the engine environment preparation, and don't forget to start dev box before if you are using vagrant.

2. Test the new engine
```
$ workon <new_engine_name>-env
$ marvin test
```
3. For more informations
```
$ marvin --help
```
### Working in an existing engine
1. Set VirtualEnv and get to engine's path
```
$ workon <engine_name>-env
```
2. Test your engine
```
$ marvin test
```
3. Bring up the notebook and access it from your browser
```
$ marvin notebook
```
### Command line interface
Usage: marvin [OPTIONS] COMMAND [ARGS]

Options:
```
  --debug       #Enable debug mode.
  --version     #Show the version and exit.
  --help        #Show this command line interface and exit.
```

Commands:
```
  engine-generate     #Generate a new marvin engine project.
  engine-generateenv  #Generate a new marvin engine environment.
  engine-grpcserver   #Marvin gRPC engine action server starts.
  engine-httpserver   #Marvin http api server starts.
  hive-dataimport     #Import data samples from a hive databse to the hive running in this toolbox.
  hive-generateconf   #Generate default configuration file.
  hive-resetremote    #Drop all remote tables from informed engine on host.
  notebook            #Start the Jupyter notebook server.
  pkg-bumpversion     #Bump the package version.
  pkg-createtag       #Create git tag using the package version.
  pkg-showchanges     #Show the package changelog.
  pkg-showinfo        #Show information about the package.
  pkg-showversion     #Show the package version.
  pkg-updatedeps      #Update requirements.txt.
  test                #Run tests.
  test-checkpep8      #Check python code style.
  test-tdd            #Watch for changes to run tests automatically.
  test-tox            #Run tests using a new virtualenv.
```

### Running a example engine 
1. Clone example engine from repository
```
$ git clone https://github.com/marvin-ai/engines.git
```
2. Generate a new marvin engine environment for Iris species engine
```
$ workon python-toolbox-env
$ marvin engine-generateenv ../engines/iris-species-engine/
```
3. Run the Iris species engine
```
$ workon iris-species-engine-env
$ marvin engine-dryrun 
```

> Marvin is a project started at B2W Digital offices and released open source on September 2017.
