# Here are some instructions for getting Airlfow and nd runnig

## Getting Started

### Postgres Backend

While Airflow can run in a standalone capacity using SQLite DB, it's relatively simple to get up and running with your own production grade backend.

To connect a Postgres DB to your Airflow instance, set the following vairable in your `airflow.cfg` file to a valid connection string. Make sure the user you provide has permissions that enable reads, writes, and modifications of public schemas on your DB!

```
sql_alchemy_conn = postgresql+psycopg2://<usernane>:<password>@<host>/<database>
```

### Syncing Repository DAGs with Core DAGS Folder

To ensure DAGs from this repository are discoverable by Airflow, we need to either:

- Set `dags_folder` to the directory in our repository containing our DAGs or,
- Sync our repositories DAGs with a different, centralized, DAG folder (recommended)

To sync our repo's DAGs with a centralized DAG folder, we use a symlink:

```
ln -s /your/repositories/dag/folder*/ /your/centralized/dag/folder/
```
