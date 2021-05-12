# Introduction 
The PIMMS (Pragmatic Insertional Mutation Mapping System) pipeline has been developed for simple conditionally essential genome discovery experiments in bacteria.
This Dashboards aims to provide interactive visualisation of the PIMMs pipeline results.

## Build and run
Install docker desktop

```sh

docker build -t pimmsdash .
docker run --rm -p 8050:8050 pimmsdash
```

## Access the page

Go to `http://127.0.0.1:8050/` in browser.

## Azure AppService / ContainerRegistry
Currently containerised and stored on **drslinuxcontainerregistory**

Deployed though AppService to https://pimms-dashboard-uon.azurewebsites.net/

The dockerfile is configured to expose port 2222 to the azure app service ssh.

For instructions pushing to container registry see https://docs.microsoft.com/en-us/azure/container-registry/container-registry-get-started-docker-cli

# Contribute
To contribute to this repository, please use separate branches for 
development of each feature, and use the Pull Request system rather
than merging directly into `master`.
