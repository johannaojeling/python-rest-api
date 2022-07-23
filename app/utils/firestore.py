from typing import Any, AsyncIterator, Dict, Optional, Tuple

from google.cloud.firestore_v1 import SERVER_TIMESTAMP, AsyncClient


class FirestoreDatabase:
    create_at_key: str = "created_at"
    updated_at_key: str = "updated_at"

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def get(self, collection: str, document_id: str) -> Optional[Dict[str, Any]]:
        doc = await self._client.collection(collection).document(document_id).get()
        return doc.to_dict() if doc.exists else None

    async def get_all(
        self, collection: str
    ) -> AsyncIterator[Tuple[str, Dict[str, Any]]]:
        docs = self._client.collection(collection).stream()
        async for doc in docs:
            yield doc.id, doc.to_dict()

    async def create(
        self, collection: str, data: Dict[str, Any], document_id: Optional[str] = None
    ) -> str:
        if document_id:
            doc = self._client.collection(collection).document(document_id)
        else:
            doc = self._client.collection(collection).document()
        entry = {
            self.create_at_key: SERVER_TIMESTAMP,
            self.updated_at_key: SERVER_TIMESTAMP,
            **data,
        }
        await doc.set(entry)
        return doc.id

    async def update(
        self,
        collection: str,
        document_id: str,
        data: Dict[str, Any],
        merge: bool = True,
    ) -> None:
        entry = {self.updated_at_key: SERVER_TIMESTAMP, **data}
        await self._client.collection(collection).document(document_id).set(
            entry, merge=merge
        )

    async def delete(
        self,
        collection: str,
        document_id: str,
    ) -> None:
        await self._client.collection(collection).document(document_id).delete()
