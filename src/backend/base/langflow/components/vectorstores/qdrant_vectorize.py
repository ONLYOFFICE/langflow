from typing import Dict
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


class QdrantVectorizeVectorStoreComponent(Component):
    display_name = "Qdrant Vectorize Documents"
    description = "Add documents to Qdrant Vector Store"
    icon = "Qdrant"

    inputs = [
        *qdrant_inputs,
        DataInput(
            name="documents",
            display_name="Documents",
            list=True,
        ),
        DataInput(
            name='metadata',
            display_name="Metadata"
        ),
    ]

    outputs = [
        Output(name="vectorize",
               display_name="Vectorize",
               method="vectorize_documents"),
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

            if check_document_exists(qdrant, docs[0]):
                return Message(text="exist")

            qdrant.add_documents(docs)

            return Message(
                text='added'
            )

        except Exception as e:
            raise Exception(f"Error vectorizing documents: {str(e)}")
