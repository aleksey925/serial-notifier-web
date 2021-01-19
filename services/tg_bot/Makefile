build-base-img:
	cd ../.. \
	&& docker build \
		-f ./services/tg_bot/base.Dockerfile \
		-t registry.gitlab.com/alex925/serial-notifier-web/tg-bot:base .

push-base-img:
	docker push registry.gitlab.com/alex925/serial-notifier-web/tg-bot:base

build-dev-app-img:
	cd ../.. \
	&& docker build \
		--build-arg CURRENT_ENV=dev \
		-f ./services/tg_bot/Dockerfile \
		-t registry.gitlab.com/alex925/serial-notifier-web/tg-bot:develop .


run-dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up


run:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

ps:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps

stop:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml -f docker-compose.prod.yml stop
