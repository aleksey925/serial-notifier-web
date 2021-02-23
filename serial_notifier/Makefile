DOCKER_COMPOSE_PROD = -f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.override.yml
AUTOFLAKE_EXCLUDE = .git,venv,volumes


build-base-img:
	cd .. \
	&& docker build \
		-f ./serial_notifier/conf_files/docker/base.Dockerfile \
		-t registry.gitlab.com/alex925/serial-notifier-web/app:base .

push-base-img:
	docker push registry.gitlab.com/alex925/serial-notifier-web/app:base

build-dev-app-img:
	cd .. \
	&& docker build \
		-f ./serial_notifier/conf_files/docker/Dockerfile \
		--build-arg CURRENT_ENV=dev \
		-t registry.gitlab.com/alex925/serial-notifier-web/app:develop .


run-dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up


run:
	docker-compose ${DOCKER_COMPOSE_PROD} up -d

ps:
	docker-compose ${DOCKER_COMPOSE_PROD} ps

stop:
	docker-compose ${DOCKER_COMPOSE_PROD} -f docker-compose.dev.yml stop


beauty_check:
	flake8 --count && \
	autoflake \
		-r \
		--remove-all-unused-imports \
		--ignore-init-module-imports \
		--exclude=${AUTOFLAKE_EXCLUDE} . && \
	isort --diff . && \
	black --diff .

beautify:
	autoflake \
		-r \
		--in-place \
		--remove-all-unused-imports \
		--ignore-init-module-imports \
		--exclude=${AUTOFLAKE_EXCLUDE} . && \
	isort . && \
	black .
