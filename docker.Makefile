.PHONY: temp

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

shell:
	docker compose exec -it dev bash

