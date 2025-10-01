# ols-embassy
Jupyter notebook describing steps to set up a custom instance of OLS on EMBL/EBI Embassy Cloud.

To run the latest version of this notebook on your local machine, if you have docker installed, you can simply pull down the latest image and run it. To do so, enter the following command from your shell (e.g. bash):

**```bash#```**```docker pull wjread/ols-embassy-jupyter```

Once the image is safely downloaded, try running it in detached mode (to serve Jupyter on its default port of 8888):

**```bash#```**```docker run -p 8888:8888 -d wjread/ols-embassy-jupyter```

When you are returned to the prompt, check that you can see Jupyter in your browser on http://localhost:8888; if it's running, you'll be getting prompted for a password or token. You need to retrieve this from your running container. Return to your shell prompt:

**```bash#```**```docker ps```

Make a note of the Juypter container id and then attach your terminal to it interactively:

**```bash#```**```docker exec -it```*```container_id```*```bash```

Once you have a prompt inside your container, you can query for the Jupyter token:

**```bash#```**```jupyter notebook list```

Copy and paste the (fairly long) token id from your terminal into your Jupyter browser window. In your browser window itself, click on "ols-embassy", then on "Custom OLS deployment on Embassy Cloud.ipynb". You can now follow the instructions therein to set your own customised instance, or instances, of OLS running on EMBL-EBI's Embassy Cloud IaaS (Infrastructure as a Service).
