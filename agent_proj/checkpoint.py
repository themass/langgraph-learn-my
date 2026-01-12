"""
Custom MySQL Checkpointer Implementation for LangGraph.
Adapts the BaseCheckpointSaver interface to store state in MySQL.
"""
from typing import Any, AsyncIterator, Dict, Optional, Tuple, List
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, desc, delete
from langgraph.checkpoint.base import BaseCheckpointSaver, Checkpoint, CheckpointMetadata, CheckpointTuple
from langgraph.checkpoint.serializers import JsonPlusSerializer
from .db_models import AgentCheckpoint, Base

class MySQLCheckpointer(BaseCheckpointSaver):
    """
    A checkpoint saver that stores state in a MySQL database.
    """
    def __init__(self, db_url: str):
        super().__init__(serializer=JsonPlusSerializer())
        self.engine = create_async_engine(db_url, echo=False)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def aput(
        self,
        config: Dict[str, Any],
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: Optional[dict] = None,
    ) -> Dict[str, Any]:
        """Save a checkpoint to the database."""
        thread_id = config["configurable"]["thread_id"]
        
        async with self.async_session() as session:
            # Serialize
            checkpoint_blob = self.serializer.dumps(checkpoint)
            
            # Create record
            record = AgentCheckpoint(
                thread_id=thread_id,
                thread_ts=checkpoint["id"],
                parent_ts=config["configurable"].get("thread_ts"),
                checkpoint=checkpoint_blob,
                metadata_=metadata
            )
            
            session.add(record)
            await session.commit()
            
        return {
            "configurable": {
                "thread_id": thread_id,
                "thread_ts": checkpoint["id"],
            }
        }

    async def aget_tuple(self, config: Dict[str, Any]) -> Optional[CheckpointTuple]:
        """Get a checkpoint tuple from the database."""
        thread_id = config["configurable"]["thread_id"]
        thread_ts = config["configurable"].get("thread_ts")
        
        async with self.async_session() as session:
           stmt = select(AgentCheckpoint).where(AgentCheckpoint.thread_id == thread_id)
           
           if thread_ts:
               stmt = stmt.where(AgentCheckpoint.thread_ts == thread_ts)
           else:
               stmt = stmt.order_by(desc(AgentCheckpoint.created_at)).limit(1)
               
           result = await session.execute(stmt)
           record = result.scalar_one_or_none()
           
           if not record:
               return None
               
           # Deserialize
           checkpoint = self.serializer.loads(record.checkpoint)
           parent_ts = record.parent_ts
           
           # Need to reconstruct CheckpointTuple
           # Note: parent_config is expected by LangGraph
           final_config = config.copy()
           final_config["configurable"]["thread_ts"] = record.thread_ts
           
           parent_config = None
           if parent_ts:
               parent_config = config.copy()
               parent_config["configurable"]["thread_ts"] = parent_ts
               
           return CheckpointTuple(
               config=final_config,
               checkpoint=checkpoint,
               metadata=record.metadata_,
               parent_config=parent_config
           )

    async def alist(
        self,
        config: Optional[Dict[str, Any]],
        *,
        filter: Optional[Dict[str, Any]] = None,
        before: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> AsyncIterator[CheckpointTuple]:
        """List checkpoints from the database."""
        # Simplified implementation for listing
        thread_id = config["configurable"]["thread_id"]
        
        async with self.async_session() as session:
            stmt = select(AgentCheckpoint).where(AgentCheckpoint.thread_id == thread_id)
            stmt = stmt.order_by(desc(AgentCheckpoint.created_at))
            if limit:
                stmt = stmt.limit(limit)
                
            result = await session.execute(stmt)
            records = result.scalars().all()
            
            for record in records:
                checkpoint = self.serializer.loads(record.checkpoint)
                yield CheckpointTuple(
                    config={"configurable": {"thread_id": thread_id, "thread_ts": record.thread_ts}},
                    checkpoint=checkpoint,
                    metadata=record.metadata_,
                    parent_config={"configurable": {"thread_id": thread_id, "thread_ts": record.parent_ts}} if record.parent_ts else None
                )

    # Sync methods are required by abstract base class but we only use async
    def put(self, config, checkpoint, metadata, new_versions): raise NotImplementedError("Async only")
    def get_tuple(self, config): raise NotImplementedError("Async only")
    def list(self, config, *, filter=None, before=None, limit=None): raise NotImplementedError("Async only")
