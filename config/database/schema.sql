-- Rainze Long-term Memory Database Schema
-- 长期记忆数据库结构定义
-- 
-- Reference: PRD §0.2.3 (Layer 3: Long-term Memory)
-- Reference: PRD §0.4 (Hybrid Storage - FAISS + SQLite)
-- 
-- Created: 2026-01-01
-- Version: 1.0.0

-- ============================================================================
-- Layer 3: Long-term Memory Tables
-- ============================================================================

-- Episodes Table - 情景记忆
CREATE TABLE IF NOT EXISTS episodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    summary TEXT,
    episode_type TEXT NOT NULL,
    scene_type TEXT,
    emotion_tag TEXT,
    importance REAL NOT NULL DEFAULT 0.5,
    affinity_delta INTEGER DEFAULT 0,
    embedding_id INTEGER,
    has_embedding BOOLEAN DEFAULT 0,
    retrieval_count INTEGER DEFAULT 0,
    access_count INTEGER DEFAULT 0,
    last_accessed_at DATETIME,
    tags TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_episodes_type ON episodes(episode_type);
CREATE INDEX IF NOT EXISTS idx_episodes_importance ON episodes(importance DESC);
CREATE INDEX IF NOT EXISTS idx_episodes_created_at ON episodes(created_at DESC);

-- User Preferences Table - 用户偏好事实
CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    confidence REAL NOT NULL DEFAULT 1.0,
    evidence_count INTEGER DEFAULT 1,
    source TEXT,
    notes TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(category, key)
);

CREATE INDEX IF NOT EXISTS idx_preferences_category ON user_preferences(category);

-- Behavior Patterns Table - 行为模式
CREATE TABLE IF NOT EXISTS behavior_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_type TEXT NOT NULL,
    description TEXT NOT NULL,
    frequency TEXT,
    time_window TEXT,
    weekday_pattern TEXT,
    confidence REAL NOT NULL DEFAULT 0.5,
    sample_count INTEGER DEFAULT 1,
    last_observed_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Relations Table - 实体关系图
CREATE TABLE IF NOT EXISTS relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object TEXT NOT NULL,
    strength REAL NOT NULL DEFAULT 0.5,
    evidence_count INTEGER DEFAULT 1,
    evidence_episodes TEXT,
    notes TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(subject, predicate, object)
);

-- Pending Vectorization Queue
CREATE TABLE IF NOT EXISTS pending_vectorization (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    episode_id INTEGER NOT NULL,
    priority REAL NOT NULL DEFAULT 0.5,
    retry_count INTEGER DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'pending',
    error_message TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at DATETIME,
    FOREIGN KEY (episode_id) REFERENCES episodes(id) ON DELETE CASCADE
);

-- Memory Metadata
CREATE TABLE IF NOT EXISTS memory_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO memory_metadata (key, value) VALUES
    ('schema_version', '1.0.0'),
    ('total_episodes', '0'),
    ('faiss_index_path', './data/faiss_index.bin');
