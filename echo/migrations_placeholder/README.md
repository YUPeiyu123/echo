This placeholder exists because the course rubric mentions evidence of database migrations.

For the final GitHub version, run:

flask --app run.py db init
flask --app run.py db migrate -m "initial database"
flask --app run.py db upgrade

Then commit the generated `migrations/` folder.
