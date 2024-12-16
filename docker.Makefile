.PHONY: temp

up:
	docker compose up -d

stop:
	docker compose stop

start:
	docker compose start

down:
	docker compose down # deletes volumes?!

build:
	docker compose build

shell:
	docker compose exec -it dev bash

