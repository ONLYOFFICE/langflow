from langchain.embeddings.base import Embeddings
from langchain_community.vectorstores import Qdrant
from langchain_core.documents import Document
from qdrant_client.models import Filter
from langflow.custom import Component
from langflow.schema import Message
from langflow.io import (
    DataInput,
    Output,
)

from langflow.utils.qdrant import get_qdrant_client, check_collection_exists, create_collection, check_document_exists, qdrant_inputs


class QdrantCheckFolderComponent(Component):
    display_name = "Qdrant Check Folder"
    description = "Check if document exists in Qdrant Vector Store"
    icon = "Qdrant"

    inputs = [
        *qdrant_inputs,
    ]

    outputs = [
        Output(name="check",
               display_name="Check folder",
               method="check_folder")
    ]

    def build_vector_store(self) -> Qdrant:
        try:
            collection_name: str = self.collection_name.get_text()
            embedding: Embeddings = self.embedding

            client = get_qdrant_client(
                self.qdrant_host.get_text(), self.qdrant_port.get_text())

            if not check_collection_exists(client, collection_name):
                # Get vector size from first document
                doc = Document(page_content='content for vectorize')
                vector = embedding.embed_query(doc.page_content)
                vector_size = len(vector)

                create_collection(
                    client, collection_name, vector_size)

            qdrant = Qdrant(client=client,
                            embeddings=embedding,
                            collection_name=collection_name)

            return qdrant

        except Exception as e:
            raise Exception(f"Error building vector store: {str(e)}")

    def check_folder(self) -> Message:
        qdrant = self.build_vector_store()

        filter = Filter(must=[
            {"key": "metadata.page", "match": {
                "value": 0
            }}
        ])

        docs = qdrant.similarity_search(
            query="",
            k=1000,
            filter=filter
        )

        files_ids = [doc.metadata.get('id') for doc in docs]
        files_versions = [doc.metadata.get('version') for doc in docs]

        response = ', '.join(
            [f'{id}:{version}' for id, version in zip(files_ids, files_versions)])

        return Message(text=response)
