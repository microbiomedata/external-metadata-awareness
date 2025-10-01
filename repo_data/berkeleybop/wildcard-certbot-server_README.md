# wildcard-certbot-server

The wildcard certbot server manages SSL certificates and private keys for Route53 DNS Zones.
It uses the Route53 DNS handshake to communicate with letsencrypt and an S3 bucket as a certificate store.
<b>It is important to note that there can only be one of these certificate manager per S3 bucket and per DNS Zones.</b>

- Downloads Certificates/Keys from S3 bucket during staging.
- Installs a cron job to renew Certificates when needed and uploads them to S3 bucket.
- Provides a playbook to generate certificates and uploads them to S3 bucket.
- Provides a playbook to revoke certificates and deletes them from S3 bucket.

## Requirements
- Terraform. Tested using v1.1.4
- Ansible. Tested using version 2.10.7
- Python. <b>Use version 3.8 or higher</b>
- go-deploy. 0.4.1 or higher.
- aws cli Optional. Used to test aws credentials

## Development Environment

<b>We have a docker based dev environment with all these tools installed.</b> See last section of this README (Appendix I: Development Environment).

The instructions in this document are run from the POV that we're working with this developement environment; i.e.:
```
docker run  -v `pwd`:'/work' -w /work --rm --name go-dev -it go-dev /bin/bash
```

## Install Python deployment Script
The go-deploy is a simple wrapper for both `terraform` and `ansible` commands

Note the `go-deploy`script has a <b>-dry-run</b> option. You can always copy the command and execute it manually

```
pip install go-deploy==0.4.1 # <b>requires python >=3.8</b>
go-deploy -h
```

## DNS Plugin/AWS Credentials

The wildcard certbot server uses the DNS plugin to prove to letsencrypt that it owns the DNS Zones.
And so you need to make sure that the AWS credentials you use have the necessary permissions.

## SSH Keys
Please ask for the <i>production ssh keys</i> and place them in the default locations. `/tmp/go-ssh` for the private key and `/tmp/go-ssh.pub` for the public key. See Appendix I at the bottom for more details.

```
cat /tmp/go-ssh
cat /tmp/go-ssh.pub

chown root /tmp/go-ssh*
chgrp root /tmp/go-ssh*

# Make sure the private key and the public key match; the following command should return nothing
diff <( ssh-keygen -y -e -f /tmp/go-ssh ) <( ssh-keygen -y -e -f /tmp/go-ssh.pub )
```

## Prepare The AWS Credentials

The credentials are need by terraform to provision the AWS instance and are used by the provisioned instance to access the s3 bucket used as a certificate store. One could also copy in from an existing credential set, see Appendix I at the end for more details.

- [ ] Copy and modify the aws credential file to the default location `/tmp/go-aws-credentials` <br/>`cp configs/go-aws-credentials.sample /tmp/go-aws-credentials`
- [ ] You will need to supply an `aws_access_key_id` and `aws_secret_access_key`. These will be marked with `REPLACE_ME`.

```
# Use the aws cli to make sure you have access to the s3 buckets `go-service-lockbox`
# and `go-workspace-certbot-server`

export AWS_SHARED_CREDENTIALS_FILE=/tmp/go-aws-credentials
aws s3 ls s3://go-service-lockbox # S3 bucket used as a certificate store
aws s3 ls s3://go-workspace-certbot-server # S3 bucket Used for terraform backend.
```

## Prepare And Initialize The S3 Terraform Backend

The S3 backend is used to store the terraform state.

Check list:
- [ ] Assumes you have prepared the aws credentials above.
- [ ] Copy the backend sample file <br/>`cp ./configs/backend.tf.sample ./aws/backend.tf`
- [ ] Initialize the backend <br/>`cat ./aws/backend.tf && go-deploy -init --working-directory aws -verbose`

## Workspace Name

Use these commands to figure out the name of an existing workspace if any. The name should have a pattern `production-YYYY-MM-DD`

Check list:

- [ ] Assumes you have initialized the backend. See above
```
go-deploy --working-directory aws -list-workspaces -verbose
```
## Provision Instance on AWS

