build-base-img:
	docker build -f ./base.Dockerfile -t serial-notifier-web:base .

build-dev-app-img:
	docker build --build-arg CURRENT_ENV=dev -t serial-notifier-web:develop .



run-dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up



run:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

stop:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml -f docker-compose.prod.yml stop
