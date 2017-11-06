### Marvin Prediction-IO Docker Image

This docker project builds a **Prediction-IO** image to support things like

- Build and test engines
- Create docker containers to run pio train and pio deploy


## How to use

To build the image just run `sh build.sh <tag version>` specifying the tag for your image.

## Dependencies

To build this project the following dependencies must be met

- Elasticsearch download - The build process will try to download elastcisearch **1.7.5** from the internet.
- Spark download - The build process will try to download spark **1.6.3** from the internet.
- Prediction-IO download - The build process will try to download Prediction-IO **0.10.0** (B2W Fork) from the internal network.
- SBT cache files - In order to optmize the build time the build process will try to download ivy and sbt custom tars from the internal network. These files are not required to build, if they're missing you can remove from Dockerfile.