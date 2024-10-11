# Introduction 
The PIMMS (Pragmatic Insertional Mutation Mapping System) pipeline has been developed for simple conditionally essential genome discovery experiments in bacteria.
This Dashboards aims to provide interactive visualisation of the PIMMs pipeline results.

---

### Prerequisites

To run the PIMMS Dashboard, ensure you have the following installed:

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- Web browser (for accessing the dashboard)
  
### Local Development

You can build and run the application locally using Docker. Follow these steps:

1. **Build the Docker image**:
   ```sh
   docker build -t pimmsdash .
   ```

2. **Run the Docker container**:
   ```sh
   docker run --rm -p 8050:8050 pimmsdash
   ```

3. **Access the dashboard**:
   Open your browser and go to:
   ```
   http://127.0.0.1:8050/
   ```

### Deployment

This project is also deployed on Azure App Service. You can access the live version here:

- [PIMMS Dashboard on Azure](https://pimms-dashboard-uon.azurewebsites.net/)


## Issues

If you encounter any bugs or have feature requests, please submit them via the [GitHub Issues](https://github.com/your-repository-link/issues) page.

## License

This project is licensed under the [MIT License](LICENSE).

---


# Contribute
To contribute to this repository, please use separate branches for 
development of each feature, and use the Pull Request system rather
than merging directly into `main`.
