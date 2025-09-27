from sqlalchemy import Table, Column, String, MetaData, Text, Boolean, TIMESTAMP, JSON, ARRAY, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from pgvector.sqlalchemy import Vector
import uuid

#
# *** Best Practice: Use SQLAlchemy for DB models, Pydantic for I/O models *** 
# You should not use Pydantic to define your models.py ORM layer. Pydantic is designed for 
# validation and serialization of input/output data—not for managing database schemas, relationships,
# or querying behavior. SQLAlchemy is purpose-built for that.
#

Base = declarative_base()

class Document_Chunk(Base):
    __tablename__ = 'document_chunk'
    __table_args__ = {'schema': 'document'}

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    embedding       = Column(Vector(1536))
    chunk_text      = Column(Text)
    doc_metadata    = Column(JSON)
    file_name       = Column(Text)
    doc_tags        = Column(ARRAY(Text))
    isActive        = Column(Boolean)
    version         = Column(Text)
    created_at      = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at      = Column(TIMESTAMP)
    
