docker build --tag cuda121:latest .

docker run -it --gpus all cuda121:latest bash
