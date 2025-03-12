from typing import Any, Dict, List
from langchain.embeddings.base import Embeddings
from langchain_community.vectorstores import Qdrant
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, Filter
from langflow.custom import Component
from langflow.schema import Message, Data
# from langflow.base.vectorstores.model import LCVectorStoreComponent, check_cached_vector_store
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
        MessageInput(name="collection_name",
                     display_name="Collection Name",
                     required=True),
        MessageInput(name="question",
                     display_name="Question",
                     ),
        MessageInput(name="restart_search",
                     display_name="Restart Search",
                     ),
        MessageInput(name="qdrant_host",
                     display_name="Qdrant Host",
                     ),
        MessageInput(name="qdrant_port",
                     display_name="Qdrant Port",
                     ),

        DataInput(name="documents", display_name="Documents"),
        DataInput(name="files", display_name="Files"),

        HandleInput(name="embedding", display_name="Embedding",
                    input_types=["Embeddings"]),
    ]

    outputs = [
        Output(name="success",
               display_name="Success",
               method="vectorize_documents"),
        Output(name="search",
               display_name="Search",
               method="search_documents"),
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

            qdrant_host = self.qdrant_host.get_text()
            qdrant_port = self.qdrant_port.get_text()

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
                documents: List[Document] = list(self.documents.data.values())
                if not documents:
                    raise ValueError("No documents provided")

                # Get vector size from first document
                vector = embedding.embed_query(documents[0].page_content)
                vector_size = len(vector)

                # Create collection if needed
                if not self.check_collection_exists(client, collection_name):
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

    def vectorize_documents(self) -> Message:
        try:
            qdrant = self.build_vector_store()
            if not self.documents:
                return Message(text="No documents to process")

            docs: Dict[str, Document] = self.documents.data

            documents = list(docs.values())

            if not documents:
                return Message(text="No documents to process")

            # Process each document chunk
            existing = True

            for i, doc in enumerate(documents, 1):

                existing_doc = self.check_document_exists(
                    qdrant, doc)

                if (existing_doc and existing):
                    existing = True

                    continue

                existing = False
                # Add document to Qdrant
                qdrant.add_documents([doc])

            msg = Message(
                role="system",
                text=f'Document {",".join(str(document.metadata["id"]) for document in documents)} added to Qdrant'
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

        not_found_files = []

        for file in files:
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
