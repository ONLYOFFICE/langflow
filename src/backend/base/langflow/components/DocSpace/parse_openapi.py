import yaml
import copy

from typing import List, Dict
from langchain_core.documents import Document
from langflow.custom import Component
from langflow.inputs.inputs import DataInput
from langflow.io import Output
from langflow.schema import Data


from langflow.utils.openapi_parser.main import Parser
from langflow.utils.openapi_parser.types import EndpointInfo, SchemaObject, TagInfo


class OpenAPIParserComponent(Component):
    display_name: str = "Parse OpenAPI"
    description: str = "Parse an OpenAPI schema and return a parsed data object."
    name: str = "OpenAPIParser"
    icon = "braces"

    inputs = [
        DataInput(
            name="openapi_spec",
            display_name="OpenAPI Spec",
            info="The OpenAPI specification to parse. Can be in YAML or JSON format.",
            required=True,
        ),
    ]

    outputs = [
        Output(display_name="Endpoints",
               name="endpoints", method="prepare_endpoints"),
        Output(display_name="Tags",
               name="tags", method="prepare_tags"),
    ]

    def prepare_endpoints(self) -> Data:
        endpoints, _, _ = self._parse()

        docs = {}

        for i, endpoint in enumerate(endpoints["endpoints"].values()):
            del endpoint["dependencies"]
            doc = Document(
                page_content=endpoint.get("summary", ""),
                metadata={
                    "name": f"{endpoint['path']}_{endpoint['method']}",
                    "method": endpoint["method"],
                    "path": endpoint["path"],
                    "content": endpoint
                })
            docs[f'endpoint-{i}'] = doc

        data = Data(
            data=docs
        )

        return data

    def prepare_tags(self) -> Data:
        endpoints, tags, _ = self._parse()

        docs = {}

        for tag in tags:
            tag_content = tag.get("description", "")
            tag_content += " "
            for endpoint in endpoints.get("endpoints", {}).values():
                if endpoint.get("tags", []).count(tag.get("name")) == 0:
                    continue

                tag_content += endpoint.get('summary', '')
                tag_content += " "

            doc = Document(page_content=tag_content,
                           metadata={"name": tag.get("name")})
            docs[tag.get("name")] = doc

        data = Data(
            data=docs
        )

        return data

    def _parse(self):
        specs: List[Data] = self.openapi_spec
        files = [spec.get_text() for spec in specs]
        yml_files = [yaml.safe_load(file) for file in files]
        parsed_files = [Parser.parse(file) for file in yml_files]

        endpoints: Dict[str, Dict[str, EndpointInfo]] = {}
        endpoints["endpoints"] = {}

        tags: List[TagInfo] = []
        components: Dict[str, SchemaObject] = {}

        for file in parsed_files:
            file_endpoints: Dict[str, EndpointInfo] = copy.deepcopy(
                file.get("endpoints", {}))
            file_tags: List[TagInfo] = file.get("tags", [])
            file_components: Dict[str, SchemaObject] = file.get(
                "components", {})

            endpoints["endpoints"].update(file_endpoints)
            tags.extend(file_tags)
            components.update(file_components)

        return copy.deepcopy(endpoints), tags, components
