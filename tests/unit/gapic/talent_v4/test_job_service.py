# -*- coding: utf-8 -*-

# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import mock

import grpc
from grpc.experimental import aio
import math
import pytest
from proto.marshal.rules.dates import DurationRule, TimestampRule

from google import auth
from google.api_core import client_options
from google.api_core import exceptions
from google.api_core import future
from google.api_core import gapic_v1
from google.api_core import grpc_helpers
from google.api_core import grpc_helpers_async
from google.api_core import operation_async  # type: ignore
from google.api_core import operations_v1
from google.auth import credentials
from google.auth.exceptions import MutualTLSChannelError
from google.cloud.talent_v4.services.job_service import JobServiceAsyncClient
from google.cloud.talent_v4.services.job_service import JobServiceClient
from google.cloud.talent_v4.services.job_service import pagers
from google.cloud.talent_v4.services.job_service import transports
from google.cloud.talent_v4.types import common
from google.cloud.talent_v4.types import filters
from google.cloud.talent_v4.types import histogram
from google.cloud.talent_v4.types import job
from google.cloud.talent_v4.types import job as gct_job
from google.cloud.talent_v4.types import job_service
from google.longrunning import operations_pb2
from google.oauth2 import service_account
from google.protobuf import duration_pb2 as duration  # type: ignore
from google.protobuf import field_mask_pb2 as field_mask  # type: ignore
from google.protobuf import timestamp_pb2 as timestamp  # type: ignore
from google.protobuf import wrappers_pb2 as wrappers  # type: ignore
from google.type import latlng_pb2 as latlng  # type: ignore
from google.type import money_pb2 as money  # type: ignore
from google.type import postal_address_pb2 as gt_postal_address  # type: ignore
from google.type import timeofday_pb2 as timeofday  # type: ignore


def client_cert_source_callback():
    return b"cert bytes", b"key bytes"


# If default endpoint is localhost, then default mtls endpoint will be the same.
# This method modifies the default endpoint so the client can produce a different
# mtls endpoint for endpoint testing purposes.
def modify_default_endpoint(client):
    return (
        "foo.googleapis.com"
        if ("localhost" in client.DEFAULT_ENDPOINT)
        else client.DEFAULT_ENDPOINT
    )


