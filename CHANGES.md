## Changes log

### 0.0.3

	- Python 3 support general compatibility refactoring (#68)
    - Add marvin_ prefix in artefacts getters and setters to avoid user code conflicts   
    - Fixing #66 bug related to override the params default values
    - Refact artifacts setter and getter in engine templates
    - Making marvin.ini from toolbox be found by default
    - Making "params" as an execute method parameter to be possible to overriden default values in runtime
    - Enabling to inform extra parameters for executor's jvm customization. Fix #65
    - Improve spark conf parameter usage in cli's commands to use SPARK_CONF_DIR and SPARK_HOME envs.
    - Not use json dumps if response type is string. Fixed #67
    - Adding gitter tag to README file.
    - Remove deploy to pipy from build
    - Install twine in distribution task
    - Add --process-dependency-links in pip install command
    - General bug fixes

### 0.0.2

    - change executor vm parameter from modelProtocol to protocol
    - Generic Dockerfile template and make commands to be used to build, run and push containers    
    - fix spark conf dir parameter bug
    - create distribute task to simplify the pypi package distribution.

### 0.0.1

 - initial version
