#
# Copyright 2024 Canonical, Ltd.
# See LICENSE file for licensing details
#

import uuid

import pytest
from k8s_test_harness import harness
from k8s_test_harness.util import constants, env_util, k8s_util
from k8s_test_harness.util.k8s_util import HelmImage

IMG_PLATFORM = "amd64"
INSTALL_NAME = "vsphere-csi-driver"


def _get_rock_image(name: str, version: str):
    rock = env_util.get_build_meta_info_for_rock_version(name, version, IMG_PLATFORM)
    return rock.image


@pytest.mark.parametrize("version", ["v3.3.1"])
def test_csi_driver(function_instance: harness.Instance, version: str):
    rock_image = _get_rock_image("vsphere-csi-driver", version)

    # This helm chart requires the registry to be separated from the image.
    registry = "docker.io"
    parts = rock_image.split("/")
    if len(parts) > 1:
        registry = parts[0]
        rock_image = "/".join(parts[1:])

    images = [
        HelmImage(uri=rock_image, prefix="controller"),
        HelmImage(uri=rock_image, prefix="node"),
    ]

    cluster_id = "test-cluster-%s" % uuid.uuid4().fields[0]
    set_configs = [
        f"global.config.global.cluster-id={cluster_id}",
    ]
    for image in images:
        set_configs.append(
            f"{image.prefix}.image.registry={registry}",
        )

    # Specifying the registry and chart version didn't work, as a workaround
    # we're passing the chart archive url.
    chart = "vsphere-csi-3.6.0"
    helm_command = k8s_util.get_helm_install_command(
        name=INSTALL_NAME,
        chart_name=f"https://github.com/vsphere-tmm/helm-charts/releases/download/{chart}/{chart}.tgz",
        images=images,
        namespace=constants.K8S_NS_KUBE_SYSTEM,
        set_configs=set_configs,
    )
    function_instance.exec(helm_command)

    # The CSI deployment is expected to enter a crash loop since it requires an
    # actual vSphere environment. For the time being, the following assertions
    # are commented out.

    # k8s_util.wait_for_daemonset(
    #     function_instance, "vsphere-csi-driver", constants.K8S_NS_KUBE_SYSTEM
    # )

    # k8s_util.wait_for_deployment(
    #     function_instance, "vsphere-csi-controller", constants.K8S_NS_KUBE_SYSTEM
    # )