def test__get_default_mtls_endpoint():
    api_endpoint = "example.googleapis.com"
    api_mtls_endpoint = "example.mtls.googleapis.com"
    sandbox_endpoint = "example.sandbox.googleapis.com"
    sandbox_mtls_endpoint = "example.mtls.sandbox.googleapis.com"
    non_googleapi = "api.example.com"

    assert JobServiceClient._get_default_mtls_endpoint(None) is None
    assert (
        JobServiceClient._get_default_mtls_endpoint(api_endpoint) == api_mtls_endpoint
    )
    assert (
        JobServiceClient._get_default_mtls_endpoint(api_mtls_endpoint)
        == api_mtls_endpoint
    )
    assert (
        JobServiceClient._get_default_mtls_endpoint(sandbox_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        JobServiceClient._get_default_mtls_endpoint(sandbox_mtls_endpoint)
        == sandbox_mtls_endpoint
    )
    assert JobServiceClient._get_default_mtls_endpoint(non_googleapi) == non_googleapi


@pytest.mark.parametrize("client_class", [JobServiceClient, JobServiceAsyncClient])
def test_job_service_client_from_service_account_file(client_class):
    creds = credentials.AnonymousCredentials()
    with mock.patch.object(
        service_account.Credentials, "from_service_account_file"
    ) as factory:
        factory.return_value = creds
        client = client_class.from_service_account_file("dummy/file/path.json")
        assert client._transport._credentials == creds

        client = client_class.from_service_account_json("dummy/file/path.json")
        assert client._transport._credentials == creds

        assert client._transport._host == "jobs.googleapis.com:443"


def test_job_service_client_get_transport_class():
    transport = JobServiceClient.get_transport_class()
    assert transport == transports.JobServiceGrpcTransport

    transport = JobServiceClient.get_transport_class("grpc")
    assert transport == transports.JobServiceGrpcTransport


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (JobServiceClient, transports.JobServiceGrpcTransport, "grpc"),
        (
            JobServiceAsyncClient,
            transports.JobServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
@mock.patch.object(
    JobServiceClient, "DEFAULT_ENDPOINT", modify_default_endpoint(JobServiceClient)
)
@mock.patch.object(
    JobServiceAsyncClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(JobServiceAsyncClient),
)
def test_job_service_client_client_options(
    client_class, transport_class, transport_name
):
    # Check that if channel is provided we won't create a new one.
    with mock.patch.object(JobServiceClient, "get_transport_class") as gtc:
        transport = transport_class(credentials=credentials.AnonymousCredentials())
        client = client_class(transport=transport)
        gtc.assert_not_called()

    # Check that if channel is provided via str we will create a new one.
    with mock.patch.object(JobServiceClient, "get_transport_class") as gtc:
        client = client_class(transport=transport_name)
        gtc.assert_called()

    # Check the case api_endpoint is provided.
    options = client_options.ClientOptions(api_endpoint="squid.clam.whelk")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host="squid.clam.whelk",
            scopes=None,
            ssl_channel_credentials=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT is
    # "never".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "never"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class()
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_ENDPOINT,
                scopes=None,
                ssl_channel_credentials=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
            )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT is
    # "always".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "always"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class()
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_MTLS_ENDPOINT,
                scopes=None,
                ssl_channel_credentials=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
            )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT has
    # unsupported value.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "Unsupported"}):
        with pytest.raises(MutualTLSChannelError):
            client = client_class()

    # Check the case GOOGLE_API_USE_CLIENT_CERTIFICATE has unsupported value.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "Unsupported"}
    ):
        with pytest.raises(ValueError):
            client = client_class()

    # Check the case quota_project_id is provided
    options = client_options.ClientOptions(quota_project_id="octopus")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            ssl_channel_credentials=None,
            quota_project_id="octopus",
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name,use_client_cert_env",
    [
        (JobServiceClient, transports.JobServiceGrpcTransport, "grpc", "true"),
        (
            JobServiceAsyncClient,
            transports.JobServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            "true",
        ),
        (JobServiceClient, transports.JobServiceGrpcTransport, "grpc", "false"),
        (
            JobServiceAsyncClient,
            transports.JobServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            "false",
        ),
    ],
)
@mock.patch.object(
    JobServiceClient, "DEFAULT_ENDPOINT", modify_default_endpoint(JobServiceClient)
)
@mock.patch.object(
    JobServiceAsyncClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(JobServiceAsyncClient),
)
@mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "auto"})
def test_job_service_client_mtls_env_auto(
    client_class, transport_class, transport_name, use_client_cert_env
):
    # This tests the endpoint autoswitch behavior. Endpoint is autoswitched to the default
    # mtls endpoint, if GOOGLE_API_USE_CLIENT_CERTIFICATE is "true" and client cert exists.

    # Check the case client_cert_source is provided. Whether client cert is used depends on
    # GOOGLE_API_USE_CLIENT_CERTIFICATE value.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}
    ):
        options = client_options.ClientOptions(
            client_cert_source=client_cert_source_callback
        )
        with mock.patch.object(transport_class, "__init__") as patched:
            ssl_channel_creds = mock.Mock()
            with mock.patch(
                "grpc.ssl_channel_credentials", return_value=ssl_channel_creds
            ):
                patched.return_value = None
                client = client_class(client_options=options)

                if use_client_cert_env == "false":
                    expected_ssl_channel_creds = None
                    expected_host = client.DEFAULT_ENDPOINT
                else:
                    expected_ssl_channel_creds = ssl_channel_creds
                    expected_host = client.DEFAULT_MTLS_ENDPOINT

                patched.assert_called_once_with(
                    credentials=None,
                    credentials_file=None,
                    host=expected_host,
                    scopes=None,
                    ssl_channel_credentials=expected_ssl_channel_creds,
                    quota_project_id=None,
                    client_info=transports.base.DEFAULT_CLIENT_INFO,
                )

    # Check the case ADC client cert is provided. Whether client cert is used depends on
    # GOOGLE_API_USE_CLIENT_CERTIFICATE value.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}
    ):
        with mock.patch.object(transport_class, "__init__") as patched:
            with mock.patch(
                "google.auth.transport.grpc.SslCredentials.__init__", return_value=None
            ):
                with mock.patch(
                    "google.auth.transport.grpc.SslCredentials.is_mtls",
                    new_callable=mock.PropertyMock,
                ) as is_mtls_mock:
                    with mock.patch(
                        "google.auth.transport.grpc.SslCredentials.ssl_credentials",
                        new_callable=mock.PropertyMock,
                    ) as ssl_credentials_mock:
                        if use_client_cert_env == "false":
                            is_mtls_mock.return_value = False
                            ssl_credentials_mock.return_value = None
                            expected_host = client.DEFAULT_ENDPOINT
                            expected_ssl_channel_creds = None
                        else:
                            is_mtls_mock.return_value = True
                            ssl_credentials_mock.return_value = mock.Mock()
                            expected_host = client.DEFAULT_MTLS_ENDPOINT
                            expected_ssl_channel_creds = (
                                ssl_credentials_mock.return_value
                            )

                        patched.return_value = None
                        client = client_class()
                        patched.assert_called_once_with(
                            credentials=None,
                            credentials_file=None,
                            host=expected_host,
                            scopes=None,
                            ssl_channel_credentials=expected_ssl_channel_creds,
                            quota_project_id=None,
                            client_info=transports.base.DEFAULT_CLIENT_INFO,
                        )

    # Check the case client_cert_source and ADC client cert are not provided.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}
    ):
        with mock.patch.object(transport_class, "__init__") as patched:
            with mock.patch(
                "google.auth.transport.grpc.SslCredentials.__init__", return_value=None
            ):
                with mock.patch(
                    "google.auth.transport.grpc.SslCredentials.is_mtls",
                    new_callable=mock.PropertyMock,
                ) as is_mtls_mock:
                    is_mtls_mock.return_value = False
                    patched.return_value = None
                    client = client_class()
                    patched.assert_called_once_with(
                        credentials=None,
                        credentials_file=None,
                        host=client.DEFAULT_ENDPOINT,
                        scopes=None,
                        ssl_channel_credentials=None,
                        quota_project_id=None,
                        client_info=transports.base.DEFAULT_CLIENT_INFO,
                    )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (JobServiceClient, transports.JobServiceGrpcTransport, "grpc"),
        (
            JobServiceAsyncClient,
            transports.JobServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
def test_job_service_client_client_options_scopes(
    client_class, transport_class, transport_name
):
    # Check the case scopes are provided.
    options = client_options.ClientOptions(scopes=["1", "2"],)
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_ENDPOINT,
            scopes=["1", "2"],
            ssl_channel_credentials=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (JobServiceClient, transports.JobServiceGrpcTransport, "grpc"),
        (
            JobServiceAsyncClient,
            transports.JobServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
def test_job_service_client_client_options_credentials_file(
    client_class, transport_class, transport_name
):
    # Check the case credentials file is provided.
    options = client_options.ClientOptions(credentials_file="credentials.json")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file="credentials.json",
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            ssl_channel_credentials=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


def test_job_service_client_client_options_from_dict():
    with mock.patch(
        "google.cloud.talent_v4.services.job_service.transports.JobServiceGrpcTransport.__init__"
    ) as grpc_transport:
        grpc_transport.return_value = None
        client = JobServiceClient(client_options={"api_endpoint": "squid.clam.whelk"})
        grpc_transport.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host="squid.clam.whelk",
            scopes=None,
            ssl_channel_credentials=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


def test_create_job(transport: str = "grpc", request_type=job_service.CreateJobRequest):
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.create_job), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gct_job.Job(
            name="name_value",
            company="company_value",
            requisition_id="requisition_id_value",
            title="title_value",
            description="description_value",
            addresses=["addresses_value"],
            job_benefits=[common.JobBenefit.CHILD_CARE],
            degree_types=[common.DegreeType.PRIMARY_EDUCATION],
            department="department_value",
            employment_types=[common.EmploymentType.FULL_TIME],
            incentives="incentives_value",
            language_code="language_code_value",
            job_level=common.JobLevel.ENTRY_LEVEL,
            promotion_value=1635,
            qualifications="qualifications_value",
            responsibilities="responsibilities_value",
            posting_region=common.PostingRegion.ADMINISTRATIVE_AREA,
            visibility=common.Visibility.ACCOUNT_ONLY,
            company_display_name="company_display_name_value",
        )

        response = client.create_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == job_service.CreateJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gct_job.Job)

    assert response.name == "name_value"

    assert response.company == "company_value"

    assert response.requisition_id == "requisition_id_value"

    assert response.title == "title_value"

    assert response.description == "description_value"

    assert response.addresses == ["addresses_value"]

    assert response.job_benefits == [common.JobBenefit.CHILD_CARE]

    assert response.degree_types == [common.DegreeType.PRIMARY_EDUCATION]

    assert response.department == "department_value"

    assert response.employment_types == [common.EmploymentType.FULL_TIME]

    assert response.incentives == "incentives_value"

    assert response.language_code == "language_code_value"

    assert response.job_level == common.JobLevel.ENTRY_LEVEL

    assert response.promotion_value == 1635

    assert response.qualifications == "qualifications_value"

    assert response.responsibilities == "responsibilities_value"

    assert response.posting_region == common.PostingRegion.ADMINISTRATIVE_AREA

    assert response.visibility == common.Visibility.ACCOUNT_ONLY

    assert response.company_display_name == "company_display_name_value"


