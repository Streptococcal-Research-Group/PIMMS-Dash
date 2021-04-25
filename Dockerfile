# Use base R image (easier than using Python then installing R images)
FROM r-base:4.0.4
# Set to noninteractive - makes  the  default  answers  be used for all questions
ENV DEBIAN_FRONTEND=noninteractive

# Update apt-get, intsall basic depandancies for Bioconductor, install python
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gdb libxml2-dev libssh-4 libssh-dev libcurl4-openssl-dev \
        python3.9 python3-pip python3-setuptools python3-dev

# Cleanup
RUN apt-get clean \
	&& rm -rf /var/lib/apt/lists/*


# Install bioconductor and DESeq2
COPY install_R_deps.R .
RUN Rscript install_R_deps.R

# Upgrade pip
RUN pip3 install --upgrade pip

# Set python path
ENV PYTHONPATH "${PYTHONPATH}:/pimms_dash"
WORKDIR /pimms_dash

COPY requirements.txt .

# Install python dependancies
RUN set -ex && \
    pip install -r requirements.txt

EXPOSE 8050

COPY pimms_dash .

CMD ["python3", "index.py"]