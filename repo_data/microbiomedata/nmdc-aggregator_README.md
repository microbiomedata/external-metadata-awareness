# Aggregation Scripts

These scripts generate the KEGG/COG/Pfam aggregations that are used for search.

A container hosted on Spin runs the `agg.sh` script, which performs the aggregations periodically (once every 4 hours, by default).

> [!NOTE]
> The container image is hosted [here](https://github.com/microbiomedata/nmdc-aggregator/pkgs/container/nmdc-aggregator).

## Development

Here's how you can set up a local development environment:

> Unless otherwise specified, all commands below are designed to be run from the root directory of the repository.

> [!NOTE]
> These instructions do not cover the process of setting up a local MongoDB server or getting access to the NERSC filesystem.

1. Create and activate a Python virtual environment
   ```shell
   python -m venv ./.venv
   source ./.venv/bin/activate
   ```
2. Install Python dependencies
   ```shell
   pip install -r requirements.txt
   ```
3. Done

### Testing

We use [pytest](https://docs.pytest.org/en/stable/index.html) as our test framework.

Here's how you can run the tests:

> Unless otherwise specified, all commands below are designed to be run from the root directory of the repository.

1. Run the tests
   ```shell
   pytest --doctest-modules
   ```
   > The `--doctest-modules` option tells pytest that we want it to also find and run doctests defined in our modules.
2. See the test results in the console

## Deployment

Here's how you can build a new version of the container image and push it to the [GitHub Container Registry](https://github.com/microbiomedata/nmdc-aggregator/pkgs/container/nmdc-aggregator):

1. On GitHub, create a new Release.
    1. Create a tag.
       - Use "[`v{major}.{minor}.{patch}`](https://semver.org/)" format (e.g. "`v1.2.3`").
    2. Click the "Generate release notes" button.
    3. Leave the Release title empty (so GitHub reuses the tag name as the Release title).
    4. Click the "Publish release" button.
2. Wait 3-4 minutes for the container image to appear on the [GitHub Container Registry](https://github.com/microbiomedata/nmdc-aggregator/pkgs/container/nmdc-aggregator).
   > Taking a long time? Check the "Actions" tab on GitHub to see the status of the GitHub Actions workflow that builds the image.

Now that the container image is hosted there, you can configure a Spin workload to run it.

## Configuration

### Environment variables

- `LOG_FILE`: Path to file to which logs will be appended (Default: `/tmp/agg.log`)
- `POLL_TIME`: Number of seconds to sleep between each run (Default: `14400`, which is 4 hours)
- `NMDC_CLIENT_ID`: Client ID for interacting with NMDC's runtime API
- `NMDC_CLIENT_PW`: Password for interacting with NMDC's runtime API
- `ENV`: Whether to run the scripts in the production or development runtime environment. Options are "prod" or "dev".

## Release Notes

https://github.com/microbiomedata/nmdc-aggregator/releases
