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

venv:
	python3 -m venv .venv
	. .venv/bin/activate

pip-install:
	pip install -r requirements.txt
