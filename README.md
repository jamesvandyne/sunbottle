# Sunbottle

Sunbottle is a tool for automatically collecting your generation, purchase and selling, and storage of electricity.

It currently works with Sharp's Cocoro Energy in Japan, but can be extended to support additional systems.


## Deploying

Sunbottle is a standard Python/Django application, so you are able to host it anywhere. However, I 
recommend [fly.io](https://fly.io) because it's where I run mine and have included instructions. 

### Clone this repository

```
$ git clone 
```

### Generate a secret key

First generate a secret key for the application using the command below. 

```
$ python3 -c "import secrets; print(secrets.token_urlsafe())"
```

## Set Secrets


```
$ flyctl secrets set DJANGO_SECRET_KEY=<my_secret key>
$ flyctl secrets set SHARP_LOGIN_MEMBERID=<my_member_id>
$ flyctl secrets set SHARP_LOGIN_PASSWORD=<strong_password_here>
$ flyctl secrets set ALLOWED_HOSTS=<my_domain>
```

# Make block storage

Add block storage so your readings and generation data will persist across deploys.

```
fly volumes create sunbottle_data --region nrt --size 3
```

Add the storage to your `fly.toml` so the server can use it.

```
[mounts]
source="sunbottle_data"
destination="/opt/sunbottle/data"
```

Deploy sunbottle

```
$ flyctl deploy
```

### Run migrations

```
$ flyctl ssh console
$ cd /app
$ python manage.py createsuperuser
```

### Add super user

``` 
$ python manage.py createsuperuser
```
