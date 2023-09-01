from typing import Optional

from dstack._internal.backend.aws.logs import AWSLogging
from dstack._internal.backend.aws.secrets import AWSSecretsManager
from dstack._internal.backend.aws.storage import AWSStorage
from dstack._internal.backend.base import ComponentBasedBackend
from dstack._internal.backend.lambdalabs.compute import LambdaCompute
from dstack._internal.backend.lambdalabs.config import LambdaConfig
from dstack._internal.backend.lambdalabs.pricing import LambdaPricing
from dstack._internal.core.instance import InstancePricing
from dstack._internal.core.job import Job


class LambdaBackend(ComponentBasedBackend):
    NAME = "lambda"

    def __init__(
        self,
        backend_config: LambdaConfig,
        primary_backend: ComponentBasedBackend,
    ):
        self.backend_config = backend_config
        self._storage = primary_backend.storage()
        self._secrets_manager = primary_backend.secrets_manager()
        self._logging = primary_backend.logging()
        self._compute = LambdaCompute(lambda_config=self.backend_config)
        self._pricing = LambdaPricing()

    @classmethod
    def load(cls) -> Optional["LambdaBackend"]:
        config = LambdaConfig.load()
        if config is None:
            return None
        return cls(config)

    def storage(self) -> AWSStorage:
        return self._storage

    def compute(self) -> LambdaCompute:
        return self._compute

    def secrets_manager(self) -> AWSSecretsManager:
        return self._secrets_manager

    def logging(self) -> AWSLogging:
        return self._logging

    def pricing(self) -> LambdaPricing:
        return self._pricing

    def run_job(
        self,
        job: Job,
        project_private_key: str,
        offer: InstancePricing,
    ):
        self._logging.create_log_groups_if_not_exist(
            self.backend_config.storage_config.bucket, job.repo_ref.repo_id
        )
        super().run_job(
            job,
            project_private_key=project_private_key,
            offer=offer,
        )
