ifeq ($(OS), Windows_NT)
	EXECUTE := py
	TOUCH := type nul >>
	RMRF := deltree
	PAUSE := set /P pausevar
else 
	EXECUTE := python
	TOUCH := touch
	RMRF := rm -rf
	PAUSE := read -n 1 -p 
endif
MANAGE = $(EXECUTE) manage.py
MAKEMIGRATION = $(MANAGE) makemigrations


all: upgrade env activate deps dev makemigration_all migrate 

env:
	@echo  --- generating virtual environment --- 
	$(EXECUTE) -m venv --clear env

activate:
	@echo  --- activating environment ---
	$(source /env/bin/activate)

deps:
	@echo  --- installing dependencies ---
	pip install --upgrade pip
	pip install -r requirements.txt

dev:
	@echo  --- making persistent files ---
	$(TOUCH) db.cnf
	$(TOUCH) abs_path.cnf
	$(PAUSE)"Verify your .cnf files are filled in properly!"

run:
	@echo  --- starting server ---
	$(MANAGE) runserver

upgrade:
	@echo  --- pulling updates from repo ---
	git pull

migrate:
	@echo  --- migrating database ---
	$(MANAGE) migrate

makemigration_all:
	@echo  --- making migrations ---
	$(MAKEMIGRATION) breathe
	$(MAKEMIGRATION) call
	$(MAKEMIGRATION) chat
	$(MAKEMIGRATION) check
	$(MAKEMIGRATION) check
	$(MAKEMIGRATION) danger
	$(MAKEMIGRATION) home
	$(MAKEMIGRATION) info
	$(MAKEMIGRATION) login
	$(MAKEMIGRATION) practice
#	$(MAKEMIGRATION) prepare
	$(MAKEMIGRATION) savemeplan

clean:
	@echo  --- cleaning up ---
	$(RMRF) env
	$(RMRF) */migrations
	$(RMRF) */__pycache__
	