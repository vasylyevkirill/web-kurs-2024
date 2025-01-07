# BACKEND TAXI PROJECT

PROJECT CONFIGURATION IN .env FILE

### Start project
```
docker compose up
```

### Stop project
```
docker compose down
```

### Parse sql dump file
```
docker compose exec -iT db psql -U taxi dev < dumpfile.sql
```
