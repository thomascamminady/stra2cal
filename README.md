# stra2cal

Find this repository on [Github](https://github.com/thomascamminady/stra2cal) or check out the [documentation](https://thomascamminady.github.io/stra2cal).

## Development

Set up the full project by running `make`.

## Documentation

Go to `Settings->Pages` and set `Source` (under `Build and deployment`) to `Github Actions`.

## Docker

````
docker build -t stra2cal .
docker run -v database:/app/database -p 4000:80 my-fastapi-app
```

Go to `localhost:4000/login`

## Credits

This package was created with [`cookiecutter`](https://github.com/audreyr/cookiecutter) and [`thomascamminady/cookiecutter-pypackage`](https://github.com/thomascamminady/cookiecutter-pypackage), a fork of [`audreyr/cookiecutter-pypackage`](https://github.com/audreyr/cookiecutter-pypackage).
````
