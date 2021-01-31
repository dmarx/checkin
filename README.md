## Basic install and other useful commands

    ## Install package for Alembic

	git clone https://github.com/dmarx/checkin.git
	cd checkin
	#conda create -f environment.yml # somethign like that...
	#conda activate checkin
	python -m venv env/env_ci
	source env/env_ci/bin/activate
	pip install -e .

	# make changes to database structure

	alembic revision --autogenerate -m "updating database..."
	alembic upgrade head

	# kick off application

	cd checkin # we're now in ~/checkin/checkin
	nohup uvicorn api:app --host 0.0.0.0 8081 &
	
	# Stop application for restart
	ps -aux | grep uvicorn
	pgrep uvicorn | xargs kill
	
	# Incorporate changes and restart
	scp .. # backup database locally
	ssh .. # remote into host
	pgrep uvicorn | xargs kill
	cd checkin
	git pull origin
	alembic upgrade head
	cd checkin
	nohup uvicorn api:app --host 0.0.0.0 8081 &
	
	