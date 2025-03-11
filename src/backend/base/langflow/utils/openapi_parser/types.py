from typing import TypedDict, Dict, List, Any, Optional, Union, Set


class ServerInfo(TypedDict):
    url: str
    description: str


class InfoObject(TypedDict):
    title: str
    version: str


class SchemaProperty(TypedDict):
    type: str
    description: Optional[str]
    format: Optional[str]
    example: Optional[Any]
    nullable: Optional[bool]
    maxLength: Optional[int]
    items: Optional[Dict[str, Any]]
    properties: Optional[Dict[str, 'SchemaProperty']]
    anyOf: Optional[List[Dict[str, Any]]]
    enum: Optional[List[str]]
    additionalProperties: Optional[bool]


class ParameterObject(TypedDict):
    name: str
    in_: str  # 'in' is a Python keyword, so using in_
    description: Optional[str]
    required: Optional[bool]
    schema: SchemaProperty


class MediaTypeObject(TypedDict):
    schema: Union[SchemaProperty, Dict[str, Any]]
    encoding: Optional[Dict[str, Dict[str, str]]]


class ResponseObject(TypedDict):
    description: str
    content: Optional[Dict[str, MediaTypeObject]]


class RequestBodyObject(TypedDict):
    description: Optional[str]
    content: Dict[str, MediaTypeObject]
    required: Optional[bool]


class OperationObject(TypedDict):
    tags: List[str]
    summary: str
    description: Optional[str]
    operationId: Optional[str]
    parameters: Optional[List[ParameterObject]]
    requestBody: Optional[RequestBodyObject]
    responses: Dict[str, ResponseObject]
    security: Optional[List[Dict[str, List[str]]]]
    x_shortName: Optional[str]  # x-shortName in YAML


class PathItemObject(TypedDict):
    get: Optional[OperationObject]
    post: Optional[OperationObject]
    put: Optional[OperationObject]
    delete: Optional[OperationObject]
    patch: Optional[OperationObject]
    parameters: Optional[List[ParameterObject]]


class SchemaObject(TypedDict):
    type: str
    properties: Optional[Dict[str, SchemaProperty]]
    required: Optional[List[str]]
    additionalProperties: Optional[bool]
    description: Optional[str]
    enum: Optional[List[str]]
    oneOf: Optional[List[Dict[str, Any]]]
    items: Optional[Dict[str, Any]]
    format: Optional[str]
    example: Optional[Any]
    nullable: Optional[bool]
    dependencies: Optional[Set[str]]


class SecuritySchemeObject(TypedDict):
    type: str  # apiKey, http, oauth2, openIdConnect
    name: Optional[str]  # Required for apiKey
    in_: Optional[str]  # Required for apiKey
    scheme: Optional[str]  # Required for http
    bearerFormat: Optional[str]  # Optional for http bearer
    flows: Optional[Dict[str, Any]]  # Required for oauth2
    openIdConnectUrl: Optional[str]  # Required for openIdConnect


class ComponentsObject(TypedDict):
    schemas: Dict[str, SchemaObject]
    securitySchemes: Optional[Dict[str, SecuritySchemeObject]]
    responses: Optional[Dict[str, ResponseObject]]
    parameters: Optional[Dict[str, ParameterObject]]
    requestBodies: Optional[Dict[str, RequestBodyObject]]


class TagObject(TypedDict):
    name: str
    description: str
    version: Optional[str]


class OpenAPIDocument(TypedDict):
    openapi: str
    info: InfoObject
    servers: List[ServerInfo]
    paths: Dict[str, PathItemObject]
    components: ComponentsObject
    tags: List[TagObject]
    security: Optional[List[Dict[str, List[str]]]]


class EndpointInfo(TypedDict):
    path: str
    method: str
    summary: str
    version: str
    tags: List[str]
    operationId: str
    source_file: str
    responses: Dict[str, ResponseObject]
    parameters: List[ParameterObject]
    requestBody: Optional[RequestBodyObject]
    components: Optional[Dict[str, SchemaObject]]
    dependencies: Optional[Set[str]]


class TagInfo(TypedDict):
    name: str
    description: str
    version: str
