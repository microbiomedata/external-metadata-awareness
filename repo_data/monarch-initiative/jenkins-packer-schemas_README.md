# Jenkins Packer Schemas

This repo contains [Packer](https://www.packer.io/) templates for building
images for Monarch Initiative Jenkins agents.

### Required Libraries

- Python >= 3.10
- Python `sh` module
- Packer
- Google Cloud CLI

## Setup

0. Install Python 3 and pip:
  ```
  apt install python3 python3-pip
  pip install sh
  ```

1. [Install Packer](https://www.packer.io/downloads)

2. [Install Google Cloud CLI](https://cloud.google.com/sdk/docs/install-sdk)  

You'll need to expose credentials for a GCP account with the following assigned roles:
- `roles/compute.instanceAdmin.v1`
- `roles/compute.networkAdmin`
- `roles/compute.securityAdmin`
- `roles/iam.serviceAccountActor`

  Typically, you'd download a service account JSON key, then set the environment
  variable `GOOGLE_APPLICATION_CREDENTIALS` to its location, e.g.:

  ```
  export GOOGLE_APPLICATION_CREDENTIALS=$( realpath ./my-sa-key.json )
  ```

## Usage 

1. Change your working directory to the location of the template before running Packer so that any relative file references are able to be resolved.  
    ```
    cd <path to repo>
    ```

1. Initialize Packer with the required plugins:
    ```
    packer init .
    ```

1. Using one of the [build methods](#build-methods) below, build and release the image to GCP as an Instance Template.

1. Update Jenkins (ci.monarchinitiative.org) to use the new template:  
    - Navigate to `Manage Jenkins` > `Manage Nodes and Clouds` > `Configure Clouds`
    - Look for `monarch-agent-[small | medium | large]` in the list of Clouds
    - Under `Machine Configuration` > `Template to use`, select the new template from the dropdown menu.

1. (Optional) Delete the old instance template from GCP:  
    - In GCP, Navigate to Compute Engine > Instance Templates  
    - Select the old templates (smaller timesetamp), and click "Delete"

**Note**: It's useful to keep the most recent template around for a while in case you need to roll back.  
If you do need to roll back, just follow the steps above, but select the old template in step 4.  
However, it's a good idea to delete old templates after a while to avoid clutter.

### Build Methods

Method 1: Use the included [Python script](create_instance_templates.py):  

1. `python3 create_instance_templates.py`

Method 2: Manually build and release
 
1. Build an image from a Packer schema:  
  `packer build <template>`  
  This will spin up a VM, run the contents of the template against it, then generate an image.  

2. Push image to Google Cloud as a template:  

- Option 1: Via Google Cloud Platform web UI  
  - Navigate to Compute Engine > Instance Templates  
  - Click "Create Instance Template"  
  - Under "Boot Disk", click "Change", select "Custom Images", and choose the agent image you'd like to use.  
- Option 2: Via Command Line  
  - `gcloud compute instance-templates create <options>`
  - See the Monarch Instance Template creation [shell script](create_instance_template.sh) for an example command.


## Agent Templates

The repo contains the following templates:

- `monarch-agent.pkr.hcl`:  
Template for packer to generate an Ubuntu 22.04 LTS image with Python3.10 + Poetry,  
as well as GCSFuse, AWS CLI, and Docker.  
For use with Monarch Initiative Jenkins.

- `archive/jenkins-agent-java-py3-docker.json`: 
A modified version of the original agent image template; adds Java, Python 3, and Docker.  
*(Archived, but included for reference.)*

- `archive/jenkins-agent.json`:  
The original agent image template from following the tutorial ["Using Jenkins for distributed builds on Compute Engine"](https://cloud.google.com/architecture/using-jenkins-for-distributed-builds-on-compute-engine#configuring_jenkins_plugins).  
Includes just the default Java JDK.  
*(Archived, but included for reference.)*

