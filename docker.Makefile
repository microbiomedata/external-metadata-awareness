.PHONY: up stop start down build shell all

up:
	docker compose up -d

stop:
	docker compose stop

start:
	docker compose start

down:
	docker compose down # deletes volumes

build:
	docker compose build --no-cache

shell:
	docker compose exec -it dev bash

all: down build up
