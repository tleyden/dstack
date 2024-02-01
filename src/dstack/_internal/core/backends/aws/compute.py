from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional

import boto3
import botocore.client
import botocore.exceptions

import dstack._internal.core.backends.aws.resources as aws_resources
import dstack.version as version
from dstack._internal import settings
from dstack._internal.core.backends.aws.config import AWSConfig
from dstack._internal.core.backends.base.compute import (
    Compute,
    InstanceConfiguration,
    get_gateway_user_data,
    get_instance_name,
    get_instance_user_data,
    get_user_data,
)
from dstack._internal.core.backends.base.offers import get_catalog_offers
from dstack._internal.core.errors import NoCapacityError
from dstack._internal.core.models.backends.aws import AWSAccessKeyCreds
from dstack._internal.core.models.backends.base import BackendType
from dstack._internal.core.models.instances import (
    InstanceAvailability,
    InstanceOffer,
    InstanceOfferWithAvailability,
    LaunchedGatewayInfo,
    LaunchedInstanceInfo,
)
from dstack._internal.core.models.runs import Job, Requirements, Run
from dstack._internal.server.models import ProjectModel, UserModel
from dstack._internal.utils.logging import get_logger

logger = get_logger(__name__)


class AWSCompute(Compute):
    def __init__(self, config: AWSConfig):
        self.config = config
        if isinstance(config.creds, AWSAccessKeyCreds):
            self.session = boto3.Session(
                aws_access_key_id=config.creds.access_key,
                aws_secret_access_key=config.creds.secret_key,
            )
        else:  # default creds
            self.session = boto3.Session()

    def get_offers(
        self, requirements: Optional[Requirements] = None
    ) -> List[InstanceOfferWithAvailability]:
        offers = get_catalog_offers(
            backend=BackendType.AWS,
            locations=self.config.regions,
            requirements=requirements,
            extra_filter=_supported_instances,
        )
        regions = set(i.region for i in offers)

        def get_quotas(client: botocore.client.BaseClient) -> Dict[str, int]:
            region_quotas = {}
            for page in client.get_paginator("list_service_quotas").paginate(ServiceCode="ec2"):
                for q in page["Quotas"]:
                    if "On-Demand" in q["QuotaName"]:
                        region_quotas[q["UsageMetric"]["MetricDimensions"]["Class"]] = q["Value"]
            return region_quotas

        quotas = {}
        with ThreadPoolExecutor(max_workers=8) as executor:
            future_to_region = {}
            for region in regions:
                future = executor.submit(
                    get_quotas, self.session.client("service-quotas", region_name=region)
                )
                future_to_region[future] = region
            for future in as_completed(future_to_region):
                quotas[future_to_region[future]] = future.result()

        availability_offers = []
        for offer in offers:
            availability = InstanceAvailability.UNKNOWN
            if not _has_quota(quotas[offer.region], offer.instance.name):
                availability = InstanceAvailability.NO_QUOTA
            availability_offers.append(
                InstanceOfferWithAvailability(**offer.dict(), availability=availability)
            )
        return availability_offers

    def terminate_instance(
        self, instance_id: str, region: str, backend_data: Optional[str] = None
    ) -> None:
        client = self.session.client("ec2", region_name=region)
        try:
            client.terminate_instances(InstanceIds=[instance_id])
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "InvalidInstanceID.NotFound":
                pass
            else:
                raise e

    def create_instance(
        self,
        project: ProjectModel,
        user: UserModel,
        instance_offer: InstanceOfferWithAvailability,
        instance_config: InstanceConfiguration,
    ) -> LaunchedInstanceInfo:
        project_id = project.name
        ec2 = self.session.resource("ec2", region_name=instance_offer.region)
        ec2_client = self.session.client("ec2", region_name=instance_offer.region)
        iam_client = self.session.client("iam", region_name=instance_offer.region)

        tags = [
            {"Key": "Name", "Value": instance_config.instance_name},
            {"Key": "owner", "Value": "dstack"},
            {"Key": "dstack_project", "Value": project_id},
            {"Key": "dstack_user", "Value": instance_config.user},
        ]
        try:
            disk_size = round(instance_offer.instance.resources.disk.size_mib / 1024)
            response = ec2.create_instances(
                **aws_resources.create_instances_struct(
                    disk_size=disk_size,
                    image_id=aws_resources.get_image_id(
                        ec2_client, len(instance_offer.instance.resources.gpus) > 0
                    ),
                    instance_type=instance_offer.instance.name,
                    iam_instance_profile_arn=aws_resources.create_iam_instance_profile(
                        iam_client, project_id
                    ),
                    user_data=get_instance_user_data(
                        authorized_keys=instance_config.get_public_keys(),
                    ),
                    tags=tags,
                    security_group_id=aws_resources.create_security_group(ec2_client, project_id),
                    spot=instance_offer.instance.resources.spot,
                )
            )
            instance = response[0]
            instance.wait_until_running()
            instance.reload()  # populate instance.public_ip_address

            if instance_offer.instance.resources.spot:  # it will not terminate the instance
                ec2_client.cancel_spot_instance_requests(
                    SpotInstanceRequestIds=[instance.spot_instance_request_id]
                )
            return LaunchedInstanceInfo(
                instance_id=instance.instance_id,
                ip_address=instance.public_ip_address,
                region=instance_offer.region,
                username="ubuntu",
                ssh_port=22,
                dockerized=True,  # because `dstack-shim docker` is used
            )
        except botocore.exceptions.ClientError as e:
            logger.warning("Got botocore.exceptions.ClientError: %s", e)
            raise NoCapacityError()

    def run_job(
        self,
        run: Run,
        job: Job,
        instance_offer: InstanceOfferWithAvailability,
        project_ssh_public_key: str,
        project_ssh_private_key: str,
    ) -> LaunchedInstanceInfo:
        project_id = run.project_name
        ec2 = self.session.resource("ec2", region_name=instance_offer.region)
        ec2_client = self.session.client("ec2", region_name=instance_offer.region)
        iam_client = self.session.client("iam", region_name=instance_offer.region)

        tags = [
            {"Key": "Name", "Value": get_instance_name(run, job)},
            {"Key": "owner", "Value": "dstack"},
            {"Key": "dstack_project", "Value": project_id},
            {"Key": "dstack_user", "Value": run.user},
        ]
        try:
            disk_size = round(instance_offer.instance.resources.disk.size_mib / 1024)
            response = ec2.create_instances(
                **aws_resources.create_instances_struct(
                    disk_size=disk_size,
                    image_id=aws_resources.get_image_id(
                        ec2_client, len(instance_offer.instance.resources.gpus) > 0
                    ),
                    instance_type=instance_offer.instance.name,
                    iam_instance_profile_arn=aws_resources.create_iam_instance_profile(
                        iam_client, project_id
                    ),
                    user_data=get_user_data(
                        backend=BackendType.AWS,
                        image_name=job.job_spec.image_name,
                        authorized_keys=[
                            run.run_spec.ssh_key_pub.strip(),
                            project_ssh_public_key.strip(),
                        ],
                        registry_auth_required=job.job_spec.registry_auth is not None,
                    ),
                    tags=tags,
                    security_group_id=aws_resources.create_security_group(ec2_client, project_id),
                    spot=instance_offer.instance.resources.spot,
                )
            )
            instance = response[0]
            instance.wait_until_running()
            instance.reload()  # populate instance.public_ip_address

            if instance_offer.instance.resources.spot:  # it will not terminate the instance
                ec2_client.cancel_spot_instance_requests(
                    SpotInstanceRequestIds=[instance.spot_instance_request_id]
                )
            return LaunchedInstanceInfo(
                instance_id=instance.instance_id,
                ip_address=instance.public_ip_address,
                region=instance_offer.region,
                username="ubuntu",
                ssh_port=22,
                dockerized=True,  # because `dstack-shim docker` is used
                backend_data=None,
            )
        except botocore.exceptions.ClientError as e:
            logger.warning("Got botocore.exceptions.ClientError: %s", e)
            raise NoCapacityError()

    def create_gateway(
        self,
        instance_name: str,
        ssh_key_pub: str,
        region: str,
        project_id: str,
    ) -> LaunchedGatewayInfo:
        ec2 = self.session.resource("ec2", region_name=region)
        ec2_client = self.session.client("ec2", region_name=region)
        tags = [
            {"Key": "Name", "Value": instance_name},
            {"Key": "owner", "Value": "dstack"},
            {"Key": "dstack_project", "Value": project_id},
        ]
        if settings.DSTACK_VERSION is not None:
            tags.append({"Key": "dstack_version", "Value": settings.DSTACK_VERSION})
        response = ec2.create_instances(
            **aws_resources.create_instances_struct(
                disk_size=10,
                image_id=aws_resources.get_gateway_image_id(ec2_client),
                instance_type="t2.micro",
                iam_instance_profile_arn=None,
                user_data=get_gateway_user_data(ssh_key_pub),
                tags=tags,
                security_group_id=aws_resources.create_gateway_security_group(
                    ec2_client, project_id
                ),
                spot=False,
            )
        )
        instance = response[0]
        instance.wait_until_running()
        instance.reload()  # populate instance.public_ip_address

        return LaunchedGatewayInfo(
            instance_id=instance.instance_id,
            region=region,
            ip_address=instance.public_ip_address,
        )


def _has_quota(quotas: Dict[str, int], instance_name: str) -> bool:
    if instance_name.startswith("p"):
        return quotas.get("P/OnDemand", 0) > 0
    if instance_name.startswith("g"):
        return quotas.get("G/OnDemand", 0) > 0
    return quotas.get("Standard/OnDemand", 0) > 0


def _supported_instances(offer: InstanceOffer) -> bool:
    for family in ["t2.small", "c5.", "m5.", "p3.", "g5.", "g4dn.", "p4d.", "p4de."]:
        if offer.instance.name.startswith(family):
            return True
    return False
