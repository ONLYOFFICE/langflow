from langchain.embeddings.base import Embeddings
from langchain_community.vectorstores import Qdrant
from langchain_core.documents import Document
from langflow.custom import Component
from langflow.schema import Message
from langflow.io import (
    DataInput,
    Output,
)

from langflow.utils.qdrant import get_qdrant_client, check_collection_exists, create_collection, check_document_exists, qdrant_inputs


class QdrantCheckFileComponent(Component):
    display_name = "Qdrant Check Document"
    description = "Check if document exists in Qdrant Vector Store"
    icon = "Qdrant"

    inputs = [
        *qdrant_inputs,
        DataInput(
            name='metadata',
            display_name="Metadata"
        ),
    ]

    outputs = [
        Output(name="check",
               display_name="Check document",
               method="check_document")
    ]

    def build_vector_store(self) -> Qdrant:
        try:
            collection_name: str = self.collection_name.get_text()
            embedding: Embeddings = self.embedding

            client = get_qdrant_client(
                self.qdrant_host.get_text(), self.qdrant_port.get_text())

            if not check_collection_exists(client, collection_name):
                # Get vector size from first document
                doc = Document(page_content='content for vectorize',
                               metadata={**self.metadata.data})
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

    def check_document(self) -> Message:
        qdrant = self.build_vector_store()

        if not self.metadata:
            return Message(text="No metadata provided")

        doc = Document(page_content="", metadata={**self.metadata.data})

        if check_document_exists(qdrant, doc):
            return Message(text="exist")

        return Message(text="not_found")
