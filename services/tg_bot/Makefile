SERVICE_IMAGE_NAME = registry.gitlab.com/alex925/serial-notifier-web/tg-bot
DOCKER_COMPOSE_PROD = -f docker-compose.yml -f docker-compose.prod.yml

build-base-img:
	cd ../.. \
	&& docker build \
		-f ./services/tg_bot/base.Dockerfile \
		-t $SERVICE_IMAGE_NAME:base .

push-base-img:
	docker push $SERVICE_IMAGE_NAME:base

build-dev-app-img:
	# Образ собирается с тегом master потому, что в проекте не используется ветка develop и все фичи сразу идут в master
	cd ../.. \
	&& docker build \
		--build-arg CURRENT_ENV=dev \
		-f ./services/tg_bot/Dockerfile \
		-t $SERVICE_IMAGE_NAME:master .


run-dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up


run:
	docker-compose ${DOCKER_COMPOSE_PROD} -d

ps:
	docker-compose ${DOCKER_COMPOSE_PROD} ps

stop:
	docker-compose ${DOCKER_COMPOSE_PROD} -f docker-compose.dev.yml stop
