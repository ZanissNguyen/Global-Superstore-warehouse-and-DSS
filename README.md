# Window python venv setup

python -m .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Docker postgres database

Window require docker desktop

docker pull postgres
docker pull dpage/pgadmin4

docker compose up -d
docker compose down

curl http://localhost:5050
to open pgadmin, account and password see in docker-compose.yml