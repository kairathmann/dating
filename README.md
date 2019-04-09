# Luna

This Git repository hosts backend for Luna mobile / website apps and website itself.

`static` directory holds website app created with `React` and `Redux`

# Introduction

The backend that hosts APIs required by both Luna's website app and Luna's mobile app for IOS and Android.

## Technology

- Django 1
- Python 2
- Amazon Web Services
    - Elastic Beanstalk
    - S3
- One Signal
    - For hanlding push notifications
- IMGIX
    - For user avatars image transformations such as scaling etc
- nginx
- React
    - Website app
- Redux
    - Website app state management

## Authorization

The Luna app uses Cookie authentication.

Post to `/api-helios/user/create/` to register a user.

Post to `/api-helios/user/login/` with `email` and `password` set (JSON, form-data and x-www-form-urlencoded supported) to obtain the token.

In Postman, create a global variable named `TOKEN` with your token.

# Launching Django backend

## Requirements:  
1. `docker`
2. `docker-compose`
3. `AWS account`
4. `One Signal account`
5. `IMGIX account` -> must be configured to use the same bucket as the one pointed by `AWS_STORAGE_BUCKET_NAME` below

## Running:  
1. Copy and paste `config.schema.env` file under name: `config.env` and fill all variables:
2. `POSTGRES_DB=luna_dev_db` -> database name that is suppose to be created / used by Luna backend, you can leave it as it is for development purposes
3. `POSTGRES_USER=luna_dev_db` -> database username that is suppose to connect from Luna backend, you can leave it as it is for development purposes
4. `POSTGRES_PASSWORD=luna_dev_db_password` -> database password for given username that is suppose to be used together in order to conenct to database from Luna backend, you can leave it as it is for development purposes
5. `POSTGRES_HOST=postgres` -> database hostname that Luna backend should connect to. Passing `postgres` works for local development because in `docker-compose.yml` backend container is linked to database container via `postgres` name
6. `POSTGRES_PORT=5432` -> database port
7. `ONESIGNAL_APPID=36289b9b-8fea-4e6c-a15b-d6052f144bfc` -> ID of Your One Signal Application
8. `ONESIGNAL_API_ENDPOINT=https://onesignal.com/api/v1/notifications` -> URL pointing to One Signal API for push notifications, should not change
9. `ONESIGNAL_AUTHORIZATION_HEADER=testtest` -> API Key for One Signal, allowing backend to create new push notifications
10. `CACERT_PATH=/usr/local/lib/python2.7/site-packages/certifi/cacert.pem`
11. `AWS_ACCESS_KEY_ID=test_access_key` -> AWS Access Key ID for user who can create new objects in S3 bucket pointed by `AWS_STORAGE_BUCKET_NAME` value
12. `AWS_SECRET_ACCESS_KEY=test_secret_access` -> AWS Secret Access Key for user who can create new objects in S3 bucket pointed by `AWS_STORAGE_BUCKET_NAME` value
13. `AWS_STORAGE_BUCKET_NAME=test_bucket` -> Existing S3 Bucket used for storing user avatars and recorded videos
14. `AWS_DEFAULT_REGION=eu-central-1` -> Region where `AWS_STORAGE_BUCKET_NAME` exists
15. Edit `imgix.env` file to match your Imgix source details
16. Execute `docker-compose up -d` in the root directory of the repository
17. Check if containers started with `docker ps`
18. You can now access DJango backend via `localhost:8001`
18. You can now access database via `localhost:5432` with credentials used in `config.env`
19. You can now access nginx instance via `localhost:443`

# Launching website app

## Requirements:  
1. `Node 8.15+`

## Running:  
1. `cd static/src`
2. Run `npm start` - this will launch Webpack Dev Server and Luna website app in your default browser

