# nmdc-orcid-creditor

NMDC ORCID Creditor is a web app NMDC team members can use to offer credits to people that contribute to the project;
and which those people can use to claim those credits—applying them to their ORCID profiles.

## Development

### Quick start

1. Create and customize your `.env` file.
   ```shell
   cp .env.example .env
   ```
2. Spin up the containerized development environment.
   ```shell
   docker compose up --detach
   ```
3. Visit the development server at: http://127.0.0.1:8000
    - API docs are at: http://127.0.0.1:8000/docs

### Common tasks

#### Outside the container

- View the container's logs:
   ```shell
   docker compose logs -f app
   ```
- Access the container's shell:
   ```shell
   docker compose exec app bash
   ```

#### Inside the container

You can run the following commands inside the container (i.e. at the container's shell).

> Alternatively, if you prepend `docker compose exec app ` to any of them, you will be able to run it from outside the
> container.

- Run tests:
  ```sh
  poetry run pytest
  
  # From outside the container:
  # $ docker compose exec app poetry run pytest
  ```
- Format Python code:
  ```sh
  poetry run black .
  
  # From outside the container:
  # $ docker compose exec app poetry run black .
  ```
- Format and lint Jinja2 templates:
  ```sh
  poetry run djlint --reformat --lint .
  
  # From outside the container:
  # $ docker compose exec app poetry run djlint --reformat --lint .
  ```
- Format JavaScript files (if you have [Node.js and NPM](https://nodejs.org/en/download/prebuilt-installer) installed):
  ```sh
  npx --yes prettier --write nmdc-orcid-creditor-proxy/*.js
  
  # From outside the container:
  # $ docker compose exec app npx --yes prettier --write nmdc-orcid-creditor-proxy/*.js
  ```

### Repository structure

Here's where you can find certain things within the repository:

- `nmdc-orcid-creditor-proxy/`: Google Apps Script
- `nmdc_orcid_creditor/`: FastAPI app
- `nmdc_orcid_creditor/templates/`: Jinja2 templates used by the FastAPI app
- `static/`: Static files served by the FastAPI app

## References

- We copied `static/favicon.png` and some brand color codes from
  the [nmdc-field-notes](https://github.com/microbiomedata/nmdc-field-notes/blob/main/public/favicon.png) repository
- We downloaded `static/undraw_online_resume_re_ru7s.svg` from [unDraw](https://undraw.co/license)
