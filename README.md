# Sunbottle

Sunbottle is a tool for automatically collecting your generation, purchase and selling, and storage of electricity.

It currently works with Sharp's Cocoro Energy in Japan, but can be extended to support additional systems.


## Deploying

Sunbottle is a standard Python/Django application, so you are able to host it anywhere. However, I 
recommend [fly.io](https://fly.io) because it's where I run mine and have included instructions. 

The application should be configured with `1024MB` of memory to run stably. 

### Clone this repository

```
$ git clone 
```


## Make block storage

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


### Generate a secret key

Generate a secret key for the application using the command below. 

```
$ python3 -c "import secrets; print(secrets.token_urlsafe())"
```

## Set Secrets

Set the following secrets: 

```
$ flyctl secrets set DJANGO_SECRET_KEY=<my_secret key>
$ flyctl secrets set SHARP_LOGIN_MEMBERID=<my_member_id>
$ flyctl secrets set SHARP_LOGIN_PASSWORD=<strong_password_here>
$ flyctl secrets set ALLOWED_HOSTS=<my_domain>
$ flyctl secrets set DB_NAME=</opt/sunbottle/data/db.sqlite3>
```

Ensure the `DB_NAME` includes the path of your block storage so your data will persist across versions.

`ALLOWED_HOSTS` should include at a minimum your fly.dev domain. Multiple domains should be separated by a comma.

### Deploy sunbottle

```
$ flyctl deploy
```

### Run migrations

Connect to the server and run migrations.

```
$ flyctl ssh console
$ cd /app
$ python manage.py migrate
```

### Add super user
So you can access the Django admin.

``` 
$ python manage.py createsuperuser
```

### Register your battery / generator

Visit `/admin/electricity/battery/add/` to register your battery in Sunbottle. Capacity is in kWh.
Next, visit `/admin/electricity/generator/add/` to add a name for your solar array.


## Test scrape

After setup is complete, Sunbottle will automatically scrape generation, battery level, purchasing, and selling of electric every half-hour.

Before that, it's good to run a test scrape to confirm everything is working.

```
$ python manage.py scrape_everything
```

After about 15 - 20 seconds, this should complete. Refreshing the main page should show data.

## Back-filling historical data

Sunbottle can also be used to scrape historical data. You can do so by running the `scrape_everything` command and including a date at the end.

```
$ python manage.py scrape_everything 2022-10-18
```

# Plugins

To add support for your own system to Sunbottle, you'll need to implement 3 Retriever sub-classes:

* generation.GenerationRetriever
* storage.StorageRetriever
* buysell.BuySellRetriever

Each Retriever will be given a headless Firefox webdriver and an optional date that indicates which date should be retrieved.

The same Firefox instance is used across all retrievers in a single command. 

Once implemented, store them in the domain package e.g. `sunbotle.domain.my_system`.

Next, instruct Sunbottle to use these retrievers by setting the following environment variables/secrets:

```
$ flyctl secrets set GENERATION_RETRIEVER_CLASS=sunbottle.domain.my_system.MyGenerationRetriever
$ flyctl secrets set STORAGE_RETRIEVER_CLASS=sunbottle.domain.my_system.MyStorageRetriever
$ flyctl secrets set BUYSELL_RETRIEVER_CLASS=sunbottle.domain.my_system.MyBuySellRetriever
```

## Generation
Generation retrievers should run a list of `GenerationReading` objects, which is the datetime and kWh of electricity generated. 


```python
from selenium import webdriver

from sunbottle.domain.electricity import generation


class MyGenerationRetriever(generation.GenerationRetriever):
    def retrieve(
        self,
        browser: Optional[webdriver.Firefox] = None,
        date: Optional[datetime.date] = None,
    ) -> list[generation.GenerationReading]:
    ...
```

## Battery level

```python
from selenium import webdriver

from sunbottle.domain.electricity import storage


class MyStorageRetriever(storage.StorageRetriever):
    def retrieve(
        self,
        browser: Optional[webdriver.Firefox] = None,
        date: Optional[datetime.date] = None,
    ) -> list[storage.StorageReading]:
    ...

```

## Buy/Sell Electric 

```python
from selenium import webdriver

from sunbottle.domain.electricity import buysell


class MyBuySellRetriever(buysell.BuySellRetriever):
    def retrieve(
        self,
        browser: Optional[webdriver.Firefox] = None,
        date: Optional[datetime.date] = None,
    ) -> list[Union[buysell.BuyReading, buysell.SellReading]]:
    ...
```