#this makefile is designed to have limited windows compatability, not full. 
#Be cautious when using file under non-UNIX-like syntax as it may result in 
#undesired behaviour
ifeq ($(OS), Windows_NT)
	EXECUTE := py
	TOUCH := type nul >>
	RMRF := deltree
	PAUSE := echo
	ACTIVATE := $(./env/bin/activate)
else
	EXECUTE := python
	TOUCH := touch
	RMRF := rm -rf
	PAUSE := read -n 1 -p
	ACTIVATE := $(source env/bin/activate)
endif
MANAGE = $(EXECUTE) manage.py
MAKEMIGRATION = $(MANAGE) makemigrations


all: upgrade env deps makemigration_all migrate

env:
	@echo  --- generating virtual environment ---
	$(EXECUTE) -m venv --clear env
	$(ACTIVATE)

deps:
	@echo  --- installing dependencies ---
	python -m pip install --upgrade pip
	pip install -r requirements.txt

dev:
	@echo  --- making persistent files ---
	$(TOUCH) db.cnf
	$(TOUCH) abs_path.cnf


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
	$(MAKEMIGRATION) prepare
	$(MAKEMIGRATION) science
	$(MAKEMIGRATION) savemeplan
	$(MAKEMIGRATION) userprofile

make_pkg: full_clean
	git checkout production
	git pull
	tar -zcvf 12stepsapp-production-branch.tar.gz *

full_clean: clean
	$(RMRF) env
	$(RMRF) lang
	$(RMRF) conf/lang.out.json


clean:
	@echo  --- cleaning up ---
	$(RMRF) */migrations
	$(RMRF) */__pycache__