def test_create_job_from_dict():
    test_create_job(request_type=dict)


@pytest.mark.asyncio
async def test_create_job_async(transport: str = "grpc_asyncio"):
    client = JobServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = job_service.CreateJobRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gct_job.Job(
                name="name_value",
                company="company_value",
                requisition_id="requisition_id_value",
                title="title_value",
                description="description_value",
                addresses=["addresses_value"],
                job_benefits=[common.JobBenefit.CHILD_CARE],
                degree_types=[common.DegreeType.PRIMARY_EDUCATION],
                department="department_value",
                employment_types=[common.EmploymentType.FULL_TIME],
                incentives="incentives_value",
                language_code="language_code_value",
                job_level=common.JobLevel.ENTRY_LEVEL,
                promotion_value=1635,
                qualifications="qualifications_value",
                responsibilities="responsibilities_value",
                posting_region=common.PostingRegion.ADMINISTRATIVE_AREA,
                visibility=common.Visibility.ACCOUNT_ONLY,
                company_display_name="company_display_name_value",
            )
        )

        response = await client.create_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gct_job.Job)

    assert response.name == "name_value"

    assert response.company == "company_value"

    assert response.requisition_id == "requisition_id_value"

    assert response.title == "title_value"

    assert response.description == "description_value"

    assert response.addresses == ["addresses_value"]

    assert response.job_benefits == [common.JobBenefit.CHILD_CARE]

    assert response.degree_types == [common.DegreeType.PRIMARY_EDUCATION]

    assert response.department == "department_value"

    assert response.employment_types == [common.EmploymentType.FULL_TIME]

    assert response.incentives == "incentives_value"

    assert response.language_code == "language_code_value"

    assert response.job_level == common.JobLevel.ENTRY_LEVEL

    assert response.promotion_value == 1635

    assert response.qualifications == "qualifications_value"

    assert response.responsibilities == "responsibilities_value"

    assert response.posting_region == common.PostingRegion.ADMINISTRATIVE_AREA

    assert response.visibility == common.Visibility.ACCOUNT_ONLY

    assert response.company_display_name == "company_display_name_value"


def test_create_job_field_headers():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.CreateJobRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.create_job), "__call__") as call:
        call.return_value = gct_job.Job()

        client.create_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_job_field_headers_async():
    client = JobServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.CreateJobRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_job), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(gct_job.Job())

        await client.create_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_create_job_flattened():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.create_job), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gct_job.Job()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_job(
            parent="parent_value", job=gct_job.Job(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].job == gct_job.Job(name="name_value")


def test_create_job_flattened_error():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_job(
            job_service.CreateJobRequest(),
            parent="parent_value",
            job=gct_job.Job(name="name_value"),
        )


@pytest.mark.asyncio
async def test_create_job_flattened_async():
    client = JobServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gct_job.Job()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(gct_job.Job())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_job(
            parent="parent_value", job=gct_job.Job(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].job == gct_job.Job(name="name_value")


@pytest.mark.asyncio
async def test_create_job_flattened_error_async():
    client = JobServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_job(
            job_service.CreateJobRequest(),
            parent="parent_value",
            job=gct_job.Job(name="name_value"),
        )


def test_batch_create_jobs(
    transport: str = "grpc", request_type=job_service.BatchCreateJobsRequest
):
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.batch_create_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")

        response = client.batch_create_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == job_service.BatchCreateJobsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_batch_create_jobs_from_dict():
    test_batch_create_jobs(request_type=dict)


@pytest.mark.asyncio
async def test_batch_create_jobs_async(transport: str = "grpc_asyncio"):
    client = JobServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = job_service.BatchCreateJobsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.batch_create_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )

        response = await client.batch_create_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_batch_create_jobs_field_headers():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.BatchCreateJobsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.batch_create_jobs), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")

        client.batch_create_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_batch_create_jobs_field_headers_async():
    client = JobServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.BatchCreateJobsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.batch_create_jobs), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )

        await client.batch_create_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_batch_create_jobs_flattened():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.batch_create_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.batch_create_jobs(
            parent="parent_value", jobs=[job.Job(name="name_value")],
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].jobs == [job.Job(name="name_value")]


def test_batch_create_jobs_flattened_error():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.batch_create_jobs(
            job_service.BatchCreateJobsRequest(),
            parent="parent_value",
            jobs=[job.Job(name="name_value")],
        )


@pytest.mark.asyncio
async def test_batch_create_jobs_flattened_async():
    client = JobServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.batch_create_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.batch_create_jobs(
            parent="parent_value", jobs=[job.Job(name="name_value")],
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].jobs == [job.Job(name="name_value")]


@pytest.mark.asyncio
async def test_batch_create_jobs_flattened_error_async():
    client = JobServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.batch_create_jobs(
            job_service.BatchCreateJobsRequest(),
            parent="parent_value",
            jobs=[job.Job(name="name_value")],
        )


