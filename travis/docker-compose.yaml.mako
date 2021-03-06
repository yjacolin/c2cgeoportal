---
# A compose file for development.
version: '2'
services:
  db:
    image: camptocamp/testgeomapfish-testdb:latest
    environment:
      POSTGRES_USER: www-data
      POSTGRES_PASSWORD: www-data
      POSTGRES_DB: geomapfish

  external-db:
    image: camptocamp/testgeomapfish-external-db:latest
    environment:
      POSTGRES_USER: www-data
      POSTGRES_PASSWORD: www-data
      POSTGRES_DB: test

  print:
    image: camptocamp/testgeomapfish-print:latest

  mapserver:
    image: camptocamp/testgeomapfish-mapserver:latest

  geoportal:
    image: camptocamp/testgeomapfish-geoportal:latest
    ports:
      - 8080:80
