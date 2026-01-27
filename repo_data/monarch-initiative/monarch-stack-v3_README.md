# monarch-stack-v3 README

This repo contains tooling to provision and deploy the Monarch stack v3, currently consisting of these three services:
- the Monarch REST API, which supports the Monarch v3 UI
- a Solr instance to provide named entity and association data to the api
- a Neo4j instance for interactive graph browsing

To do this, we deploy the following resources:
- A VM running a neo4j server hosting the MonarchKG. (monarch-v3-XXX-neo4j)
- A VM running solr.
- A VM running the Monarch Initiative's API (very general, runs mcq, etc).
- A VM which is the "manager" of the three previous "worker" machines.
- A load balancer which directs traffic to and from these VMs.

This document will outline the process by which one can deploy a fresh versions of these compute instances.

## The basics 
The stack relies on [Terraform](https://www.terraform.io/) to provision cloud
resources, currently on Google Cloud (aka "GCP"). Once Terraform has provisoned
virtual machines ("VMs" or "nodes") to run the services,
[Ansible](https://www.ansible.com/) is then used to install Docker on each VM,
then join the VMs to a [Docker Swarm](https://docs.docker.com/engine/swarm/).
Swarm is used to schedule the containers that make up the Monarch stack on each
VM. Services that share data are scheduled on the same VM (i.e. the monarch-API, as are services that
are too small on their own to warrant their own VM.


## Prior knowledge
To construct and deploy our cloud instances we need a few tools and their specific terms to help us.
### GCP / Google Cloud Platform
We use the Google Cloud Platform (GCP) as our provider of cloud resources. What this mainly entails for our purposes here is spinning up and shutting down "instances" (virtual computers which we control running on Google's servers)
### Docker
[Docker](https://docs.docker.com) is a tool which aims to standardize software deploy processes. It tries to create a blank canvas in a small pocket on a computer which can be used to host software. The reason why this is useful is modern software distribution and deploying is quite gnarly; software often depends on other software in a very complex fashion. Even small seemingly minor changes to a tiny library somewhere can render a machine inoperable without intervention. Docker tries to work around this by capturing the state of all dependencies needed to run some in a little box called an "image".  We use Docker to help us create machine templates and deploy these templates to the VMs we spin up.
##### Docker Swarm
[Docker Swarm](https://docs.docker.com/engine/swarm/) is an extension of the Docker system which interlinks multiple deployed VMs into one entity which can be collectively managed.
### Terraform
[Terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli) is a tool which aims to make resource requests to cloud resource providers more flexible and interoperable (in the event we ever decide to change to AWS hypothetically it would be easier). What we use Terraform for is we pass it the terraform configuration files (*.tf in deployment/terraform) and a host of information on what we want to name machines using the environment variables from site-envs. If properly configured it will run and create a set of 4 virtual machines. Terraform also has a large amount of "state" information on the machines which were created, which enables us to easily find and communicate with these machines.
 ### Ansible 
 [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html) is a reference to an idea from author Ursula K Le Guin of a machine which can communicate instantaneously across time and space. I personally think that's a bit overkill, but Ansible does give us a suite of tools to put software on the VMs (in our case, the VMs we created using Terraform). The basics of how Ansible works is that you provide it an "inventory" file which contains information on the specific machines which are running and a "playbook" file, which contains a set of instructions which we want to run on each cloud machine in a specific order. Ansible then provides us detailed progress and error reports on the status of these executions.


## Deploy tutorial
I'm going to assume the deploy will be running on a fresh Google Cloud VM instance and testing it as such. Likely this will only give me a pretty fresh machine so it should be close to any other machines. The box these instructions were written on is running Debian.

### Step 1 - Prerequisites and getting tools/software ready

#### Step 1.1 - Git clone this repo
```
sudo apt-get install git
```
Since this is a read and write protected repo, you'll need to follow the instructions [here](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account) to get git command line to be able to talk to this repo. This entails the following steps.
```
ssh-keygen -t ed25519 -C YOUR_GITHUB_ACCOUNT_EMAIL@EMAIL.ORG
cat ~/.ssh/id_ed25519.pub
```
Copy and paste this into Github.com (click top right)->settings->SSH and GPG keys->New SSH Key
```
git clone git@github.com:monarch-initiative/monarch-stack-v3.git
```

#### Step 1.2 - Get GCP permissions
One of the more complicated things with cloud deploying is how to actually get the machine you're executing *'monarch-stack-v3'* on to be able to talk to google cloud. A lot of detail for what happens is detailed in 1.  [.secrets/Readme.md](.secrets/Readme.md). In this description of execution, I'm going to run things slightly differently, just to help ensure the permissions file is corrected downloaded.
- Go to the following link: [https://console.cloud.google.com/iam-admin/serviceaccounts?project=monarch-initiative](https://console.cloud.google.com/iam-admin/serviceaccounts?project=monarch-initiative)
 - Select terraform@monarch-initiative.iam.gserviceaccount.com from the list of possible service accounts.
 - Select KEYS from the tabs at the top of the page.
 - Select ADD KEY->Create new key. Choose JSON and press create.
This should've sent a JSON file downloaded onto the computer running the browser with the name *monarch-initiative-XXX.json*.
You need to transfer *monarch-initiative-XXX.json* onto the machine you're running the deploy from (likely just upload the file).
Now put the JSON file you just put onto the server into the .secrets directory.
```
mv ~/monarch-initiative-XXX.json ~/monarch-stack-v3/.secrets/.
```
If you aren't running this process on a fresh GCP VM (on your own workstation for example), you're going to have install gcloud CLI (what let's the command `gcloud` work in Step 2.1). You can find info on installing this [here](https://cloud.google.com/sdk/gcloud#download_and_install_the). 
>##### Side note - Could we use a different service account?
>We use 'terraform@monarch-initiative.iam.gserviceaccount.com' as the service account for performing all of our operations on the GCP, but it isn't necessary to use that account. If one wanted to ever change this you'd need to make a service account under monarch-initiative project. This service account would need permissions to be able to create and destroy VMs and also read and write access to a bucket with the same name provided by $TF_VAR_state_bucket (in Step 1.3)

>##### Side note - Aligning with most deploys
>Some of our deploy setups have a built in assumption the terraform secret file will be located at `$HOME/.secrets/terraform@monarch-initiative.iam.gserviceaccount.com.json`. You can accomplish this by changing the above command to `mv ~/monarch-initiative-XXX.json ~/monarch-stack-v3/.secrets/terraform@monarch-initiative.iam.gserviceaccount.com.json`. 

#### Step 1.3 - Setup environment variables
The specific environment variables present on a machine are what let terraform and ansible create unique deploys. We're going to modify an arbitrary exist configuration to make this work. To set these up
```
cd ~/monarch-stack-v3/deployment/site-envs
cp monarch-dev.env TEST_DEPLOY.env
```
First we want to set this file to point to our credentials we got in Step 1.2. Run
```
realpath ~/monarch-stack-v3/.secrets/monarch-initiative-XXX.json
```
Then copy replace the path of `export TF_VAR_credentials_file` on line 4 with the output from above.
Now we'll modify the name of the entire deployment. Change line 6 to
```
export TF_VAR_env="NEW_UNIQUE_VAL"&&exit
```
You *must* change the value of NEW_UNIQUE_VAL (and remove the exit) to something unique or future steps won't work and will throw a bunch of very confusing errors.
Once you've made the change above run
```
source TEST_DEPLOY.env
```
to set all those parameters as part of your environment. (Note to future me; if your terminal just crashed, you likely copy and pasted the change to TF_VAR_env without looking at it; you need to set it to something unique and remove the && exit from the end of the line.)
>##### Side notes on these environment variables
>All of these environment variables could hypothetically be changed, but probably shouldn't be without massive changes to how GCP is setup; the only one's that are likely to need to be modified in future deploys are $MONARCH_KG_VERSION, $MONARCH_API_VERSION, $TF_VAR_credentials_file, and $TF_VAR_env. 

### Step 1.4 - Install Terraform
Terraform install instructions are located [here](https://developer.hashicorp.com/terraform/install). I'm going to summarize all of the steps to the essentials, but if they don't work please refer to that link.
```
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform
```
### Step 1.5 - Install Ansible
Ansible is a strange piece of software that seems to have about 12 ways to install it. I'll just give you the one that worked for me.

```
sudo apt-get install pipx
pipx install ansible-core
pipx ensurepath
```
Assuming that worked, you're going to have to **restart your terminal** (or just run *screen*, which is my personal preference). Now we're going to have to install two plugins for Ansible to let it properly work with our playbook.
```
ansible-galaxy collection install community.docker
ansible-galaxy collection install community.general
```
Now with all of the setup out of the way; we can start running the build processes.


### Step 2 - Run Terraform
#### Step 2.1 - Get GCP credentials setup.
This command needs be run to give Terraform the gcp credentials.
```
export GOOGLE_APPLICATION_CREDENTIALS=$TF_VAR_credentials_file
#export GOOGLE_APPLICATION_CREDENTIALS=$(realpath TERRAFORM_KEY_XXX.JSON)
gcloud auth activate-service-account --key-file="${GOOGLE_APPLICATION_CREDENTIALS}"
```
We're also going to have reinitiate the environment variables because we had to restart the terminal to set up ansible.
```
source ~/monarch-stack-v3/deployment/site-envs/TEST_DEPLOY.env
```
#### Step 2.2 - Terraform init
Initialize the terraform process (this takes in the 5 terraform configuration files in deployment/terraform/*.tf and the environment variables and the environment variables from 

```
cd ~/monarch-stack-v3/deployment/terraform
terraform init -var-file ../terraform.tfvars -backend-config="bucket=$TF_VAR_state_bucket" -backend-config="prefix=$TF_VAR_state_bucket_prefix"
```
>#### Side note
>If you want to look at what Terraform will run the following `terraform plan -var-file ../terraform.tfvars`
>It may be helpful to contain your Terraform to a special workspace. This will help if you do multiple deploys from the same machine.
>```
>terraform workspace new "${TF_VAR_env}"
>terraform workspace select "${TF_VAR_env}"
>```

#### Step 2.3 - Terraform apply
Run Terraform to allocate resources on GCP. 
```
terraform apply -var-file ../terraform.tfvars #enter "yes"
```
Finally grab the resulting state of the Terraform deploy and put it into a local JSON file.
```
 terraform state pull > terraform_state_${TF_VAR_env}.json
```

> #### Side Note
> Once you feel comfortable with the basics of the Terraform process, you should look at `~/monarch-stack-v3/deployment/provision.sh`. It provides a lot of deployment functionality inside a single script, including the ability to destroy/tear down a terraform deployment.

### Step 3 - Run Ansible

#### Step 3.1 - Make Ansible inventory file
Ansible needs an "inventory" file to help it catalog all of the machines it should send commands to. We've created a python script which takes in the "state" information from the Terraform deploy and converts it into a format Ansible can use.
```
cd ../ansible
python3 terraform_state_to_ansible_inventory.py --input ../terraform/terraform_state_${TF_VAR_env}.json --output ansible_inventory_${TF_VAR_env}.yml
```
> ##### Side note
> To look how Ansible reads in the inventory file (e.g. what exact information it extracts from it), you can run `ansible-inventory -i ansible_inventory_${TF_VAR_env}.yml --graph` and `ansible-inventory -i ansible_inventory_${TF_VAR_env}.yml --list`. This helps massively in validation if the information in the inventory ever needs to be modified.

#### Step 3.2 - Run the "playbook"
Ansible documents all of the actions it plans to perform on "the cloud" in files called "Playbooks". Our playbook is located in 3 files. The primary playbook is `~/monarch-stack-v3/deployment/ansible/setup_swarm.yml`. This file invokes two more playbooks; `support/setup_docker.yml` on line 28-30 and `setup_stack_app.yml` on link 98-99. 
To run Ansible call:
```
ansible-playbook --inventory ansible_inventory_${TF_VAR_env}.yml setup_swarm.yml
```
Please note, the first Ansible command may take a very long time to complete (I'd estimate up to an hour) because the command needs to wait for the initialization process of all machines from the Terraform deploy to complete.

### Step 4 - Destroy your setup
Nothing is permanent. Destroy your new found creation before the unavoidable march of time does it for you.
```
cd ~/monarch-stack-v3/deployment/terraform
terraform destroy --var-file ../terraform.tfvars #Enter 'yes' when prompted
```
You'll likely need to run this command multiple times to get the destroy to fully take. If you run into any issues, you likely need to make sure you're in the right terraform workspace ( `terraform workspace list`), have run site-envs, and $GOOGLE_APPLICATION_CREDENTIALS configured correctly.

## Other release tasks

### Get MonarchKG data's latest release updated.
```
gsutil rm -r gs://data-public-monarchinitiative/monarch-kg/latest
gsutil -m cp -r gs://data-public-monarchinitiative/monarch-kg/${MONARCH_KG_VERSION} gs://data-public-monarchinitiative/monarch-kg/latest
```

## Advanced Usage/Chesteron Fence documentation
Once you've completed the tutorial/basic deploy above, we have some more useful tools and documentation.

1. Make any stack customizations you want to make in the [deployment/terraform.tfvars](deployment/terraform.tfvars) file.  
  This can either be done by editing the file directly, or by setting environment variables via the `.env` files in [deployment/site-envs](deployment/site-envs).  
  See the [Configuration](#configuration) section for details. 

1. Setup the service VMs, enter `deployment` and run the `./provision.sh` ([deployment/provision.sh](deployment/provision.sh)) script.  
  Use the `-h` flag to see the available options.

1. Once the script has finished, you can destroy the provisioned resources by running `./provision.sh -d -na`.   

    **Note:** do NOT `ctrl-c` the script while it's running, as this will leave the  
    resources in an inconsistent state. Instead, wait for the script to finish or fail,  
    then use `./provision.sh -d -na` to destroy the resources.

### Notes on Provisioning

The `provision.sh` script follows approximately this process:

  - First, terraform will run, and will compare the desired resources to what's  
    currently deployed; if this is the first time running the script, you'll only  
    see additions, but if you've run it before you might also see removals or  
    changes if you've changed your terraform config since the last time you ran it.  
    You'll be asked for your approval, and must explicitly answer `yes` for  
    resources to be provisioned.

  - Once terraform has set up cloud resources, Ansible will run using terraform's  
    output to populate its inventory of virtual machines. Ansible will set up each  
    node to run Docker, including Docker Swarm, and will peform role-specific setup  
    on each VM. For example, the VM designated as the manager will start the swarm,  
    and nodes designated as workers will join it.

  - Once all the prerequisities are set up on the nodes, the Monarch stack will
    be deployed to the swarm using the `docker-compose.yml` file in `stack`.

### Configuration

**Note:** To deploy the Monarch stack, see [.secrets/README.md](.secrets/README.md) for details on how to obtain a service account keyfile and modify the Terraform config to use it.

There are three places where you'll likely be making changes to customize the
stack:
- `deployment/terraform.tfvars` — A terraform file of variable definitions that specifies, among other things:  
  - the name of the stack you’re setting up  
  - the environment that you're targeting (one of 'dev' or 'stable' at the moment)  
  - the VMs along with their metadata (e.g., the type of VM, like “e2-small”, its boot disk size, its role — worker or manager, and its services as a list of strings).  

  Note that these variables can be overridden by environment variables, if you find that more convenient.  
  See [Input Variables: Environment Variables](https://developer.hashicorp.com/terraform/language/values/variables#environment-variables) for details.  

- `stack/Makefile` — a Makefile that gets executed on each VM.  
  Currently, services are mapped to targets in this Makefile by the `deployment/ansible/setup_stack_app.yml` file.  
  Search for where the dict variable `service_to_maketarget` is specified,  
  then add your service name as the key and the target as the value.  
  Ostensibly, the target fetches data that the service depends on before it can start.  
  For example, `setup_solr` downloads and unpacks a database that Solr uses to initialize itself at first run.

- `stack/docker-compose.yml` — a docker compose file where you specify the containers you want to run and how they’ll be mapped to VMs

### Rolling updates to docker images

#### Updating the api

```

gcloud compute ssh --zone us-central1-a monarch-v3-${TF_VAR_env}-manager -- sudo docker service update monarch-v3_api --with-registry-auth  --update-order=start-first --force --image us-central1-docker.pkg.dev/monarch-initiative/monarch-api/monarch-api:${MONARCH_API_VERSION}
          
gcloud compute ssh --zone us-central1-a monarch-v3-${TF_VAR_env}-manager -- sudo docker service update monarch-v3_nginx --with-registry-auth  --update-order=start-first --force --image us-central1-docker.pkg.dev/monarch-initiative/monarch-api/monarch-ui:${MONARCH_API_VERSION}

```

For semsimian-server, you may need to look up the container tag, this assumes latest

```
gcloud compute ssh --zone us-central1-a monarch-v3-${TF_VAR_env}-manager -- sudo docker service update monarch-v3_semsim --with-registry-aut
h  --update-order=start-first --force --image us-central1-docker.pkg.dev/monarch-initiative/monarch-api/semsimian-server:latest 
```

to monitor the api deploy you may wish to watch:

```
gcloud compute ssh --zone us-central1-a monarch-v3-${TF_VAR_env}-api -- sudo docker stats
gcloud compute ssh --zone us-central1-a monarch-v3-${TF_VAR_env}-manager -- sudo docker service logs -n 1 -f monarch-v3_api 
```

#### Updating semsimian-server

Awkwardly get the latest tag from https://console.cloud.google.com/artifacts/docker/monarch-initiative/us-central1/monarch-api/semsimian-server?project=monarch-initiative

```
gcloud compute ssh --zone us-central1-a monarch-v3-${TF_VAR_env}-manager -- sudo docker service update monarch-v3_semsim --with-registry-auth  --update-order=start-first --force --image us-central1-docker.pkg.dev/monarch-initiative/monarch-api/semsimian-server:{tag}
```

##### Restarting semsimian-server

If semsimian-server has gotten itself into some kind of error state that is not being caught by the healthcheck (like if search is failing but compare is working), you can do a plain old turn it off and turn it back on again using:

```
gcloud compute ssh --zone us-central1-a monarch-v3-${TF_VAR_env}-manager -- sudo docker service update --force monarch-v3_semsim
```

(this command works to restart any other service as well)

#### Inspecting running containers

To check if environment variables are properly set in running containers, you can use these commands:

##### Check all environment variables in a specific container
```
gcloud compute ssh --zone us-central1-a monarch-v3-${TF_VAR_env}-manager -- sudo docker exec \$(sudo docker ps -q -f name=monarch-v3_api) env
```

##### Check for a specific environment variable (e.g., MONARCH_KG_VERSION)
```
gcloud compute ssh --zone us-central1-a monarch-v3-${TF_VAR_env}-manager -- sudo docker exec \$(sudo docker ps -q -f name=monarch-v3_api) env | grep MONARCH_KG_VERSION
```

##### Inspect the docker service configuration
```
gcloud compute ssh --zone us-central1-a monarch-v3-${TF_VAR_env}-manager -- sudo docker service inspect monarch-v3_api
```

These commands are useful for troubleshooting deployments and verifying that environment variables are correctly passed through the deployment pipeline.

#### Updating environment variables on running services

You can update environment variables on running services without redeploying the entire stack:

##### Update an environment variable (e.g., MONARCH_KG_VERSION) on both api and nginx services
```
gcloud compute ssh --zone us-central1-a monarch-v3-${TF_VAR_env}-manager -- sudo docker service update monarch-v3_api --env-add MONARCH_KG_VERSION=2025-07-15
gcloud compute ssh --zone us-central1-a monarch-v3-${TF_VAR_env}-manager -- sudo docker service update monarch-v3_nginx --env-add MONARCH_KG_VERSION=2025-07-15
```

##### Update all environment variables (MONARCH_KG_VERSION, MONARCH_API_VERSION, MONARCH_KG_SOURCE) on both api and nginx services
```
gcloud compute ssh --zone us-central1-a monarch-v3-${TF_VAR_env}-manager -- sudo docker service update monarch-v3_api --env-add MONARCH_KG_VERSION="${MONARCH_KG_VERSION}" --env-add MONARCH_API_VERSION="${MONARCH_API_VERSION}" --env-add MONARCH_KG_SOURCE="${MONARCH_KG_SOURCE}"
gcloud compute ssh --zone us-central1-a monarch-v3-${TF_VAR_env}-manager -- sudo docker service update monarch-v3_nginx --env-add MONARCH_KG_VERSION="${MONARCH_KG_VERSION}" --env-add MONARCH_API_VERSION="${MONARCH_API_VERSION}" --env-add MONARCH_KG_SOURCE="${MONARCH_KG_SOURCE}"
```

##### Force immediate restart with environment variable update
```
gcloud compute ssh --zone us-central1-a monarch-v3-${TF_VAR_env}-manager -- sudo docker service update --force monarch-v3_api --env-add MONARCH_KG_VERSION=2025-07-15
gcloud compute ssh --zone us-central1-a monarch-v3-${TF_VAR_env}-manager -- sudo docker service update --force monarch-v3_nginx --env-add MONARCH_KG_VERSION=2025-07-15
```

This triggers a rolling restart of the services with the new environment variable. Both api and nginx services need the environment variable (nginx can expose it via a version endpoint). The `--force` flag ensures an immediate restart even if Docker thinks no changes are needed.

#### Updating the KG

Solr needs a restart after running provision.sh to load fresh data on to the image: 

```
gcloud compute ssh --zone us-central1-a monarch-v3-${TF_VAR_env}-manager -- sudo docker service update --force monarch-v3_solr
```

#### What if I'm running provision.sh and see "No space left on device"

Time for some gardening, let's assume it's the api server:

```
gcloud compute ssh --zone us-central1-a monarch-v3-${TF_VAR_env}-api -- sudo docker system prune
```

Then re-run provision.sh

#### What if I want to teardown a stack and not bring it back up?

-d: Destroy

```
./provision.sh -d 
```

## Interesting/Useful Facts
### How Resource Prefixes Are Derived

In order to keep resources created by this stack from clashing with existing
resources, a prefix is used to implicitly namespace the resources on Google
Cloud.

The terraform variables `stack` and `env` together form the prefix that is
prepended to the name of all the resources created by terraform. Specifically,
`stack`, `env`, and the name of the resource are joined by hyphens to construct
the full name of the resource. For example, if stack was `monarch-v3` and `env`
was `dev` (both of which are the default values), the manager VM, whose name is
`manager`, would ultimately be named `monarch-v3-dev-manager` (you can look at 
the code which defines these [here](https://github.com/monarch-initiative/monarch-stack-v3/blob/ef2105772385f698e6e65bfa2c1f06e13c3bc539/deployment/terraform/config.tf#L75-L94)).