def test_get_job(transport: str = "grpc", request_type=job_service.GetJobRequest):
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_job), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = job.Job(
            name="name_value",
            company="company_value",
            requisition_id="requisition_id_value",
            title="title_value",
            description="description_value",
            addresses=["addresses_value"],
            job_benefits=[common.JobBenefit.CHILD_CARE],
            degree_types=[common.DegreeType.PRIMARY_EDUCATION],
            department="department_value",
            employment_types=[common.EmploymentType.FULL_TIME],
            incentives="incentives_value",
            language_code="language_code_value",
            job_level=common.JobLevel.ENTRY_LEVEL,
            promotion_value=1635,
            qualifications="qualifications_value",
            responsibilities="responsibilities_value",
            posting_region=common.PostingRegion.ADMINISTRATIVE_AREA,
            visibility=common.Visibility.ACCOUNT_ONLY,
            company_display_name="company_display_name_value",
        )

        response = client.get_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == job_service.GetJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, job.Job)

    assert response.name == "name_value"

    assert response.company == "company_value"

    assert response.requisition_id == "requisition_id_value"

    assert response.title == "title_value"

    assert response.description == "description_value"

    assert response.addresses == ["addresses_value"]

    assert response.job_benefits == [common.JobBenefit.CHILD_CARE]

    assert response.degree_types == [common.DegreeType.PRIMARY_EDUCATION]

    assert response.department == "department_value"

    assert response.employment_types == [common.EmploymentType.FULL_TIME]

    assert response.incentives == "incentives_value"

    assert response.language_code == "language_code_value"

    assert response.job_level == common.JobLevel.ENTRY_LEVEL

    assert response.promotion_value == 1635

    assert response.qualifications == "qualifications_value"

    assert response.responsibilities == "responsibilities_value"

    assert response.posting_region == common.PostingRegion.ADMINISTRATIVE_AREA

    assert response.visibility == common.Visibility.ACCOUNT_ONLY

    assert response.company_display_name == "company_display_name_value"


def test_get_job_from_dict():
    test_get_job(request_type=dict)


@pytest.mark.asyncio
async def test_get_job_async(transport: str = "grpc_asyncio"):
    client = JobServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = job_service.GetJobRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._client._transport.get_job), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            job.Job(
                name="name_value",
                company="company_value",
                requisition_id="requisition_id_value",
                title="title_value",
                description="description_value",
                addresses=["addresses_value"],
                job_benefits=[common.JobBenefit.CHILD_CARE],
                degree_types=[common.DegreeType.PRIMARY_EDUCATION],
                department="department_value",
                employment_types=[common.EmploymentType.FULL_TIME],
                incentives="incentives_value",
                language_code="language_code_value",
                job_level=common.JobLevel.ENTRY_LEVEL,
                promotion_value=1635,
                qualifications="qualifications_value",
                responsibilities="responsibilities_value",
                posting_region=common.PostingRegion.ADMINISTRATIVE_AREA,
                visibility=common.Visibility.ACCOUNT_ONLY,
                company_display_name="company_display_name_value",
            )
        )

        response = await client.get_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, job.Job)

    assert response.name == "name_value"

    assert response.company == "company_value"

    assert response.requisition_id == "requisition_id_value"

    assert response.title == "title_value"

    assert response.description == "description_value"

    assert response.addresses == ["addresses_value"]

    assert response.job_benefits == [common.JobBenefit.CHILD_CARE]

    assert response.degree_types == [common.DegreeType.PRIMARY_EDUCATION]

    assert response.department == "department_value"

    assert response.employment_types == [common.EmploymentType.FULL_TIME]

    assert response.incentives == "incentives_value"

    assert response.language_code == "language_code_value"

    assert response.job_level == common.JobLevel.ENTRY_LEVEL

    assert response.promotion_value == 1635

    assert response.qualifications == "qualifications_value"

    assert response.responsibilities == "responsibilities_value"

    assert response.posting_region == common.PostingRegion.ADMINISTRATIVE_AREA

    assert response.visibility == common.Visibility.ACCOUNT_ONLY

    assert response.company_display_name == "company_display_name_value"


def test_get_job_field_headers():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.GetJobRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_job), "__call__") as call:
        call.return_value = job.Job()

        client.get_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_job_field_headers_async():
    client = JobServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.GetJobRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._client._transport.get_job), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(job.Job())

        await client.get_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_job_flattened():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_job), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = job.Job()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_job(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_get_job_flattened_error():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_job(
            job_service.GetJobRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_get_job_flattened_async():
    client = JobServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._client._transport.get_job), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = job.Job()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(job.Job())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_job(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_get_job_flattened_error_async():
    client = JobServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_job(
            job_service.GetJobRequest(), name="name_value",
        )


def test_update_job(transport: str = "grpc", request_type=job_service.UpdateJobRequest):
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.update_job), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gct_job.Job(
            name="name_value",
            company="company_value",
            requisition_id="requisition_id_value",
            title="title_value",
            description="description_value",
            addresses=["addresses_value"],
            job_benefits=[common.JobBenefit.CHILD_CARE],
            degree_types=[common.DegreeType.PRIMARY_EDUCATION],
            department="department_value",
            employment_types=[common.EmploymentType.FULL_TIME],
            incentives="incentives_value",
            language_code="language_code_value",
            job_level=common.JobLevel.ENTRY_LEVEL,
            promotion_value=1635,
            qualifications="qualifications_value",
            responsibilities="responsibilities_value",
            posting_region=common.PostingRegion.ADMINISTRATIVE_AREA,
            visibility=common.Visibility.ACCOUNT_ONLY,
            company_display_name="company_display_name_value",
        )

        response = client.update_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == job_service.UpdateJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gct_job.Job)

    assert response.name == "name_value"

    assert response.company == "company_value"

    assert response.requisition_id == "requisition_id_value"

    assert response.title == "title_value"

    assert response.description == "description_value"

    assert response.addresses == ["addresses_value"]

    assert response.job_benefits == [common.JobBenefit.CHILD_CARE]

    assert response.degree_types == [common.DegreeType.PRIMARY_EDUCATION]

    assert response.department == "department_value"

    assert response.employment_types == [common.EmploymentType.FULL_TIME]

    assert response.incentives == "incentives_value"

    assert response.language_code == "language_code_value"

    assert response.job_level == common.JobLevel.ENTRY_LEVEL

    assert response.promotion_value == 1635

    assert response.qualifications == "qualifications_value"

    assert response.responsibilities == "responsibilities_value"

    assert response.posting_region == common.PostingRegion.ADMINISTRATIVE_AREA

    assert response.visibility == common.Visibility.ACCOUNT_ONLY

    assert response.company_display_name == "company_display_name_value"


