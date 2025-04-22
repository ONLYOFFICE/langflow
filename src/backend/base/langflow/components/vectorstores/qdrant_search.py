from typing import Any, Dict, List, Optional
from langchain.embeddings.base import Embeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client.models import Filter
from langflow.custom import Component
from langflow.schema import Message
from langflow.io import (
    MessageInput,
    DataInput,
    Output,
)

from langflow.utils.qdrant import get_qdrant_client, check_collection_exists, qdrant_inputs


class QdrantSearchFileComponent(Component):
    display_name = "Qdrant Search File"
    description = "Search in Qdrant Vector Store"
    icon = "Qdrant"

    inputs = [
        *qdrant_inputs,
        MessageInput(
            name="question",
            display_name="Question",
        ),
        DataInput(
            name="files",
            display_name="Files",
            list=True
        ),
    ]

    outputs = [
        Output(name="search",
               display_name="Search",
               method="search_documents"),
    ]

    def build_vector_store(self) -> Optional[Qdrant]:
        try:
            collection_name: str = self.collection_name.get_text()
            embedding: Embeddings = self.embedding

            client = get_qdrant_client(
                self.qdrant_host.get_text(), self.qdrant_port.get_text())

            if not check_collection_exists(client, collection_name):
                return None

            qdrant = Qdrant(client=client,
                            embeddings=embedding,
                            collection_name=collection_name)

            return qdrant

        except Exception as e:
            raise Exception(f"Error building vector store: {str(e)}")

    def search_documents(self) -> Message:

        question: str = self.question.get_text()

        if not question:
            return Message(text="No question provided")

        qdrant = self.build_vector_store()

        if not qdrant:
            return Message(text="No qdrant collection found")

        if not self.files:
            docs = qdrant.similarity_search(
                query=question,
                k=5
            )

            return Message(text="\n".join(f'{item.metadata.get('id')}:{item.metadata.get('title')}\n{item.page_content}\n\n' for item in docs))

        files: List[Dict[str, Any]] = [item.data for item in self.files]

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

        return Message(text="\n".join(f'{item.metadata.get('id')}:{item.metadata.get('title')}\n{item.page_content}\n\n' for item in docs))