We only need to provision the AWS instance once. This is because we
only want one instance to manage the wildcard certificates. Use the
terraform commands shown above to figure out the name of an existing
workspace. If such workspace exists, then you can skip the
provisionning of the aws instance. Or you can destroy the aws instance
and re-provision if that is the intent.

Check list:
- [ ] <b>Choose your workspace name. We use the following pattern `production-YYYY-MM-DD`</b>. For example: `production-2022-10-18`.
- [ ] Copy `configs/config-instance.yaml.sample` to another location and modify using vim or emacs.
- [ ] Verify the location of the ssh keys for your AWS instance in your copy of `config-instance.yaml` under `ssh_keys`.
- [ ] Verify location of the public ssh key in `aws/main.tf`
- [ ] Remember you can use the -dry-run option to test "go-deploy"
- [ ] Execute the command set right below in "Command set".
- [ ] Note down the ip address of the aws instance that is created. This can also be found in production-YYYY-MM-DD.cfg

<b>Command set</b>:
```
cp ./configs/config-instance.yaml.sample config-instance.yaml
cat ./config-instance.yaml   # Verify contents and modify if needed.
go-deploy --workspace production-YYYY-MM-DD --working-directory aws -verbose --conf config-instance.yaml

# The previous command creates a terraform tfvars. These variables override the variables in `aws/main.tf`
cat production-YYYY-MM-DD.json

# Useful terraform commands to check what you have just done using the `-var-file` option
terraform -chdir=aws workspace show -var-file=production-YYYY-MM-DD.tfvars.json  # current terraform workspace
terraform -chdir=aws show -var-file=production-YYYY-MM-DD.tfvars.json            # current state deployed ...
terraform -chdir=aws output -var-file=production-YYYY-MM-DD.tfvars.json          # public ip of aws instance

# These commands should also work if the credential file and the public ssh key in `aws/main.tf`
# point to the right locations.
terraform -chdir=aws workspace show  # current terraform workspace
terraform -chdir=aws show            # current state deployed ...
terraform -chdir=aws output          # public ip of aws instance
```

## Deploy

- Builds docker image, copies artifacts, scripts ..., installs crontab
- Downloads certs and then calls renew ...

Check list:
- [ ] Copy `configs/config-stack.yaml.sample` to another location and modify using vim or emacs.
- [ ] Verify the location of the ssh keys for your AWS instance in your copy of `config-stack.yaml` under `ssh_keys`.
- [ ] Verify location of the public ssh key in `aws/main.tf`
- [ ] Verify the name of S3 bucket (certstore) in your copy of `config-stack.yaml` under `S3_SSL_CERTS_BUCKET`
- [ ] Verify the location of aws credentials in your copy of `config-stack.yaml` under `S3_SSL_CRED_FILE`
- [ ] </b>Use the correct terraform workspace</b>.
- [ ] Remember you can use the -dry-run option
- [ ] Execute the command set right below in "Command set".

<b>Command set</b>:

```
cp ./configs/config-stack.yaml.sample ./config-stack.yaml
cat ./config-stack.yaml    # Verify contents and modify if needed.
export ANSIBLE_HOST_KEY_CHECKING=False
go-deploy --workspace production-YYYY-MM-DD --working-directory aws -verbose --conf config-stack.yaml
```

## Generate Wildcard Certificate

This will generate a wildcard certificate/keys for some `domain` and upload them to s3 bucket certstore.

Check list:
- [ ] Assumes staging has been done.
- [ ] Copy `configs/config-gencert.yaml.sample` to another location and modify using vim or emacs.
- [ ] Verify the location of the ssh keys for your AWS instance in your copy of `config-gencert.yaml` under `ssh_keys`.
- [ ] Verify location of the public ssh key in `aws/main.tf`
- [ ] <b>Specify the domain.</b> Example: geneontology.io
- [ ] <b>Specify the emails.</b> Comma seperated emails
- [ ] </b>Use the correct terraform workspace</b>.
- [ ] Remember you can use the -dry-run option
- [ ] Execute the command set right below in "Command set".

<b>Command set</b>:

