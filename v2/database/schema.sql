-- Weekly Food Planner V2 persistent state
-- PostgreSQL / Supabase compatible. GitHub contains schema only; real household data stays private.

create extension if not exists pgcrypto;

create table households (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  currency text not null default 'GBP',
  timezone text not null default 'Europe/London',
  weekly_budget numeric(10,2),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table household_members (
  id uuid primary key default gen_random_uuid(),
  household_id uuid not null references households(id) on delete cascade,
  display_name text not null,
  member_type text not null check (member_type in ('adult','child')),
  portion_factor numeric(5,2) not null check (portion_factor > 0),
  active boolean not null default true,
  created_at timestamptz not null default now()
);

create table preferences (
  id uuid primary key default gen_random_uuid(),
  household_id uuid not null references households(id) on delete cascade,
  member_id uuid references household_members(id) on delete cascade,
  preference_type text not null check (preference_type in ('loved','good','okay','needs_adjustment','avoid','standing_rule')),
  subject text not null,
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table ingredients (
  id text primary key,
  name text not null,
  canonical_unit text not null check (canonical_unit in ('g','ml','each'))
);

create table inventory (
  id uuid primary key default gen_random_uuid(),
  household_id uuid not null references households(id) on delete cascade,
  ingredient_id text not null references ingredients(id),
  quantity numeric(12,3) not null check (quantity >= 0),
  unit text not null check (unit in ('g','ml','each')),
  priority text not null default 'no_urgency' check (priority in ('use_first','use_if_sensible','no_urgency')),
  source text not null default 'confirmed_stock',
  notes text,
  updated_at timestamptz not null default now(),
  unique(household_id, ingredient_id, unit)
);

create table weeks (
  id uuid primary key default gen_random_uuid(),
  household_id uuid not null references households(id) on delete cascade,
  start_date date not null,
  end_date date not null,
  status text not null check (status in ('draft','confirmed','current','archived')),
  budget_target numeric(10,2),
  budget_forecast numeric(10,2),
  confirmed_at timestamptz,
  created_at timestamptz not null default now(),
  unique(household_id, start_date)
);

create unique index one_current_week_per_household on weeks(household_id) where status = 'current';

create table meals (
  id uuid primary key default gen_random_uuid(),
  week_id uuid not null references weeks(id) on delete cascade,
  meal_key text not null,
  meal_date date not null,
  slot text not null check (slot in ('breakfast','lunch','dinner','snack')),
  title text not null,
  meal_mode text not null check (meal_mode in ('cook','standalone','planned_leftover')),
  source_meal_id uuid references meals(id),
  cuisine text,
  method jsonb,
  flavour_note text,
  child_note text,
  storage_note text,
  created_at timestamptz not null default now(),
  unique(week_id, meal_key),
  check ((meal_mode = 'planned_leftover' and source_meal_id is not null) or meal_mode <> 'planned_leftover')
);

create table meal_allocations (
  id uuid primary key default gen_random_uuid(),
  meal_id uuid not null references meals(id) on delete cascade,
  member_id uuid not null references household_members(id),
  purpose text not null check (purpose in ('breakfast','lunch','dinner','snack','other')),
  portion_factor numeric(5,2) not null check (portion_factor > 0)
);

create table meal_ingredients (
  id uuid primary key default gen_random_uuid(),
  meal_id uuid not null references meals(id) on delete cascade,
  ingredient_id text not null references ingredients(id),
  quantity numeric(12,3) not null check (quantity > 0),
  unit text not null check (unit in ('g','ml','each')),
  notes text,
  unique(meal_id, ingredient_id, unit)
);

create table shopping_items (
  id uuid primary key default gen_random_uuid(),
  week_id uuid not null references weeks(id) on delete cascade,
  ingredient_id text references ingredients(id),
  name text not null,
  quantity numeric(12,3) not null check (quantity > 0),
  unit text not null,
  estimated_cost numeric(10,2),
  category text not null default 'food' check (category in ('food','breakfast','snack','toiletry','household','other')),
  purchased boolean not null default false,
  purchased_at timestamptz,
  intentional_remainder numeric(12,3),
  notes text
);

create table inventory_movements (
  id uuid primary key default gen_random_uuid(),
  household_id uuid not null references households(id) on delete cascade,
  ingredient_id text not null references ingredients(id),
  week_id uuid references weeks(id) on delete set null,
  movement_type text not null check (movement_type in ('opening_stock','purchase','recipe_use','adjustment','waste','carry_forward')),
  quantity numeric(12,3) not null,
  unit text not null check (unit in ('g','ml','each')),
  notes text,
  created_at timestamptz not null default now()
);

create table meal_feedback (
  id uuid primary key default gen_random_uuid(),
  household_id uuid not null references households(id) on delete cascade,
  meal_id uuid references meals(id) on delete set null,
  meal_title text not null,
  rating text not null check (rating in ('loved','good','okay','needs_adjustment','do_not_suggest')),
  notes text,
  created_at timestamptz not null default now()
);

create table week_events (
  id uuid primary key default gen_random_uuid(),
  week_id uuid not null references weeks(id) on delete cascade,
  event_type text not null check (event_type in ('meal_out','night_away','work_change','nursery_change','request','confirmed_need','other')),
  event_date date,
  details jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

-- Database invariants that are easier to express procedurally/application-side:
-- 1. planned_leftover meals must not have meal_ingredients rows.
-- 2. a planned_leftover must reference a cook/standalone source meal in the same household/week context.
-- 3. week transition archives the previous current week atomically.
-- 4. confirmed/current weeks may only be created from a publishable deterministic reconciliation.
-- 5. inventory is updated from reconciled movements, never inferred from historical plans.
