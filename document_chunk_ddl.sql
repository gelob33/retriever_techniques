-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- for UUID generation

-- Create the table
CREATE TABLE document_chunk (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    embedding VECTOR(1536),  -- text embedding adjust dimension to match your model
    chunk TEXT, -- chunk text / clear
    metadata JSONB, -- metadata for the chunk
    file_name TEXT, -- the name of the file
    tags TEXT[], -- tags that can be used to keyword search
    isActive BOOLEAN, -- identifies if the record is active
    version TEXT, -- defines the file version (e.g. updates)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- date/time the record was created
    updated_at TIMESTAMP -- date/time the record was updated 
);

-- Create an index on the embedding column for similarity search
-- Use ivfflat for approximate nearest neighbor (ANN) search
CREATE INDEX documents_embedding_idx
ON document_chunk USING ivfflat (embedding vector_l2_ops)
WITH (lists = 100);  -- tune 'lists' based on dataset size
