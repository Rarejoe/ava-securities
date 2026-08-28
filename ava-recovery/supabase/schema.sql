-- AVA — Supabase schema
-- Run this once in Supabase: Project -> SQL Editor -> New query -> paste -> Run

-- Profiles table (extends Supabase's built-in auth.users)
create table if not exists public.profiles (
    id uuid references auth.users(id) on delete cascade primary key,
    full_name text,
    created_at timestamptz default now()
);

-- One row per submitted case / report, for ANY service type
create table if not exists public.cases (
    id uuid default gen_random_uuid() primary key,
    user_id uuid references auth.users(id) on delete cascade not null,
    service_slug text not null,              -- matches SERVICES key in config/services.py
    case_number text unique not null,        -- human-friendly ref, e.g. AVA-2026-000123
    data jsonb not null default '{}'::jsonb, -- all form field answers, keyed by field "key"
    status text not null default 'open',     -- open | in_progress | closed
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

create index if not exists cases_user_id_idx on public.cases (user_id);
create index if not exists cases_service_slug_idx on public.cases (service_slug);

-- Row Level Security: users can only ever see their own cases
alter table public.cases enable row level security;

create policy "Users can view their own cases"
    on public.cases for select
    using (auth.uid() = user_id);

create policy "Users can insert their own cases"
    on public.cases for insert
    with check (auth.uid() = user_id);

create policy "Users can update their own cases"
    on public.cases for update
    using (auth.uid() = user_id);

alter table public.profiles enable row level security;

create policy "Users can view their own profile"
    on public.profiles for select
    using (auth.uid() = id);

create policy "Users can update their own profile"
    on public.profiles for update
    using (auth.uid() = id);

-- Auto-create a profile row whenever a new auth user signs up
create or replace function public.handle_new_user()
returns trigger as $$
begin
    insert into public.profiles (id, full_name)
    values (new.id, new.raw_user_meta_data->>'full_name');
    return new;
end;
$$ language plpgsql security definer;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
    after insert on auth.users
    for each row execute procedure public.handle_new_user();

-- Storage bucket for uploaded evidence (screenshots / receipts)
-- Create this via Supabase Dashboard -> Storage -> New bucket -> name: "attachments"
-- Keep it PRIVATE (not public) and add this policy so users only reach their own files:
--
-- create policy "Users can upload their own attachments"
--   on storage.objects for insert
--   with check (bucket_id = 'attachments' and (storage.foldername(name))[1] = auth.uid()::text);
--
-- create policy "Users can view their own attachments"
--   on storage.objects for select
--   using (bucket_id = 'attachments' and (storage.foldername(name))[1] = auth.uid()::text);
