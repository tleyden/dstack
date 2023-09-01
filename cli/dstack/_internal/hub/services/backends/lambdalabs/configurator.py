import json
from typing import Dict, List, Optional, Tuple, Union

from requests import HTTPError

from dstack._internal.backend.base import ComponentBasedBackend
from dstack._internal.backend.lambdalabs import LambdaBackend
from dstack._internal.backend.lambdalabs.api_client import LambdaAPIClient
from dstack._internal.backend.lambdalabs.config import LambdaConfig
from dstack._internal.hub.db.models import Backend as DBBackend
from dstack._internal.hub.schemas import (
    BackendElement,
    BackendElementValue,
    BackendInfo,
    BackendMultiElement,
    LambdaBackendConfig,
    LambdaBackendConfigWithCreds,
    LambdaBackendConfigWithCredsPartial,
    LambdaBackendValues,
)
from dstack._internal.hub.services.backends.base import (
    PRIMARY_BACKEND_TYPES,
    BackendConfigError,
    Configurator,
)

REGIONS = [
    "us-south-1",
    "us-west-2",
    "us-west-1",
    "us-midwest-1",
    "us-west-3",
    "us-east-1",
    "australia-southeast-1",
    "europe-central-1",
    "asia-south-1",
    "me-west-1",
    "europe-south-1",
    "asia-northeast-1",
]


class LambdaConfigurator(Configurator):
    NAME = "lambda"

    def configure_backend(
        self, backend_config: LambdaBackendConfigWithCredsPartial, backend_infos: List[BackendInfo]
    ) -> LambdaBackendValues:
        backend_values = LambdaBackendValues()
        if backend_config.api_key is None:
            return backend_values
        self._validate_lambda_api_key(api_key=backend_config.api_key)
        backend_values.regions = self._get_regions_element(selected=backend_config.regions)
        backend_values.primary_backend = self._get_primary_backend_element(
            backend_infos=backend_infos,
            selected=backend_config.primary_backend,
        )
        return backend_values

    def create_backend(
        self, project_name: str, backend_config: LambdaBackendConfigWithCreds
    ) -> Tuple[Dict, Dict]:
        config_data = {
            "regions": backend_config.regions,
        }
        auth_data = {
            "api_key": backend_config.api_key,
        }
        return config_data, auth_data

    def get_backend_config(
        self, db_backend: DBBackend, include_creds: bool
    ) -> Union[LambdaBackendConfig, LambdaBackendConfigWithCreds]:
        config_data = json.loads(db_backend.config)
        if include_creds:
            auth_data = json.loads(db_backend.auth)
            return LambdaBackendConfigWithCreds(
                regions=config_data["regions"],
                api_key=auth_data["api_key"],
            )
        return LambdaBackendConfig(
            regions=config_data["regions"],
        )

    def get_backend(
        self, db_backend: DBBackend, primary_backend: Optional[ComponentBasedBackend]
    ) -> LambdaBackend:
        config_data = json.loads(db_backend.config)
        auth_data = json.loads(db_backend.auth)
        config = LambdaConfig(
            regions=config_data["regions"],
            api_key=auth_data["api_key"],
        )
        return LambdaBackend(config, primary_backend)

    def _validate_lambda_api_key(self, api_key: str):
        client = LambdaAPIClient(api_key=api_key)
        try:
            client.list_instance_types()
        except HTTPError as e:
            if e.response.status_code in [401, 403]:
                raise BackendConfigError(
                    "Invalid credentials",
                    code="invalid_credentials",
                    fields=[["api_key"]],
                )
            raise e

    def _get_regions_element(self, selected: Optional[List[str]]) -> BackendMultiElement:
        if selected is not None:
            for r in selected:
                if r not in REGIONS:
                    raise BackendConfigError(
                        "Invalid regions",
                        code="invalid_regions",
                        fields=[["regions"]],
                    )
        element = BackendMultiElement(
            selected=selected or REGIONS,
            values=[BackendElementValue(value=r, label=r) for r in REGIONS],
        )
        return element

    def _get_primary_backend_element(
        self, backend_infos: List[BackendInfo], selected: Optional[str]
    ) -> BackendElement:
        element = BackendElement(selected=selected)
        for backend_info in backend_infos:
            if backend_info.name in PRIMARY_BACKEND_TYPES:
                element.values.append(
                    BackendElementValue(value=backend_info.name, label=backend_info.name)
                )
        if element.selected is None and len(element.values) > 0:
            element.selected = element.values[0].value
        return element
