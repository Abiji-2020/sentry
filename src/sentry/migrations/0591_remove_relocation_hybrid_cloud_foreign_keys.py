# Generated by Django 3.2.23 on 2023-11-07 22:35

from django.db import migrations

import sentry.db.models.fields.bounded
from sentry.new_migrations.migrations import CheckedMigration


class Migration(CheckedMigration):
    # This flag is used to mark that a migration shouldn't be automatically run in production. For
    # the most part, this should only be used for operations where it's safe to run the migration
    # after your code has deployed. So this should not be used for most operations that alter the
    # schema of a table.
    # Here are some things that make sense to mark as post deployment:
    # - Large data migrations. Typically we want these to be run manually by ops so that they can
    #   be monitored and not block the deploy for a long period of time while they run.
    # - Adding indexes to large tables. Since this can take a long time, we'd generally prefer to
    #   have ops run this and not block the deploy. Note that while adding an index is a schema
    #   change, it's completely safe to run the operation after the code has deployed.
    is_post_deployment = False

    dependencies = [
        ("sentry", "0590_add_metadata_to_sentry_app"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    """
                    ALTER TABLE "sentry_relocation" ADD COLUMN "creator_id" bigint NOT NULL;
                    ALTER TABLE "sentry_relocation" ADD COLUMN "owner_id" bigint NOT NULL;
                    """,
                    reverse_sql="""
                    ALTER TABLE "sentry_relocation" DROP COLUMN "creator_id";
                    ALTER TABLE "sentry_relocation" DROP COLUMN "owner_id";
                    """,
                    hints={"tables": ["sentry_relocation"]},
                )
            ],
            state_operations=[
                migrations.RemoveField(model_name="relocation", name="creator"),
                migrations.RemoveField(model_name="relocation", name="owner"),
                migrations.AddField(
                    model_name="relocation",
                    name="creator_id",
                    field=sentry.db.models.fields.bounded.BoundedBigIntegerField(),
                ),
                migrations.AddField(
                    model_name="relocation",
                    name="owner_id",
                    field=sentry.db.models.fields.bounded.BoundedBigIntegerField(),
                ),
            ],
        )
    ]
