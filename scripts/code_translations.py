import logging
import os

import polars as pl

URI = f'postgresql://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@{os.getenv("POSTGRES_HOST")}:{os.getenv("POSTGRES_PORT")}/{os.getenv("POSTGRES_DATABASE")}'


def get_translations(xlate_source: str) -> dict[str, pl.DataFrame]:
    logging.info("Querying translations for source %s", xlate_source)
    translations = {}
    for xtable in (
        pl.read_database_uri(
            """
            select
                table_name
            from information_schema.tables
            where
                1=1
                and table_type = 'BASE TABLE'
                and table_schema = 'gsidb'
                and table_name like 'x_%'
            """,
            URI,
            engine="connectorx",
        )
        .to_series()
        .to_list()
    ):
        # Get translations for the x table
        xlates = pl.read_database_uri(
            "select * from %s where source = '%s'" % (xtable, xlate_source),
            URI,
            engine="connectorx",
        )
        if not xlates.is_empty():
            # Get the foreign keys for the x table
            fk = pl.read_database_uri(
                """
                select
                    kcu.table_schema,
                    tc.constraint_name,
                    kcu.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM
                    information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE
                    constraint_type = 'FOREIGN KEY'
                    AND tc.table_name = '%s'
                    AND left(ccu.table_name, 2) = 'e_'
                """
                % (xtable),
                URI,
                engine="connectorx",
            )
            # Get the primary keys for the x table
            pk_cols = pl.read_database_uri(
                """
                SELECT
                    string_agg('x.' || kcu.column_name, ',') as pk_cols
                FROM
                    information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                WHERE
                    tc.constraint_type = 'PRIMARY KEY'
                    AND tc.table_name = '%s'
                """
                % (xtable),
                URI,
                engine="connectorx",
            )["pk_cols"][0]
            # Get all the columns for the foreign table, minus the columns "rev_time" and "rev_user"
            vv_cols = pl.read_database_uri(
                """
                select string_agg('f.' || column_name, ',' order by ordinal_position) as cols
                from information_schema.columns
                where table_name = '%s'
                and table_schema = 'gsidb'
                and column_name not in ('rev_time', 'rev_user')
            """
                % (fk["foreign_table_name"][0]),
                URI,
                engine="connectorx",
            )["cols"][0]
            # Join the x table with the foreign table
            # This produces a table with all source translations and their valid value definition.
            df = pl.read_database_uri(
                """
                select
                    %s,
                    %s
                from
                    %s as x
                    inner join %s as f on x.%s = f.%s
                where x.source = '%s'
                order by %s
                """
                % (
                    pk_cols,
                    vv_cols,
                    xtable,
                    fk["foreign_table_name"][0],
                    fk["foreign_column_name"][0],
                    fk["column_name"][0],
                    xlate_source,
                    pk_cols,
                ),
                URI,
                engine="connectorx",
            )
            logging.info("Found %s translations for table %s" % (df.shape[0], xtable))
            translations[xtable] = df
    return translations
