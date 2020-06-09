# Introduction 
The PIMMS (Pragmatic Insertional Mutation Mapping System) pipeline has been developed for simple conditionally essential genome discovery experiments in bacteria.
This Dashboards aims to provide interactive visualisation of the PIMMs pipeline results.

## Build and run
Install docker desktop

```sh

docker build -t dash .
docker run --rm -p 8050:8050 dash
```

## Access the page

Go to `http://127.0.0.1:8050/` in browser.

# Contribute
To contribute to this repository, please use separate branches for 
development of each feature, and use the Pull Request system rather
than merging directly into `master`.