def test_update_job_from_dict():
    test_update_job(request_type=dict)


@pytest.mark.asyncio
async def test_update_job_async(transport: str = "grpc_asyncio"):
    client = JobServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = job_service.UpdateJobRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gct_job.Job(
                name="name_value",
                company="company_value",
                requisition_id="requisition_id_value",
                title="title_value",
                description="description_value",
                addresses=["addresses_value"],
                job_benefits=[common.JobBenefit.CHILD_CARE],
                degree_types=[common.DegreeType.PRIMARY_EDUCATION],
                department="department_value",
                employment_types=[common.EmploymentType.FULL_TIME],
                incentives="incentives_value",
                language_code="language_code_value",
                job_level=common.JobLevel.ENTRY_LEVEL,
                promotion_value=1635,
                qualifications="qualifications_value",
                responsibilities="responsibilities_value",
                posting_region=common.PostingRegion.ADMINISTRATIVE_AREA,
                visibility=common.Visibility.ACCOUNT_ONLY,
                company_display_name="company_display_name_value",
            )
        )

        response = await client.update_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gct_job.Job)

    assert response.name == "name_value"

    assert response.company == "company_value"

    assert response.requisition_id == "requisition_id_value"

    assert response.title == "title_value"

    assert response.description == "description_value"

    assert response.addresses == ["addresses_value"]

    assert response.job_benefits == [common.JobBenefit.CHILD_CARE]

    assert response.degree_types == [common.DegreeType.PRIMARY_EDUCATION]

    assert response.department == "department_value"

    assert response.employment_types == [common.EmploymentType.FULL_TIME]

    assert response.incentives == "incentives_value"

    assert response.language_code == "language_code_value"

    assert response.job_level == common.JobLevel.ENTRY_LEVEL

    assert response.promotion_value == 1635

    assert response.qualifications == "qualifications_value"

    assert response.responsibilities == "responsibilities_value"

    assert response.posting_region == common.PostingRegion.ADMINISTRATIVE_AREA

    assert response.visibility == common.Visibility.ACCOUNT_ONLY

    assert response.company_display_name == "company_display_name_value"


def test_update_job_field_headers():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.UpdateJobRequest()
    request.job.name = "job.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.update_job), "__call__") as call:
        call.return_value = gct_job.Job()

        client.update_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "job.name=job.name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_update_job_field_headers_async():
    client = JobServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.UpdateJobRequest()
    request.job.name = "job.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_job), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(gct_job.Job())

        await client.update_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "job.name=job.name/value",) in kw["metadata"]


def test_update_job_flattened():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.update_job), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gct_job.Job()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_job(
            job=gct_job.Job(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].job == gct_job.Job(name="name_value")

        assert args[0].update_mask == field_mask.FieldMask(paths=["paths_value"])


def test_update_job_flattened_error():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_job(
            job_service.UpdateJobRequest(),
            job=gct_job.Job(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )


@pytest.mark.asyncio
async def test_update_job_flattened_async():
    client = JobServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gct_job.Job()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(gct_job.Job())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_job(
            job=gct_job.Job(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].job == gct_job.Job(name="name_value")

        assert args[0].update_mask == field_mask.FieldMask(paths=["paths_value"])


@pytest.mark.asyncio
async def test_update_job_flattened_error_async():
    client = JobServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_job(
            job_service.UpdateJobRequest(),
            job=gct_job.Job(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )


def test_batch_update_jobs(
    transport: str = "grpc", request_type=job_service.BatchUpdateJobsRequest
):
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.batch_update_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")

        response = client.batch_update_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == job_service.BatchUpdateJobsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_batch_update_jobs_from_dict():
    test_batch_update_jobs(request_type=dict)


@pytest.mark.asyncio
async def test_batch_update_jobs_async(transport: str = "grpc_asyncio"):
    client = JobServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = job_service.BatchUpdateJobsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.batch_update_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )

        response = await client.batch_update_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_batch_update_jobs_field_headers():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.BatchUpdateJobsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.batch_update_jobs), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")

        client.batch_update_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_batch_update_jobs_field_headers_async():
    client = JobServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.BatchUpdateJobsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.batch_update_jobs), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )

        await client.batch_update_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_batch_update_jobs_flattened():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.batch_update_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.batch_update_jobs(
            parent="parent_value", jobs=[job.Job(name="name_value")],
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].jobs == [job.Job(name="name_value")]


def test_batch_update_jobs_flattened_error():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.batch_update_jobs(
            job_service.BatchUpdateJobsRequest(),
            parent="parent_value",
            jobs=[job.Job(name="name_value")],
        )


@pytest.mark.asyncio
async def test_batch_update_jobs_flattened_async():
    client = JobServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.batch_update_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.batch_update_jobs(
            parent="parent_value", jobs=[job.Job(name="name_value")],
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].jobs == [job.Job(name="name_value")]


@pytest.mark.asyncio
async def test_batch_update_jobs_flattened_error_async():
    client = JobServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.batch_update_jobs(
            job_service.BatchUpdateJobsRequest(),
            parent="parent_value",
            jobs=[job.Job(name="name_value")],
        )


def test_delete_job(transport: str = "grpc", request_type=job_service.DeleteJobRequest):
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.delete_job), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        response = client.delete_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == job_service.DeleteJobRequest()

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_job_from_dict():
    test_delete_job(request_type=dict)


