-- ═══════════════════════════════════════════════════════════════════════
-- StudyAI — user_notes Table
-- Run this SQL in the Supabase SQL Editor (Dashboard > SQL Editor > New query)
-- ═══════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS user_notes (
    id            BIGSERIAL PRIMARY KEY,
    user_id       UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    video_id      INT NOT NULL,
    content       TEXT NOT NULL,
    timestamp     FLOAT NOT NULL DEFAULT 0.0,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for fast user+video filtering
CREATE INDEX IF NOT EXISTS idx_user_notes_user_video
    ON user_notes (user_id, video_id);

-- Row Level Security (RLS)
ALTER TABLE user_notes ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access their own notes
CREATE POLICY "Users can manage their own notes"
    ON user_notes
    FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Allow service_role full access (for backend API using service key)
CREATE POLICY "Service role full access on user_notes"
    ON user_notes
    FOR ALL
    USING (true)
    WITH CHECK (true);
