from datetime import datetime
from typing import Optional, List

from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.domain.entity import Entity
from tracardi.service.storage.factory import StorageFor, storage_manager, StorageForBulk


async def save_sessions(profiles: List[Session]):
    return await StorageForBulk(profiles).index('session').save()


async def update_session_duration(session: Session):
    await storage_manager("session").update_document(id=session.id, record={
        "metadata": {
            "time": {
                "update": datetime.utcnow(),
                "duration": session.metadata.time.duration
            }
        }
    }, retry_on_conflict=3)


async def save_session(session: Session, profile: Optional[Profile], profile_less, persist_session: bool = True):

    if persist_session:
        if profile_less is False:
            if session.operation.new:
                # Add new profile id to session if it does not exist, or profile id in session is different then
                # the real profile id.
                if session.profile is None or (isinstance(session.profile, Entity)
                                               and isinstance(profile, Entity)
                                               and session.profile.id != profile.id):
                    # save only profile Entity
                    session.profile = Entity(id=profile.id)
                return await StorageFor(session).index().save()
            else:
                # Update session duration
                await update_session_duration(session)

    return BulkInsertResult()


async def load(id: str) -> Session:
    return await StorageFor(Entity(id=id)).index("session").load(Session)


async def delete(id: str):
    return await storage_manager('session').delete(id)


async def refresh():
    return await storage_manager('session').refresh()


async def flush():
    return await storage_manager('session').flush()


async def get_nth_last_session(profile_id: str, n: int):
    result = await storage_manager('session').query({
        "query": {
            "term": {"profile.id": profile_id}
        },
        "size": 11,
        "sort": [
            {"metadata.time.insert": "desc"}
        ]
    })

    return result["hits"]["hits"][n - 1]["_source"] if len(result["hits"]["hits"]) >= n else None