@pytest.mark.asyncio
async def test_delete_job_async(transport: str = "grpc_asyncio"):
    client = JobServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = job_service.DeleteJobRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        response = await client.delete_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_job_field_headers():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.DeleteJobRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.delete_job), "__call__") as call:
        call.return_value = None

        client.delete_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_job_field_headers_async():
    client = JobServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.DeleteJobRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_job), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        await client.delete_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_delete_job_flattened():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.delete_job), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_job(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_delete_job_flattened_error():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_job(
            job_service.DeleteJobRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_job_flattened_async():
    client = JobServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_job(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_delete_job_flattened_error_async():
    client = JobServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_job(
            job_service.DeleteJobRequest(), name="name_value",
        )


def test_batch_delete_jobs(
    transport: str = "grpc", request_type=job_service.BatchDeleteJobsRequest
):
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.batch_delete_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")

        response = client.batch_delete_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == job_service.BatchDeleteJobsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_batch_delete_jobs_from_dict():
    test_batch_delete_jobs(request_type=dict)


@pytest.mark.asyncio
async def test_batch_delete_jobs_async(transport: str = "grpc_asyncio"):
    client = JobServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = job_service.BatchDeleteJobsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.batch_delete_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )

        response = await client.batch_delete_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_batch_delete_jobs_field_headers():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.BatchDeleteJobsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.batch_delete_jobs), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")

        client.batch_delete_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_batch_delete_jobs_field_headers_async():
    client = JobServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.BatchDeleteJobsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.batch_delete_jobs), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )

        await client.batch_delete_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_batch_delete_jobs_flattened():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.batch_delete_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.batch_delete_jobs(
            parent="parent_value", names=["names_value"],
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].names == ["names_value"]


def test_batch_delete_jobs_flattened_error():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.batch_delete_jobs(
            job_service.BatchDeleteJobsRequest(),
            parent="parent_value",
            names=["names_value"],
        )


@pytest.mark.asyncio
async def test_batch_delete_jobs_flattened_async():
    client = JobServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.batch_delete_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.batch_delete_jobs(
            parent="parent_value", names=["names_value"],
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].names == ["names_value"]


@pytest.mark.asyncio
async def test_batch_delete_jobs_flattened_error_async():
    client = JobServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.batch_delete_jobs(
            job_service.BatchDeleteJobsRequest(),
            parent="parent_value",
            names=["names_value"],
        )


def test_list_jobs(transport: str = "grpc", request_type=job_service.ListJobsRequest):
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_jobs), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = job_service.ListJobsResponse(
            next_page_token="next_page_token_value",
        )

        response = client.list_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == job_service.ListJobsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListJobsPager)

    assert response.next_page_token == "next_page_token_value"


def test_list_jobs_from_dict():
    test_list_jobs(request_type=dict)


@pytest.mark.asyncio
async def test_list_jobs_async(transport: str = "grpc_asyncio"):
    client = JobServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = job_service.ListJobsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            job_service.ListJobsResponse(next_page_token="next_page_token_value",)
        )

        response = await client.list_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListJobsAsyncPager)

    assert response.next_page_token == "next_page_token_value"


def test_list_jobs_field_headers():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.ListJobsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_jobs), "__call__") as call:
        call.return_value = job_service.ListJobsResponse()

        client.list_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_jobs_field_headers_async():
    client = JobServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.ListJobsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_jobs), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            job_service.ListJobsResponse()
        )

        await client.list_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_jobs_flattened():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_jobs), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = job_service.ListJobsResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_jobs(
            parent="parent_value", filter="filter_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].filter == "filter_value"


def test_list_jobs_flattened_error():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_jobs(
            job_service.ListJobsRequest(), parent="parent_value", filter="filter_value",
        )


@pytest.mark.asyncio
async def test_list_jobs_flattened_async():
    client = JobServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = job_service.ListJobsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            job_service.ListJobsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_jobs(parent="parent_value", filter="filter_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].filter == "filter_value"


@pytest.mark.asyncio
async def test_list_jobs_flattened_error_async():
    client = JobServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_jobs(
            job_service.ListJobsRequest(), parent="parent_value", filter="filter_value",
        )


def test_list_jobs_pager():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_jobs), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListJobsResponse(
                jobs=[job.Job(), job.Job(), job.Job(),], next_page_token="abc",
            ),
            job_service.ListJobsResponse(jobs=[], next_page_token="def",),
            job_service.ListJobsResponse(jobs=[job.Job(),], next_page_token="ghi",),
            job_service.ListJobsResponse(jobs=[job.Job(), job.Job(),],),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_jobs(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, job.Job) for i in results)


def test_list_jobs_pages():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_jobs), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListJobsResponse(
                jobs=[job.Job(), job.Job(), job.Job(),], next_page_token="abc",
            ),
            job_service.ListJobsResponse(jobs=[], next_page_token="def",),
            job_service.ListJobsResponse(jobs=[job.Job(),], next_page_token="ghi",),
            job_service.ListJobsResponse(jobs=[job.Job(), job.Job(),],),
            RuntimeError,
        )
        pages = list(client.list_jobs(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_jobs_async_pager():
    client = JobServiceAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_jobs),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListJobsResponse(
                jobs=[job.Job(), job.Job(), job.Job(),], next_page_token="abc",
            ),
            job_service.ListJobsResponse(jobs=[], next_page_token="def",),
            job_service.ListJobsResponse(jobs=[job.Job(),], next_page_token="ghi",),
            job_service.ListJobsResponse(jobs=[job.Job(), job.Job(),],),
            RuntimeError,
        )
        async_pager = await client.list_jobs(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, job.Job) for i in responses)


@pytest.mark.asyncio
async def test_list_jobs_async_pages():
    client = JobServiceAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_jobs),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListJobsResponse(
                jobs=[job.Job(), job.Job(), job.Job(),], next_page_token="abc",
            ),
            job_service.ListJobsResponse(jobs=[], next_page_token="def",),
            job_service.ListJobsResponse(jobs=[job.Job(),], next_page_token="ghi",),
            job_service.ListJobsResponse(jobs=[job.Job(), job.Job(),],),
            RuntimeError,
        )
        pages = []
        async for page_ in (await client.list_jobs(request={})).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_search_jobs(
    transport: str = "grpc", request_type=job_service.SearchJobsRequest
):
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.search_jobs), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = job_service.SearchJobsResponse(
            next_page_token="next_page_token_value",
            total_size=1086,
            broadened_query_jobs_count=2766,
        )

        response = client.search_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == job_service.SearchJobsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, job_service.SearchJobsResponse)

    assert response.next_page_token == "next_page_token_value"

    assert response.total_size == 1086

    assert response.broadened_query_jobs_count == 2766