```
cp ./configs/config-gencert.yaml.sample config-gencert.yaml
cat ./config-gencert.yaml   # Verify contents and modify as needed. (domain/email)
go-deploy --workspace production-YYYY-MM-DD --working-directory aws -verbose --conf config-gencert.yaml
```

## Revoking Wildcard Certificate

This will revoke a wildcard certificate/keys for some `domain` and remove them from s3 bucket certstore.

Check list:
- [ ] Assumes staging has been done.
- [ ] Copy `configs/config-gencert.yaml.sample` to another location and modify using vim or emacs.
- [ ] Verify the location of the ssh keys for your AWS instance in your copy of `config-gencert.yaml` under `ssh_keys`.
- [ ] Verify location of the public ssh key in `aws/main.tf`
- [ ] <b>Specify the domain.</b> Example: geneontology.io
- [ ] </b>Use the correct terraform workspace</b>.
- [ ] Remember you can use the -dry-run option
- [ ] Execute the command set right below in "Command set".

<b>Command set</b>:

```
cp ./configs/config-revokecert.yaml.sample config-revokecert.yaml
cat ./config-revokecert.yaml   # Verify contents and modify `domain` as needed.
go-deploy --workspace production-YYYY-MM-DD --working-directory aws -verbose --conf config-revokecert.yaml
```

## Debugging/Testing

- Use -dry-run and copy and paste the command and execute it manually

- ssh to machine using ssh private key. Username is ubuntu
  - docker image list  # should show the image aws-certbot
  - sudo cat /root/.aws/config  # shoud show AWS credentials to access s3 bucket certificate store
  - ls stage_dir/certs  # should show directories for each zone
  - sudo find stage_dir/certs -name fullchain.pem
  - sudo find stage_dir/certs -name privkey.pem
  - crontab -l   # shoud show the crontab for cert renewal. Run the command to test renewal script.

## Destroy Instance and Delete Workspace.

```sh
# Make sure you pointing to the correct workspace before destroying the stack.
terraform -chdir=aws workspace list
terraform -chdir=aws workspace select <name_of_workspace>
terraform -chdir=aws workspace show # shows the name of current workspace
terraform -chdir=aws show           # shows the state you are about to destroy
terraform -chdir=aws destroy        # You would need to type Yes to approve.

# Now delete workspace.
terraform -chdir=aws workspace select default # change to default workspace
terraform -chdir=aws workspace delete <name_of_workspace>  # delete workspace.
```

## Appendix I: Development Environment

Build docker image using docker/Dockerfile.dev. This image is based on `go-devops-base:tools-jammy-0.4.1`
meaning ubuntu 22.04 (jammy) and go-deploy-0.4.1. In addition to go-deploy it has aws, terraform and ansible
tools installed.

```
# Build image which will contain this repo under /tmp. See docker/Dockerfile.dev
git clone https://github.com/berkeleybop/wildcard-certbot-server.git
cd wildcard-certbot-server
docker build -f docker/Dockerfile.dev -t go-dev .

# Start docker container `go-dev` in interactive mode.
docker run --rm --name go-dev -it go-dev /bin/bash

# In the command above we used the `--rm` option which means the container will be deleted when you exit. If that is not
# the intent and you want delete it later at your own convenience. Use the following `docker run` command.

docker run --name go-dev -it go-dev /bin/bash

# Exit or stop the container.
docker stop go-dev  # stop container with the intent of restarting it. This equivalent to `exit` inside the container

docker start -ia go-dev  # restart and attach to the container
docker rm -f go-dev # get rid of it for good when ready.
```

SSH/AWS Credentials:

Use `docker cp` to copy these credentials to /tmp. You can also copy and paste using your favorite editor vim or emacs.

Under /tmp you would need the following:

- /tmp/go-aws-credentials
- /tmp/go-ssh
- /tmp/go-ssh.pub

```
# Example using `docker cp` to copy files from host to docker container named `go-dev`

docker cp <path_on_host> go-dev:/tmp/
```

Then, within the docker image:

```
chown root /tmp/go-*
chgrp root /tmp/go-*
```
