# Generated by Django 2.2.28 on 2023-06-22 15:55
import re
from typing import cast

from django.db import migrations

from sentry.api.issue_search import parse_search_query
from sentry.exceptions import InvalidSearchQuery
from sentry.new_migrations.migrations import CheckedMigration
from sentry.utils.query import RangeQuerySetWrapperWithProgressBar


def replacement_term(original_term: str) -> str | None:
    try:
        search_filters = parse_search_query(original_term)
    except Exception:
        return None

    # there should only be a single term since we intentionally find the term substring
    # from the query (which could have multiple terms)
    if len(search_filters) != 1:
        raise Exception(
            f"'{original_term}' should only include a single parselable SearchFilter but {len(search_filters)} were parsed"
        )

    assigned_filter = search_filters[0]

    in_syntax = isinstance(assigned_filter.value.raw_value, list)
    vals_set: set[str] = (
        set(cast(list, assigned_filter.value.raw_value))
        if in_syntax
        else {cast(str, assigned_filter.value.raw_value)}
    )

    if (
        "my_teams" in vals_set
    ):  # if this query already includes my_teams, assume its correct and move on
        return None
    elif "me" in vals_set:
        search_filter_values: list[str] = (
            list(cast(list, assigned_filter.value.raw_value))
            if in_syntax
            else [cast(str, assigned_filter.value.raw_value)]
        )
        # None is a legal value for assigned* filters, it denotes unassigned/not-owned
        # we need to replace Nones with the literal string 'none'
        if None in vals_set:
            search_filter_values = [v if v is not None else "none" for v in search_filter_values]

        for i, v in enumerate(search_filter_values):
            if v == "me":
                search_filter_values.insert(i + 1, "my_teams")
                break

        # if for what-ever reason the in value contains a space, we wrap the raw value in double quotes before joining
        for i, v in enumerate(search_filter_values):
            if " " in v:
                search_filter_values[i] = f'"{v}"'

        joined = ", ".join(search_filter_values)
        search_filter_key = (
            "assigned"
            if assigned_filter.key.name in ("assigned_to", "assigned")
            else "assigned_or_suggested"
        )
        return f"{search_filter_key}:[{joined}]"

    # pessimistically avoid re-writing the query if we aren't sure about the term syntax
    return None


def update_saved_search_query(apps, schema_editor):
    SavedSearch = apps.get_model("sentry", "SavedSearch")
    assigned_regex = re.compile(
        r"(assigned|assigned_to|assigned_or_suggested):me($|\s)", re.IGNORECASE
    )
    assigned_in_regex = re.compile(
        r"(assigned|assigned_to|assigned_or_suggested):\[(.*?)]($|\s)", re.IGNORECASE
    )

    for ss in RangeQuerySetWrapperWithProgressBar(SavedSearch.objects.all()):
        query = ss.query

        try:
            parse_search_query(query)
        except InvalidSearchQuery:
            # make sure the entire saved search query is parselable and syntactically correct before we even
            # attempt to re-write it
            continue

        assigned_me_idx_iter = re.finditer(assigned_regex, query)
        assigned_me_in_idx_iter = re.finditer(assigned_in_regex, query)

        all_idx = [m.span() for m in list(assigned_me_idx_iter) + list(assigned_me_in_idx_iter)]

        try:
            replacements = []
            for start, stop in all_idx or ():
                maybe_replacement = replacement_term(query[start:stop])
                if maybe_replacement:
                    replacements.append((start, stop, maybe_replacement))

            if replacements:
                result = []
                i = 0
                for start, end, replacement in replacements:
                    result.append(query[i:start] + replacement)
                    i = end
                result.append(query[i:])

                ss.query = " ".join(result).strip()
                ss.save(update_fields=["query"])
        except Exception:
            continue


class Migration(CheckedMigration):
    # This flag is used to mark that a migration shouldn't be automatically run in production. For
    # the most part, this should only be used for operations where it's safe to run the migration
    # after your code has deployed. So this should not be used for most operations that alter the
    # schema of a table.
    # Here are some things that make sense to mark as dangerous:
    # - Large data migrations. Typically we want these to be run manually by ops so that they can
    #   be monitored and not block the deploy for a long period of time while they run.
    # - Adding indexes to large tables. Since this can take a long time, we'd generally prefer to
    #   have ops run this and not block the deploy. Note that while adding an index is a schema
    #   change, it's completely safe to run the operation after the code has deployed.
    is_dangerous = True

    dependencies = [
        ("sentry", "0501_typed_bitfield_remove_labels"),
    ]

    operations = [
        migrations.RunPython(
            update_saved_search_query,
            reverse_code=migrations.RunPython.noop,
            hints={"tables": ["sentry_savedsearch"]},
        ),
    ]
