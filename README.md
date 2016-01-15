Here is project to study distributed systems.


### Schema

There is 3 types of processes:
    - main process, which receives POST requests with input data and sends it for processing in workers. Workers respond with frequencies hash map, which is added by main process to redis database
    - broker process. Intermediary between main process and workers
    - worker process. Receives text and responds with frequencies map.


### Requirements
    
    - Python 3.5
    - Docker
    - Redis server
    - libzmq [http://zeromq.org/area:download](installed)
    
### Installation
    
    
    git clone ....
    cd wcpy
    pyvenv venv
    source venv/bin/activate
    pip install 
