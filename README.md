# Installation & Usage

You will need install docker-compose

## Build container
```bash
sudo docker-compose build
```

## Run service
```bash
sudo docker-compose up
```

# Installing from scratch

git checkout review # current working branch
mkvirtualenv -p $(which python3) notoi
pip install -r requirements.txt
createdb notoi
cat > config/settings/config.yaml <<EOF
databases:
  develop:
    name: notoi
    host:
    port:
    user:
    password:
  prod:
    name: name
    host: host
    port: 5432
    user: user
    password: password

whitelist:
  prod:
  - "http://notoi.somenergia.coop"
  develop:
  - "http://localhost:8080"
  - "http://127.0.0.1:9000"
EOF
./manage migrate
./manage test
./manage runserver




