create table jobs (
  id uuid primary key,
  tenant_id uuid not null,
  owner_id uuid not null,
  provider_job_id text not null unique,
  state text not null check (state in ('queued','running','cancel_requested','cancelled','completed','failed')),
  updated_at timestamptz not null default now(),
  version integer not null default 0
);

create index jobs_tenant_state_idx on jobs (tenant_id, state);

create table audit_events (
  id uuid primary key,
  tenant_id uuid not null,
  actor_id uuid not null,
  action text not null,
  subject_id uuid not null,
  created_at timestamptz not null default now()
);
