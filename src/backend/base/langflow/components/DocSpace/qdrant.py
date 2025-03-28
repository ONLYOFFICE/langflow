import os
from typing import Any, Dict, List
from langchain.embeddings.base import Embeddings
from langchain_community.vectorstores import Qdrant
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, Filter
from langflow.custom import Component
from langflow.schema import Message
from langflow.io import (
    MessageInput,
    DataInput,
    HandleInput,
    Output,
)


class DocSpaceQdrantVectorStoreComponent(Component):
    display_name = "DocsSpace Qdrant Vector Store"
    description = "Add documents to Qdrant Vector Store"
    icon = "Qdrant"

    inputs = [
        MessageInput(
            name="collection_name",
            display_name="Collection Name",
            required=True
        ),
        MessageInput(
            name="question",
            display_name="Question",
        ),
        MessageInput(
            name="restart_search",
            display_name="Restart Search",
        ),
        MessageInput(
            name="qdrant_host",
            display_name="Qdrant Host",
        ),
        MessageInput(
            name="qdrant_port",
            display_name="Qdrant Port",
        ),

        DataInput(
            name="documents",
            display_name="Documents",
            list=True,
        ),
        DataInput(
            name="files",
            display_name="Files"
        ),
        DataInput(
            name='metadata',
            display_name="Metadata"
        ),

        HandleInput(
            name="embedding",
            display_name="Embedding",
            input_types=["Embeddings"]
        ),
    ]

    outputs = [
        Output(name="vectorize",
               display_name="Vectorize",
               method="vectorize_documents"),
        Output(name="search",
               display_name="Search",
               method="search_documents"),
        Output(name="check",
               display_name="Check document",
               method="check_document")
    ]

    def check_collection_exists(self, client: QdrantClient, collection_name: str) -> bool:
        """Check if collection exists in Qdrant."""
        try:
            collections = client.get_collections()
            return any(collection.name == collection_name for collection in collections.collections)
        except Exception as e:
            raise Exception(f"Error checking collections list: {str(e)}")

    def create_collection(self, client: QdrantClient, collection_name: str, vector_size: int) -> bool:
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

    # @check_cached_vector_store
    def build_vector_store(self) -> Qdrant:
        try:
            collection_name = self.collection_name.get_text()
            embedding: Embeddings = self.embedding

            # Get host and port from inputs or environment variables
            qdrant_host = self.qdrant_host.get_text() if hasattr(
                self, 'qdrant_host') and self.qdrant_host else None
            qdrant_port = self.qdrant_port.get_text() if hasattr(
                self, 'qdrant_port') and self.qdrant_port else None

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

            if self.files:
                if not self.check_collection_exists(client, collection_name):
                    return None

            if self.documents:
                documents: List[str] = [
                    i.data.get('text') for i in self.documents]

                if not documents:
                    raise ValueError("No documents provided")

            if not self.check_collection_exists(client, collection_name):
                # Get vector size from first document
                doc = Document(page_content='content for vectorize',
                               metadata={**self.metadata.data})
                vector = embedding.embed_query(doc.page_content)
                vector_size = len(vector)
                self.create_collection(
                    client, collection_name, vector_size)

            qdrant = Qdrant(client=client,
                            embeddings=embedding,
                            collection_name=collection_name)

            return qdrant

        except Exception as e:
            raise Exception(f"Error building vector store: {str(e)}")

    def check_document_exists(self, qdrant: Qdrant, document: Document) -> List[Document]:
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

    def check_document(self) -> Message:
        qdrant = self.build_vector_store()

        if not self.metadata:
            return Message(text="No metadata provided")

        doc = Document(page_content="", metadata={**self.metadata.data})

        if self.check_document_exists(qdrant, doc):
            return Message(text="exist")

        return Message(text="not_found")

    def vectorize_documents(self) -> Message:
        try:
            qdrant = self.build_vector_store()

            if not self.documents:
                return Message(text="No documents to process")

            metadata = self.metadata.data

            docs: Dict[str, str] = [
                Document(page_content=doc.data.get('text'), metadata={**metadata, "page": i}) for i, doc in enumerate(self.documents)]

            if not docs:
                return Message(text="No documents to process")

            if not metadata:
                return Message(text="No metadata provided")

            if self.check_document_exists(qdrant, docs[0]):
                return Message(text="exist")

            qdrant.add_documents(docs)

            msg = Message(
                text=f'added'
            )

            return msg

        except Exception as e:
            raise Exception(f"Error vectorizing documents: {str(e)}")

    def search_documents(self) -> Message:
        files: List[Dict[str, Any]] = self.files.data.get("files", [])

        if not files:
            return Message(text="No files found in input")

        question: str = self.question.get_text()

        if not question:
            return Message(text="No question provided")

        qdrant = self.build_vector_store()

        if not qdrant:
            return Message(text=", ".join([str(file.get('id', 'unknown')) for file in files]),
                           data={"docs": []})

        # Create a unique list of files based on id and version
        unique_files = []
        file_keys = set()

        for file in files:
            file_id = file.get('id', 'unknown')
            file_version = file.get('version', 1)
            file_key = f"{file_id}_{file_version}"

            if file_key not in file_keys:
                file_keys.add(file_key)
                unique_files.append(file)

        not_found_files = []

        for file in unique_files:
            if self.check_document_exists(qdrant, Document(
                page_content=question,
                metadata={
                    "id": file.get('id', 'unknown'),
                    "version": file.get('version', 1),
                }
            )):
                continue

            not_found_files.append(file)

        if len(not_found_files):
            return Message(text=", ".join([str(file.get('id', 'unknown')) for file in files]),
                           data={"docs": []})

        # Create OR conditions for each file (file_id AND version must match)
        file_conditions = [
            {
                "must": [
                    {"key": "metadata.id", "match": {
                        "value": file.get('id', 'unknown')}},
                    {"key": "metadata.version", "match": {
                        "value": file.get('version', 1)}}
                ]
            } for file in files
        ]

        filter: Filter = Filter(
            should=file_conditions
        )

        docs = qdrant.similarity_search(
            query=question,
            k=5,
            filter=filter
        )

        return Message(text=", ".join([str(file.get('id', 'unknown')) for file in files]),
                       data={"docs": docs})
