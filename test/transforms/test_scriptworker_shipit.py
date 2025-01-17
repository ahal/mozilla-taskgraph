import traceback
from pprint import pprint

import pytest

from mozilla_taskgraph.transforms.scriptworker.shipit.mark_as_shipped import (
    transforms as mark_as_shipped_transforms,
)


def assert_missing_config(e):
    assert isinstance(e, Exception)


def assert_default_level_1(task):
    assert task == {
        "description": "Mark app as shipped in Ship-It",
        "label": "mark-as-shipped",
        "scopes": [
            "project:releng:ship-it:action:mark-as-shipped",
            "project:releng:ship-it:server:staging",
        ],
        "worker": {"release-name": "app-1.0.0-build1"},
    }


def assert_default_level_3(task):
    assert task == {
        "description": "Mark app as shipped in Ship-It",
        "label": "mark-as-shipped",
        "scopes": [
            "project:releng:ship-it:action:mark-as-shipped",
            "project:releng:ship-it:server:production",
        ],
        "worker": {"release-name": "app-1.0.0-build1"},
    }


def assert_release_format(task):
    assert task["worker"]["release-name"] == "release-app-v1.2.3-b10"


def assert_scope_prefix(task):
    assert task["scopes"] == [
        "project:app:releng:action:mark-as-shipped",
        "project:app:releng:server:staging",
    ]


@pytest.mark.parametrize(
    "shipit_config,params",
    (
        pytest.param({}, None, id="missing_config"),
        pytest.param(
            {"shipit": {"product": "app"}},
            {"version": "1.0.0", "level": "1"},
            id="default_level_1",
        ),
        pytest.param(
            {"shipit": {"product": "app"}},
            {"version": "1.0.0", "level": "3"},
            id="default_level_3",
        ),
        pytest.param(
            {
                "shipit": {
                    "product": "app",
                    "release-format": "release-{product}-v{version}-b{build_number}",
                }
            },
            {"level": "1", "version": "1.2.3", "build_number": "10"},
            id="release_format",
        ),
        pytest.param(
            {"shipit": {"product": "app", "scope-prefix": "project:app:releng"}},
            {"level": "1"},
            id="scope_prefix",
        ),
    ),
)
def test_mark_as_shipped(
    request,
    make_graph_config,
    make_transform_config,
    run_transform,
    shipit_config,
    params,
):
    graph_config = make_graph_config(extra_config=shipit_config)
    config = make_transform_config(graph_cfg=graph_config, params=params)

    try:
        result = run_transform(mark_as_shipped_transforms, {}, config)
        assert len(result) == 1
        result = result[0]

        print("Dumping result:")
        pprint(result, indent=2)
    except Exception as e:
        traceback.print_exc()
        result = e

    param_id = request.node.callspec.id
    assert_func = globals()[f"assert_{param_id}"]
    assert_func(result)
