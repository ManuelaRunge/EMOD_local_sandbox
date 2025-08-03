# EMOD_local_sandbox
Sandbox repository to test out EMOD simulations on a local machine.


## Installation 

- https://github.com/EMOD-Hub/emodpy-malaria/tree/main/examples-container#readme  
- https://github.com/InstituteforDiseaseModeling/idmtools/tree/main/idmtools_platform_container#readme  


> **How to run examples in container platform**  
>  - Install [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (or Docker engine) when running with container platform
>  - Make sure Docker Desktop (or Docker) is running
>  - Create a virtual environment (python)
>  - Activate the virtual environment
>  - Install [emodpy-malaria](https://github.com/EMOD-Hub/emodpy-malaria/tree/main) and dependencies
>  - Install [idmtools_platform_container](https://github.com/InstituteforDiseaseModeling/idmtools/tree/main/idmtools_platform_container) and dependencies if run container examples  

_Source: IDM, EMOD-Hub [examples-container#readme](https://github.com/EMOD-Hub/emodpy-malaria/tree/main/examples-container#readme)_  


**Steps (Windows):** 

1. Create a virtual environment:  
    ```
    python -m venv emod_local
    ```

2. Activate the virtual environment:  
    ```
    emod_local\Scripts\activate
    ```

3. Install emodpy-malaria:  
    ```
    pip install emodpy-malaria --extra-index-url=https://packages.idmod.org/api/pypi/pypi-production/simple 
    ```

4. Install all container platform related packages  
    ```
    pip install idmtools[container] --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple  
    ```

    - To override existing idmtools container related packages after installing emodpy, run this command
      ```
      pip install idmtools[container] --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple --force-reinstall --no-cache-dir --upgrade  
      ```

5.Check installation 

```
pip list | grep idmtools
pip list | grep emodpy
```

6. Submit simple example simulation from terminal


```
python example_container.py
```



7. To run interactively, update Python settings in Pycharm/Visual Studio
Also start a new session.

Ensure the correct path is used via 

```
import sys
print(sys.executable)
```


## Navigating the container  


- See running jobs:  
   ```
   idmtools container status <experiment id>
   ```

- See past jobs:  
   ```
   idmtools container history [<container-id>] [-l <limit>] [-n <next>]
   ```
  
- See job status: 
   ```
   idmtools container jobs [<container-id>] [-l <limit>] [-n <next>]
   ```

- Cancel job: 
   ```
   idmtools container cancel <item-id> [-c <container_id>]
   ```
  


## Additional examples

Run with a custom analyzer imported from `analyzer.py`  that runs after waiting within the same python session for simulations to finish.  

```
python example_integrated_analyzer.py
```


Run with a custom analyzer imported from `analyzer.py`  that is flexible to run independently after the simulations finish.  


```
python example_external_analyzer.py
```


Run advanced example including EMOD serialization.  
(not yet functional)
  
```
python example_serialization.py
```