def test_search_jobs_from_dict():
    test_search_jobs(request_type=dict)


@pytest.mark.asyncio
async def test_search_jobs_async(transport: str = "grpc_asyncio"):
    client = JobServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = job_service.SearchJobsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.search_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            job_service.SearchJobsResponse(
                next_page_token="next_page_token_value",
                total_size=1086,
                broadened_query_jobs_count=2766,
            )
        )

        response = await client.search_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, job_service.SearchJobsResponse)

    assert response.next_page_token == "next_page_token_value"

    assert response.total_size == 1086

    assert response.broadened_query_jobs_count == 2766


def test_search_jobs_field_headers():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.SearchJobsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.search_jobs), "__call__") as call:
        call.return_value = job_service.SearchJobsResponse()

        client.search_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_search_jobs_field_headers_async():
    client = JobServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.SearchJobsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.search_jobs), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            job_service.SearchJobsResponse()
        )

        await client.search_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_search_jobs_for_alert(
    transport: str = "grpc", request_type=job_service.SearchJobsRequest
):
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.search_jobs_for_alert), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = job_service.SearchJobsResponse(
            next_page_token="next_page_token_value",
            total_size=1086,
            broadened_query_jobs_count=2766,
        )

        response = client.search_jobs_for_alert(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == job_service.SearchJobsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, job_service.SearchJobsResponse)

    assert response.next_page_token == "next_page_token_value"

    assert response.total_size == 1086

    assert response.broadened_query_jobs_count == 2766


def test_search_jobs_for_alert_from_dict():
    test_search_jobs_for_alert(request_type=dict)


@pytest.mark.asyncio
async def test_search_jobs_for_alert_async(transport: str = "grpc_asyncio"):
    client = JobServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = job_service.SearchJobsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.search_jobs_for_alert), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            job_service.SearchJobsResponse(
                next_page_token="next_page_token_value",
                total_size=1086,
                broadened_query_jobs_count=2766,
            )
        )

        response = await client.search_jobs_for_alert(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, job_service.SearchJobsResponse)

    assert response.next_page_token == "next_page_token_value"

    assert response.total_size == 1086

    assert response.broadened_query_jobs_count == 2766


def test_search_jobs_for_alert_field_headers():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.SearchJobsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.search_jobs_for_alert), "__call__"
    ) as call:
        call.return_value = job_service.SearchJobsResponse()

        client.search_jobs_for_alert(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_search_jobs_for_alert_field_headers_async():
    client = JobServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.SearchJobsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.search_jobs_for_alert), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            job_service.SearchJobsResponse()
        )

        await client.search_jobs_for_alert(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.JobServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = JobServiceClient(
            credentials=credentials.AnonymousCredentials(), transport=transport,
        )

    # It is an error to provide a credentials file and a transport instance.
    transport = transports.JobServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = JobServiceClient(
            client_options={"credentials_file": "credentials.json"},
            transport=transport,
        )

    # It is an error to provide scopes and a transport instance.
    transport = transports.JobServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = JobServiceClient(
            client_options={"scopes": ["1", "2"]}, transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.JobServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    client = JobServiceClient(transport=transport)
    assert client._transport is transport


def test_transport_get_channel():
    # A client may be instantiated with a custom transport instance.
    transport = transports.JobServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel

    transport = transports.JobServiceGrpcAsyncIOTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel


@pytest.mark.parametrize(
    "transport_class",
    [transports.JobServiceGrpcTransport, transports.JobServiceGrpcAsyncIOTransport],
)
def test_transport_adc(transport_class):
    # Test default credentials are used if not provided.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        transport_class()
        adc.assert_called_once()


def test_transport_grpc_default():
    # A client should use the gRPC transport by default.
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)
    assert isinstance(client._transport, transports.JobServiceGrpcTransport,)


def test_job_service_base_transport_error():
    # Passing both a credentials object and credentials_file should raise an error
    with pytest.raises(exceptions.DuplicateCredentialArgs):
        transport = transports.JobServiceTransport(
            credentials=credentials.AnonymousCredentials(),
            credentials_file="credentials.json",
        )


def test_job_service_base_transport():
    # Instantiate the base transport.
    with mock.patch(
        "google.cloud.talent_v4.services.job_service.transports.JobServiceTransport.__init__"
    ) as Transport:
        Transport.return_value = None
        transport = transports.JobServiceTransport(
            credentials=credentials.AnonymousCredentials(),
        )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        "create_job",
        "batch_create_jobs",
        "get_job",
        "update_job",
        "batch_update_jobs",
        "delete_job",
        "batch_delete_jobs",
        "list_jobs",
        "search_jobs",
        "search_jobs_for_alert",
    )
    for method in methods:
        with pytest.raises(NotImplementedError):
            getattr(transport, method)(request=object())

    # Additionally, the LRO client (a property) should
    # also raise NotImplementedError
    with pytest.raises(NotImplementedError):
        transport.operations_client


def test_job_service_base_transport_with_credentials_file():
    # Instantiate the base transport with a credentials file
    with mock.patch.object(
        auth, "load_credentials_from_file"
    ) as load_creds, mock.patch(
        "google.cloud.talent_v4.services.job_service.transports.JobServiceTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        load_creds.return_value = (credentials.AnonymousCredentials(), None)
        transport = transports.JobServiceTransport(
            credentials_file="credentials.json", quota_project_id="octopus",
        )
        load_creds.assert_called_once_with(
            "credentials.json",
            scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/jobs",
            ),
            quota_project_id="octopus",
        )


def test_job_service_base_transport_with_adc():
    # Test the default credentials are used if credentials and credentials_file are None.
    with mock.patch.object(auth, "default") as adc, mock.patch(
        "google.cloud.talent_v4.services.job_service.transports.JobServiceTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        adc.return_value = (credentials.AnonymousCredentials(), None)
        transport = transports.JobServiceTransport()
        adc.assert_called_once()


def test_job_service_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        JobServiceClient()
        adc.assert_called_once_with(
            scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/jobs",
            ),
            quota_project_id=None,
        )


