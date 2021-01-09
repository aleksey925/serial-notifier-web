build-base-img:
	docker build \
		-f ./conf_files/docker/base.Dockerfile \
		-t registry.gitlab.com/alex925/serial-notifier-web/app:base .

build-dev-app-img:
	docker build \
		-f ./conf_files/docker/Dockerfile \
		--build-arg CURRENT_ENV=dev \
		-t registry.gitlab.com/alex925/serial-notifier-web/app:develop .


run-dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up


run:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.override.yml up -d

ps:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.override.yml ps

stop:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml -f docker-compose.prod.yml -f docker-compose.override.yml stop
