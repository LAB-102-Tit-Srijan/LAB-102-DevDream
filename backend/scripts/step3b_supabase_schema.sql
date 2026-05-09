-- STEP 3B: Status lifecycle + transcript uniqueness + policy fix
-- Run in Supabase SQL Editor.

begin;

-- 1) Ensure videos.processing_status exists with strict lifecycle values
alter table public.videos
add column if not exists processing_status text not null default 'uploaded';

do $$
begin
    if not exists (
        select 1
        from pg_constraint
        where conname = 'videos_processing_status_check'
    ) then
        alter table public.videos
        add constraint videos_processing_status_check
        check (processing_status in ('uploaded', 'transcribing', 'transcribed', 'ready', 'failed'));
    end if;
end
$$;

-- 2) One transcript per video (duplicate prevention at DB level)
create unique index if not exists uq_transcripts_video_id
on public.transcripts (video_id);

-- 3) Useful query/index support for status polling
create index if not exists idx_videos_processing_status
on public.videos (processing_status);

-- 4) Optional hardening: keep FK explicit and cascading deletes
do $$
begin
    if not exists (
        select 1
        from information_schema.table_constraints
        where table_schema = 'public'
          and table_name = 'transcripts'
          and constraint_type = 'FOREIGN KEY'
          and constraint_name = 'transcripts_video_id_fkey'
    ) then
        alter table public.transcripts
        add constraint transcripts_video_id_fkey
        foreign key (video_id)
        references public.videos(id)
        on delete cascade;
    end if;
end
$$;

commit;

-- ------------------------------------------------------------
-- POLICY FIX OPTIONS (pick ONE approach)
-- ------------------------------------------------------------

-- A) Recommended (production-safe):
--    Keep RLS strict and set SUPABASE_SERVICE_ROLE_KEY in backend .env.
--    No permissive anon UPDATE policy needed.

-- B) Hackathon fallback (less secure):
--    Allow anon role to update video status via REST API.
--    Use only for demo environments.
--
-- alter table public.videos enable row level security;
--
-- do $$
-- begin
--     if not exists (
--         select 1
--         from pg_policies
--         where schemaname = 'public'
--           and tablename = 'videos'
--           and policyname = 'allow_anon_update_video_status'
--     ) then
--         create policy allow_anon_update_video_status
--         on public.videos
--         for update
--         to anon
--         using (true)
--         with check (processing_status in ('uploaded', 'transcribing', 'transcribed', 'ready', 'failed'));
--     end if;
-- end
-- $$;
