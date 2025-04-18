import os

from typing import Optional, List

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, Filter

from langchain_community.vectorstores import Qdrant
from langchain_core.documents import Document

from langflow.io import (
    MessageInput,
    HandleInput,
)

qdrant_inputs = [
    MessageInput(
        name="collection_name",
        display_name="Collection Name",
        required=True
    ),
    MessageInput(
        name="qdrant_host",
        display_name="Qdrant Host",
        required=False
    ),
    MessageInput(
        name="qdrant_port",
        display_name="Qdrant Port",
        required=False
    ),
    HandleInput(
        name="embedding",
        display_name="Embedding",
        input_types=["Embeddings"]
    ),
]


def check_collection_exists(client: QdrantClient, collection_name: str) -> bool:
    """Check if collection exists in Qdrant."""
    try:
        collections = client.get_collections()
        return any(collection.name == collection_name for collection in collections.collections)
    except Exception as e:
        raise Exception(f"Error checking collections list: {str(e)}")


def create_collection(client: QdrantClient, collection_name: str, vector_size: int) -> bool:
    """Create a new collection in Qdrant."""
    try:
        # Create new collection
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )

        return True

    except Exception as e:
        raise Exception(
            f"Failed to create collection {collection_name}: {str(e)}")


def get_qdrant_client(host: Optional[str], port: Optional[int]) -> QdrantClient:
    try:

        # Get host and port from inputs or environment variables
        qdrant_host = host if host else None
        qdrant_port = port if port else None

        # If not provided in inputs, check environment variables
        if not qdrant_host:
            qdrant_host = os.getenv(
                'HOST_QDRANT_SERVICE', 'onlyoffice-qdrant')

        if not qdrant_port:
            qdrant_port = os.getenv('HOST_QDRANT_PORT', "6333")

            # Create QdrantClient with HTTP and timeout
            client = QdrantClient(
                host=qdrant_host,
                port=qdrant_port,  # HTTP/REST API port
                prefer_grpc=False,  # Use HTTP
                timeout=10.0  # Add timeout
            )

        return client

    except Exception as e:
        raise Exception(f"Error building vector store: {str(e)}")


def check_document_exists(qdrant: Qdrant, document: Document) -> List[Document]:
    # Only check if document has metadata with id and version
    if not document.metadata or 'id' not in document.metadata or 'version' not in document.metadata:
        return []

    return qdrant.similarity_search(
        query=document.page_content,
        k=1,
        filter=Filter(
            must=[
                {"key": "metadata.id", "match": {
                        "value": document.metadata['id']}},
                {"key": "metadata.version", "match": {
                        "value": document.metadata['version']}},
            ]
        )
    )
