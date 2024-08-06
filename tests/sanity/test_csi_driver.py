#
# Copyright 2024 Canonical, Ltd.
# See LICENSE file for licensing details
#

import pytest
from k8s_test_harness.util import docker_util, env_util

# In the future, we may also test ARM
IMG_PLATFORM = "amd64"
IMG_NAME = "vsphere-csi-driver"

EXPECTED_FILES = [
    "/bin/vsphere-csi",
]

EXPECTED_HELPSTR = "Usage of /bin/vsphere-csi:"


@pytest.mark.parametrize("version", ["v3.3.1"])
def test_csi_driver(version: str):
    rock = env_util.get_build_meta_info_for_rock_version(
        IMG_NAME, version, IMG_PLATFORM
    )

    # check rock filesystem
    docker_util.ensure_image_contains_paths(rock.image, EXPECTED_FILES)

    docker_run = docker_util.run_in_docker(rock.image, ["/bin/vsphere-csi", "--help"])
    assert EXPECTED_HELPSTR in docker_run.stderr
