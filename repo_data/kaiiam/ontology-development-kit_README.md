# ontology-development-kit

[![Build Status](https://travis-ci.org/INCATools/ontology-development-kit.svg?branch=master)](https://travis-ci.org/INCATools/ontology-development-kit)

Initialize a GitHub repo for managing your ontology the OBO Library way!

For more details, see

 * [2018 Article](https://douroucouli.wordpress.com/2018/08/06/new-version-of-ontology-development-kit-now-with-docker-support/)
 * [ICBO Workshop Slides 2018](https://docs.google.com/presentation/d/1nIybviEEJiRKHO2rkBMZsQ0QjtsHyU01_-9beZqD_Z4/edit?usp=sharing)
 * [ICBO Workshop Slides 2017](https://docs.google.com/presentation/d/1JPAaDl6Nitxet9NVqWI30eIygcerYAjdMIGmxbRtIn0/edit?usp=sharing)

# Instructions: Create a new ontology project

We will walk you though the steps to make a new ontology project

## 1. Install and Start Docker

 * [docker](https://www.docker.com/get-docker)

See below for an alternative protocol where you install the software yourself rather than use Docker

## 2. Download the wrapper script and pull latest ODK version

 * Linux/Mac: [seed-via-docker.sh](https://raw.githubusercontent.com/INCATools/ontology-development-kit/master/seed-via-docker.sh)
 * PC: [seed-via-docker.bat](https://raw.githubusercontent.com/INCATools/ontology-development-kit/master/seed-via-docker.bat)
 * First, make sure you have Docker running (you will see the Docker whale in your toolbar on a Mac)
 * To make sure you have the latest version of the ODK installed, run in the command line 

    `docker pull obolibrary/odkfull`

**NOTE** The very first time you run this it may be slow, while docker downloads necessary images. Don't worry, subsequent runs should be much faster!

## 3. Run the wrapper script

You can either pass in a `project.yaml` file that specifies your ontology project setup, or you can pass arguments on the command line.

Passing arguments on the command line:

    ./seed-via-docker.sh   -d po ro pato -u cmungall -t "Triffid Behavior ontology" triffo

Using a the predefined [examples/triffo/project.yaml](examples/triffo/project.yaml) file:

    ./seed-via-docker.sh -C examples/triffo/project.yaml

You can add a -c (lowercase) just before the -C (capital c) in the command to first delete any previous attempt to generate your ontology with the ODK, and then replaces it with a completely new one.

This will create your starter files in
`target/triffid-behavior-ontology`. It will also prepare an initial
release and initialize a local repository (not yet pushed to GitHub).

You can customize at this stage, or (recommended) after making an initial push to github

## 4. Push to GitHub

The development kit will automatically initialize a git project, add all files and commit.

You will need to create a project on GitHub.

 1. Go to: https://github.com/new
 2. The owner MUST be the org you selected with the `-u` option. The name MUST be the one you set with `-t`.
 3. Do not initialize with a README (you already have one)
 4. Click Create
 5. See the section under "…or push an existing repository from the command line"

Follow the instructions there. E.g.

```
cd target/triffid-behavior-ontology
git remote add origin git@github.com:cmungall/triffid-behavior-ontology.git
git push -u origin master
```

Note: you can now mv `target/triffid-behavior-ontology` to anywhere you like in your home directory. Or you can do a fresh checkout from github

## Next Steps: Edit and release cycle

In your repo you will see a README-editors.md file that has been customized for your project. Follow these instructions.

Generally the cycle is to:

 - branch
 - the edit the edit.owl file
 - make test
 - git commit
 - git push

To make a release

`make prepare_release`

Note that any make step can be preceded by run.sh if you have Docker installed

## OBO Library metadata

The assumption here is that you are ahdering to OBO principles and
want to eventually submit to OBO. Your repo will contain stub metadata
files to help you do this.

You can create pull requests for your ontology on the OBO Foundry. See the `src/metadata` file for more details.

For more documentation, see http://obofoundry.org

## Additional

You will want to also:

 * enable travis
 * enable zenodo (optional)

See the README-editors.md file that has been generated for your project.

## Troubleshooting.

If you have issues, file them here: https://github.com/INCATools/ontology-development-kit/issues

Some things to check:

 * if something goes wrong you can try again. You may want to remove the `target` dir, or use the `-c` option
 * make sure your ontid has no spaces
 * if your title has spaces, enclose it in quotes


## Customizing

You will likely want to customize the build process, and of course to edit the ontology.

We recommend that you do not edit the main Makefile, but instead the supplemental one (e.g. myont.Makefile) is src/ontology

## Regenerating configuration files in an existing project

DOCUMENTATION TODO

You can recreate the Makefile by running `odk.py create_makefile -C project.yaml`

## Adapting an existing ontology repo

The ODK is designed for creating a new repo for a new ontology. It can still be used to help figure out how to migrate an existing github repository to the ODK structure. There are different ways to do this.

 * Manually compare your ontology against the [template](https://github.com/INCATools/ontology-development-kit/tree/master/template) folder and make necessary adjustments
 * Run the seed script as if creating a new repo. Manually compare this with your existing repo and use `git mv` to rearrange, and adding any missing files by copying them across and doing a `git add`
 * Create a new repo de novo and abandon your existing one, using github issue mover to move tickets across.
 
Obviously the second method is not ideal as you lose your github history. Note even with `git mv` history tracking becomes harder

If you have built your ontology using a previous version of ODK,
migration of your setup is unfortunately a manual process. In general
you do not absolutely *need* to upgrade your setup, but doing so will
bring advantages in terms of aligning with emerging standards ways of
doing things. The less customization you do on your repo the easier it
should be to migrate.

Consult the [Changes.md](Changes.md) file for changes made between
releases to assist in upgrading.

## More documentation

You will find additional documentation in the src/ontology/README-editors.md file in your repo

## Alterantive to Docker

You can run the seed script without docker, you will need Python3.6 or
higher and Java. See requirements.txt for python requirements.
