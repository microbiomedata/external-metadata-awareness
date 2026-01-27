# Semsimian Server

A simple web server for the Semsimian project, written in Rust.

## Requirements:

- [Rust](https://www.rust-lang.org/tools/install)

  - rustup >= 1.28
  - rustc >= 1.89
  - cargo >= 1.89

## Installation:

0. Semsimian Server requires a local copy of the Phenio DB.  
   It will check for the existence of `$HOME/.data.oaklib/phenio.db`, and **automatically download the latest version** if it is missing.  
   However, if you wish to use a specific version, you may manually download a copy of `phenio.db.gz`  
   from https://data.monarchinitiative.org and unpack it into `$HOME/.data/oaklib`:

   ```bash
   mkdir -p ~/.data/oaklib
   cd ~/.data/oaklib
   wget https://data.monarchinitiative.org/monarch-kg/latest/phenio.db.gz
   gunzip phenio
   ```

### From `crates.io`

Semsimian Server is published to [crates.io](https://crates.io/crates/semsimian_server).  
To install it for local usage, you can run:

```bash
cargo install semsimian_server
```

This will install the binary to your `~/.cargo/bin` directory,  
which can be run from any directory by calling:

```bash
semserver
```

### From Source

1. Clone the repository:
   ```bash
   git clone https://github.com/monarch-initiative/semsimian-server
   ```
2. Build the project:
   ```bash
   cd semsimian-server
   cargo build
   ```
3. Run the server:
   ```bash
   cargo run
   ```

### Docker Image

A Dockerfile is provided for convenience. While it is hosted on [Google Cloud Platform](us-central1-docker.pkg.dev/monarch-initiative/monarch-api/semsimian-server:latest),  
it can be built locally.

To build the image, run the following command from the root of the repository:

```bash
docker build -t semsimian-server .
```

To run the image, run the following command:

```bash
docker run -p 9999:9999 semsimian-server
```

## Usage:

In debug mode (ie. `cargo build`), the server will be running on `http://localhost:9999`.  
The address and port can be configured in the `Rocket.toml` file, or by setting the `ROCKET_ADDRESS` and `ROCKET_PORT` environment variables.

The server exposes two endpoints:

- `/compare/<termset1>/<termset2>/<metric>`:  
  Returns a JSON object containing the similarity score between the two termsets.

  - `termset1` and `termset2`: comma-separated lists of ontology terms.
  - `metric`: (optional) the similarity method to use, one of:
    - `ancestor_information_content` (**default**)
    - `jaccard_similarity`
    - `phenodigm_score`
    - `cosine_similarity`  

- `/search/<termset>/<prefix>/<metric>?<limit>&<direction>`:  
  Returns a JSON object containing a list of ontology terms that match the search term and prefix.

  - `termset`: comma-separated list of ontology terms.
  - `prefix`: string that will be used to filter the results.
  - `metric`: (optional) the similarity method to use, one of:
    - `ancestor_information_content` (**default**)
    - `jaccard_similarity`
    - `phenodigm_score`
    - `cosine_similarity`  
  - `limit`: number, limit the number of results
  - `direction`: the direction of the associations to search for, one of:  
    `bidirectional`, `subject_to_object`, `object_to_subject`

Example endpoints:

- http://localhost:9999/compare/HP:0000001,HP:0000002/HP:0000003,HP:0000004
- http://localhost:9999/compare/HP:0000001,HP:0000002/HP:0000003,HP:0000004/jaccard_similarity
- http://localhost:9999/search/HP:0000001,HP:0000002/zfin/ancestor_information_content?limit=5&direction=bidirectional
- http://localhost:9999/search/HP:0000001,HP:0000002/zfin?limit=3&direction=bidirectional
