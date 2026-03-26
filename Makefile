server-restart: stop start

start:
	docker compose up -d

stop:
	docker compose down -v --remove-orphans

down:
	docker compose down --remove-orphans

docker-up:
	docker compose up -d

docker-build:
	docker compose build --pull

docker-pull:
	docker compose pull
