# Connecting to NMDC production MongoDB (jump-dev tunnel)

NMDC's production MongoDB runs inside a GCP Kubernetes cluster and is not
publicly reachable. Access goes through an SSH gateway,
`jump-dev.microbiomedata.org`, which forwards a local port into the cluster.
Once the gateway key is in place the tunnel is key-based and non-interactive.

This is the connection EMA tools use for realized prod biosamples, for example
`mixs-required-slot-report --weight-source env-package --refresh-weights`.

## One-time setup

1. Get the SSH gateway private key. It lives in NERSC project storage and is
   fetched once with your NERSC account. The authoritative steps are in
   [`nmdc-lakehouse/docs/mongodb-connection.md`](https://github.com/microbiomedata/nmdc-lakehouse/blob/main/docs/mongodb-connection.md);
   the result is `~/.ssh/jump-dev.microbiomedata.org.private_key` (`chmod 400`).
2. Get a personal MongoDB account on the NMDC prod instance (contact the NMDC
   infrastructure lead). Put the username and password in a git-ignored `.env`
   under one of the key pairs EMA tools read, in order:
   `MONGO_USER`/`MONGO_PASSWORD`, then `SOURCE_MONGO_USER`/`SOURCE_MONGO_PASS`,
   then `NMDC_MONGO_USER`/`NMDC_MONGO_PASSWORD`. Never commit the `.env`.

## Open the tunnel

```bash
ssh -i ~/.ssh/jump-dev.microbiomedata.org.private_key \
    -o IdentitiesOnly=yes \
    -L 27124:runtime-api-mongodb-headless.nmdc-prod.svc.cluster.local:27017 \
    -o ServerAliveInterval=60 \
    ssh-mongo@jump-dev.microbiomedata.org
```

That holds the tunnel open in the foreground (leave the terminal open). To run
it in the background instead, add `-f -N`. While it is up, `localhost:27124`
forwards to the prod MongoDB.

The gateway key authenticates on its own, so no NERSC password or OTP is needed
to open the tunnel once the key is present. NERSC credentials are only needed
for the one-time key fetch above.

## Connection parameters

| Setting | Value |
|---|---|
| Host / port | `localhost` / `27124` (the tunnel) |
| Database | `nmdc` |
| `authSource` | `admin` |
| `directConnection` | `true` (required: the replica-set members advertise internal Kubernetes hostnames) |

URI shape (credentials injected from your `.env`, never committed):

```
mongodb://<user>:<password>@localhost:27124/nmdc?authSource=admin&directConnection=true
```

## Verify

```bash
mongosh "mongodb://localhost:27124/nmdc?authSource=admin&directConnection=true" \
    --username "<your-mongo-username>" --password \
    --eval 'db.biosample_set.estimatedDocumentCount()'
```

## Read-only alternative (no tunnel)

For read-only aggregate queries you do not need the tunnel at all: the
prod-backed public API serves the same records. For example, biosample
`env_package` values (the basis for the `env-package` weights) come from:

```
https://api.microbiomedata.org/nmdcschema/biosample_set?max_page_size=999999&projection=env_package
```

Use the tunnel when you need direct MongoDB access (aggregation pipelines,
collections the API does not expose, or write access).

## Use from the report tool

With the tunnel up and `--env-file` pointing at your git-ignored `.env`:

```bash
mixs-required-slot-report \
    --weight-source env-package --refresh-weights \
    --env-file local/.env \
    -o local/mixs_required_slot_report.tsv
```

Without `--refresh-weights`, the tool uses a baked-in snapshot of these weights
and needs no tunnel.

## Tear down

The tunnel closes when its terminal exits. For a backgrounded (`-f -N`) tunnel:

```bash
pkill -f '27124:runtime-api-mongodb-headless'
```

## See also

- [`nmdc-lakehouse/docs/mongodb-connection.md`](https://github.com/microbiomedata/nmdc-lakehouse/blob/main/docs/mongodb-connection.md):
  authoritative source for the one-time gateway-key fetch from NERSC.
- `infra-admin/mongodb/connection-guide.md` documents an older NERSC-Spin
  access path and predates this GCP gateway. Prefer the steps here for the
  GCP-hosted prod instance.