def test_job_service_transport_auth_adc():
    # If credentials and host are not provided, the transport class should use
    # ADC credentials.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        transports.JobServiceGrpcTransport(
            host="squid.clam.whelk", quota_project_id="octopus"
        )
        adc.assert_called_once_with(
            scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/jobs",
            ),
            quota_project_id="octopus",
        )


def test_job_service_host_no_port():
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(api_endpoint="jobs.googleapis.com"),
    )
    assert client._transport._host == "jobs.googleapis.com:443"


def test_job_service_host_with_port():
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="jobs.googleapis.com:8000"
        ),
    )
    assert client._transport._host == "jobs.googleapis.com:8000"


def test_job_service_grpc_transport_channel():
    channel = grpc.insecure_channel("http://localhost/")

    # Check that channel is used if provided.
    transport = transports.JobServiceGrpcTransport(
        host="squid.clam.whelk", channel=channel,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"


def test_job_service_grpc_asyncio_transport_channel():
    channel = aio.insecure_channel("http://localhost/")

    # Check that channel is used if provided.
    transport = transports.JobServiceGrpcAsyncIOTransport(
        host="squid.clam.whelk", channel=channel,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"


@pytest.mark.parametrize(
    "transport_class",
    [transports.JobServiceGrpcTransport, transports.JobServiceGrpcAsyncIOTransport],
)
def test_job_service_transport_channel_mtls_with_client_cert_source(transport_class):
    with mock.patch(
        "grpc.ssl_channel_credentials", autospec=True
    ) as grpc_ssl_channel_cred:
        with mock.patch.object(
            transport_class, "create_channel", autospec=True
        ) as grpc_create_channel:
            mock_ssl_cred = mock.Mock()
            grpc_ssl_channel_cred.return_value = mock_ssl_cred

            mock_grpc_channel = mock.Mock()
            grpc_create_channel.return_value = mock_grpc_channel

            cred = credentials.AnonymousCredentials()
            with pytest.warns(DeprecationWarning):
                with mock.patch.object(auth, "default") as adc:
                    adc.return_value = (cred, None)
                    transport = transport_class(
                        host="squid.clam.whelk",
                        api_mtls_endpoint="mtls.squid.clam.whelk",
                        client_cert_source=client_cert_source_callback,
                    )
                    adc.assert_called_once()

            grpc_ssl_channel_cred.assert_called_once_with(
                certificate_chain=b"cert bytes", private_key=b"key bytes"
            )
            grpc_create_channel.assert_called_once_with(
                "mtls.squid.clam.whelk:443",
                credentials=cred,
                credentials_file=None,
                scopes=(
                    "https://www.googleapis.com/auth/cloud-platform",
                    "https://www.googleapis.com/auth/jobs",
                ),
                ssl_credentials=mock_ssl_cred,
                quota_project_id=None,
            )
            assert transport.grpc_channel == mock_grpc_channel


@pytest.mark.parametrize(
    "transport_class",
    [transports.JobServiceGrpcTransport, transports.JobServiceGrpcAsyncIOTransport],
)
def test_job_service_transport_channel_mtls_with_adc(transport_class):
    mock_ssl_cred = mock.Mock()
    with mock.patch.multiple(
        "google.auth.transport.grpc.SslCredentials",
        __init__=mock.Mock(return_value=None),
        ssl_credentials=mock.PropertyMock(return_value=mock_ssl_cred),
    ):
        with mock.patch.object(
            transport_class, "create_channel", autospec=True
        ) as grpc_create_channel:
            mock_grpc_channel = mock.Mock()
            grpc_create_channel.return_value = mock_grpc_channel
            mock_cred = mock.Mock()

            with pytest.warns(DeprecationWarning):
                transport = transport_class(
                    host="squid.clam.whelk",
                    credentials=mock_cred,
                    api_mtls_endpoint="mtls.squid.clam.whelk",
                    client_cert_source=None,
                )

            grpc_create_channel.assert_called_once_with(
                "mtls.squid.clam.whelk:443",
                credentials=mock_cred,
                credentials_file=None,
                scopes=(
                    "https://www.googleapis.com/auth/cloud-platform",
                    "https://www.googleapis.com/auth/jobs",
                ),
                ssl_credentials=mock_ssl_cred,
                quota_project_id=None,
            )
            assert transport.grpc_channel == mock_grpc_channel


def test_job_service_grpc_lro_client():
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(), transport="grpc",
    )
    transport = client._transport

    # Ensure that we have a api-core operations client.
    assert isinstance(transport.operations_client, operations_v1.OperationsClient,)

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client


def test_job_service_grpc_lro_async_client():
    client = JobServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport="grpc_asyncio",
    )
    transport = client._client._transport

    # Ensure that we have a api-core operations client.
    assert isinstance(transport.operations_client, operations_v1.OperationsAsyncClient,)

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client


def test_job_path():
    project = "squid"
    tenant = "clam"
    job = "whelk"

    expected = "projects/{project}/tenants/{tenant}/jobs/{job}".format(
        project=project, tenant=tenant, job=job,
    )
    actual = JobServiceClient.job_path(project, tenant, job)
    assert expected == actual


def test_parse_job_path():
    expected = {
        "project": "octopus",
        "tenant": "oyster",
        "job": "nudibranch",
    }
    path = JobServiceClient.job_path(**expected)

    # Check that the path construction is reversible.
    actual = JobServiceClient.parse_job_path(path)
    assert expected == actual


def test_client_withDEFAULT_CLIENT_INFO():
    client_info = gapic_v1.client_info.ClientInfo()

    with mock.patch.object(
        transports.JobServiceTransport, "_prep_wrapped_messages"
    ) as prep:
        client = JobServiceClient(
            credentials=credentials.AnonymousCredentials(), client_info=client_info,
        )
        prep.assert_called_once_with(client_info)

    with mock.patch.object(
        transports.JobServiceTransport, "_prep_wrapped_messages"
    ) as prep:
        transport_class = JobServiceClient.get_transport_class()
        transport = transport_class(
            credentials=credentials.AnonymousCredentials(), client_info=client_info,
        )
        prep.assert_called_once_with(client_info)
