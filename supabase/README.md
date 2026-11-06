# Supabase

Schema for The Geeky Times lives here as SQL migrations (decision 34). Nothing is edited by hand in the Supabase dashboard.

## What is here

- `migrations/` holds the schema, one timestamped file per change, applied in filename order.
- `migrations/20261106085857_init_story_slice.sql` creates the `story` and `published_version` tables, their indexes,
  row-level security policies, and the `publish_version(int)` function that promotes a version atomically (decision 42).
  It contains no story content.

## Rules

- **Migrations are additive only.** Add new files for new changes. Never edit a migration that has already been applied
  to a project, and never drop or rename a table or column in place.
- **Never run `supabase db reset` against a project the owner uses.** It wipes the database it targets. It is only for a
  throwaway local database.
- Readers use the publishable key only. The service-role key stays on the server (seed and publish CLI) and never
  carries a `VITE_` prefix.

## Applying the migration

Install the Supabase CLI, then run these from the repo root. Use the project ref from the Supabase dashboard (not the
URL, and never a key):

```bash
supabase link --project-ref <your-project-ref>
supabase db push
```

If the CLI reports that the project is not initialised, the owner runs `supabase init` once from the repo root. That
creates `supabase/config.toml`, which is then committed. Review the output of `supabase db push` before confirming.

## Reference

- Row-level security: https://supabase.com/docs/guides/database/postgres/row-level-security
- Securing data: https://supabase.com/docs/guides/database/secure-data
