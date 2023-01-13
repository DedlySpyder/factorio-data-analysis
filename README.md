[Factorio](https://www.factorio.com/) data stage analysis tool.

This tools uses a [docker image](https://hub.docker.com/repository/docker/dedlyspyder/factorio-data-analysis) to handle portability. [Docker](https://www.docker.com/products/docker-desktop) is required for use. Docker compose is recommended for easy usage.


## Usage

This tool has 2 main modes of operation:

* `diff` -  Dump the state of `data.raw` after each mod runs a data sub-stage, then commit it to `git` to use as a viewer
* `final` - Dump the final state of `data.raw` after all mods have modified it


**NOTE: the mods directory used for this tool must contain the 2 mods from this [runtime/mods](./runtime/mods) directory here**


### Docker Compose - Preferred

Running the relevant [compose file](./runtime/docker) for this tool will use any mods in the [mods](./runtime/mods) directory here for analysis. The output for either mode will be in a directory here named either `diff_data` or `final_data`.

Either of these directories can be overridden by creating a `.env` file in the same directory as the `docker-compose.yml` file. An [example](./runtime/docker/example.env) of this file is provided.


### Manual Docker Runs

Running this tool manually requires mounting a `/factorio/mods` and an `/output` directory inside the container. An example docker run command to mount the mods directory here, and output to a `data` directory here looks like this:

```shell
docker run -t \
  --mount type=bind,source="$(pwd)"/mods,target=/factorio/mods \
  --mount type=bind,source="$(pwd)"/data,target=/output \
  dedlyspyder/factorio-data-analysis [final|diff]
```

This will run the underlying python script directly, so passing in `-h` or `--help` will provide more help if required.
