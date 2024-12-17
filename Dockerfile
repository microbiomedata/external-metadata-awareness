FROM ubuntu:latest

# todo could remove git (and just copy cwd contents into container)
# todo could remove mongosh and just interact within mongo container or host (which wouod require exposing port)
# todo couod remove duckdb and just copy a completed file to host
# todo remoke make and use soem kind of Docker automation?

RUN apt-get update -y
RUN apt-get upgrade -y

RUN apt-get install wget curl git make gnupg nano unzip -y

# mongosh
RUN wget -qO- https://www.mongodb.org/static/pgp/server-8.0.asc | tee /etc/apt/trusted.gpg.d/server-8.0.asc
RUN echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu noble/mongodb-org/8.0 multiverse" |  tee /etc/apt/sources.list.d/mongodb-org-8.0.list
RUN apt-get update -y
RUN apt install  mongodb-mongosh -y

# some projects just copy dev files into the container and then publish the image
RUN git clone https://github.com/microbiomedata/external-metadata-awareness.git
RUN cd external-metadata-awareness && git checkout thanks-o1

# would prefer to get pipx, pyenv and then specifically get 3.12.7
RUN apt install python3 -y
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1

RUN curl -sSL https://install.python-poetry.org | python3 -
RUN cd external-metadata-awareness && ~/.local/bin/poetry install

RUN echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

RUN wget --verbose https://github.com/duckdb/duckdb/releases/download/v1.1.3/duckdb_cli-linux-amd64.zip
RUN unzip duckdb_cli-linux-amd64.zip

## Set the working directory
#WORKDIR /app

## Copy the application code
#COPY . .

# Command to run a shell when the container starts
# or some other no-op loop?
CMD ["/bin/bash"]
