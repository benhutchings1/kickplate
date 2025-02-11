from abc import ABC, abstractmethod
from kr8s.asyncio.objects import APIObject


from models.base import BaseRequest, BaseResource


class BaseEntityBuilder(ABC):
    @abstractmethod
    def build_resource(self, request: BaseRequest) -> BaseResource:
        """Base method for building resource from request"""
        raise NotImplementedError()

    @abstractmethod
    def build_manifest(self, resource: BaseResource, namespace: str) -> APIObject:
        """Base method for building k8s manifest definition from resource"""
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def get_crd() -> type[APIObject]:
        """Getter for CRD definition"""
        raise NotImplementedError()
