Here is project to study distributed systems.


### Schema

There is 3 types of processes:

- main process, which receives POST requests with input data and sends it for processing in workers. Workers respond with frequencies hash map, which is added by main process to redis database
- broker process. Intermediary between main process and workers. Broker process is required if we'll need to add more clients, e.g. for input from DB.
- worker process. Receives text and responds with frequencies map.


### Requirements
    
- Python 3.5
- Docker and docker-compose
- Redis server
- libzmq [installed](http://zeromq.org/area:download)
    
### Installation in local virtualenv
    
Run following commands to get working copy of project:

    git clone https://github.com/Riliam/wcpy.git
    cd wcpy
    pyvenv venv
    source venv/bin/activate
    pip install -e .

Now executable `wcpy` in $PATH should appear. It is created using `Click` toolkit. `wcpy --help` will show available commands.

### How to run project

1. Start Redis server. For example, using Docker:

        docker run --name wordcount -d -p 6379:6379 redis:3.0
    
2. Start 1 main process (options to change hosts or ports are availabe, see --help):

        wcpy main_run
    
3. Start 1 broker process (options available):

        wcpy broker_run
    
4. Start 1 or more worker processes:

        wcpy worker_run
    
5. Main process runs HTTP server on default port 8080, and accepts POST request on url `/add-frequencies` with key `text`. For example, using `httpie`:

        http -f POST localhost:8080/add-frequencies text="a b c d"
    
    or `curl`:

        curl --data "text=a b c d"  localhost:8080/add-frequencies
    
6. Top 10 frequent words will show in HTTP response as well as in server console output.

Alse, `wcpy spam` and `wcpy spam --random-strings` commands available, to send input to main process.


### docker-compose.yml

Given `docker-compose` installed, run:

    docker build -t local/wcpy .
    docker-compose up

Docker-compose exposes 8080 port, so `wcpy spam` or curl/httpie are required to send input data.
