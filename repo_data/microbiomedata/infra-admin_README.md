# infra-admin

This private repository contains documentation, scripts, and other tools NMDC team members use to manage NMDC infrastructure.

## URLs

Here are URLs that people can use to access specific NMDC systems from the public Internet.

Also shown are hostname-port combinations people can use to access specific NMDC systems from within the NERSC network only.

### Development environment

This environment is used by NMDC team members to test things without impacting the production environment. It is hosted on Spin, in the `nmdc-dev` namespace.

#### Public Internet

- Submission portal: https://data-dev.microbiomedata.org/submission
- Data portal: https://data-dev.microbiomedata.org
- Data portal - Swagger UI: https://data-dev.microbiomedata.org/api/docs
- Runtime API - Swagger UI: https://api-dev.microbiomedata.org
- Dagit (Dagster UI): https://dagit-dev.microbiomedata.org _(password-protected)_
- NMDC EDGE: https://dev.nmdc-edge.org

#### NERSC Network only

- MongoDB server: `mongo-loadbalancer.nmdc-dev.production.svc.spin.nersc.org:27017`
- Data portal PostgreSQL server: `db-loadbalancer.nmdc-dev.production.svc.spin.nersc.org:5432`

### Production environment

This environment is used by the general public. It is hosted on Spin, in the `nmdc` namespace.

#### Public Internet

- Submission portal: https://data.microbiomedata.org/submission
- Data portal: https://data.microbiomedata.org
- Data portal - Swagger UI: https://data.microbiomedata.org/api/docs
- Runtime API - Swagger UI: https://api.microbiomedata.org
- Dagit (Dagster UI): https://dagit.microbiomedata.org _(password-protected)_
- NMDC EDGE: https://nmdc-edge.org/

#### NERSC Network only

- MongoDB server: `mongo-loadbalancer.nmdc.production.svc.spin.nersc.org:27017`
- Data portal PostgreSQL server: `db-loadbalancer.nmdc.production.svc.spin.nersc.org:5432`

### Documentation websites

- General: https://docs.microbiomedata.org
- NMDC Schema: https://microbiomedata.github.io/nmdc-schema

#### Obsolete documentation websites

- NMDC Documentation: https://nmdc-documentation.readthedocs.io (redirects to "General" site)
- NMDC Workflows documentation: https://nmdc-workflow-documentation.readthedocs.io (redirects to "General" site)
- NMDC Data Portal user guide: https://the-nmdc-portal-user-guide.readthedocs.io (redirects to "General" site)
- NMDC Runtime documentation: https://microbiomedata.github.io/nmdc-runtime (redirects to "General" site)

## Footnotes

Looking for the `aggregation` directory? On May 9, 2024, that directory and its contents were extracted from this repository and moved to the [microbiomedata/nmdc-aggregator](https://github.com/microbiomedata/nmdc-aggregator) repository.
