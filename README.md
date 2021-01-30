## Basic install and other useful commands

    ## Install package for Alembic

	git clone https://github.com/dmarx/checkin.git
	cd checkin
	conda create -f environment.yml # somethign like that...
	conda activate checkin
	pip install -e .

	# make changes to database structure

	alembic revision --autogenerate -m "updating database..."
	alembic upgrade head

	# kick off application

	cd checkin # we're now in ~/checkin/checkin
	nohup uvicorn api:app --host 0.0.0.0 8081 &