## run locally, on the host, without Docker
```shell
uvicorn app.main:app --host 0.0.0.0 --port 80  --reload
```

The Swagger UI is available at http://localhost/docs or http://localhost/redoc  
0.0.0.0 or 127.0.0.1 can be used instead of `localhost` hostname

## build
```shell
docker build -t nmdc-utils-image:latest .
```

## run
```shell
docker run --name nmdc-utils-container -p 80:80 nmdc-utils-image:latest
```

## optionally save as an image archive
```shell
docker save usage_diff_image -o usage_diff_image.tar
```

## establish a connection between AWS and Docker
```shell
aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws/c1r1e2u3
```

## build tag and push
requires some setup within AWS ECR ans ECS 
```shell
docker build -t nmdc-utils-image:latest .
docker tag nmdc-utils-image:latest public.ecr.aws/c1r1e2u3/nmdc-utils-repository:latest
docker push public.ecr.aws/c1r1e2u3/nmdc-utils-repository:latest
```

## tell ECS to use the latest ECR push in the cluster? service? task?
this will change the endpoint's IP address, so clients will need to be updated
```shell
aws ecs update-service --cluster nmdc-utils-cluster --service nmdc-utils-service --force-new-deployment
```

