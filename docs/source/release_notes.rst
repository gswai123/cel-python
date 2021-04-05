##################
Release Notes
##################

Initial Release
================

Phase I – base features
-----------------------

-   Lark parser for CEL language.
    This includes adjusting the ``cel.lark`` to eliminate Lark's ``!`` notations. These are a hint that the EBNF is written at the wrong level.

-   Base Run-time environment in which CEL evaluations occur.

-   Acceptance tests converted from textproto to Gherkin and placed in ``features`` directory.

    *   features/basic.textproto, Includes simple list, map, variable, and function operations

    *   features/integer_math.textproto

    *   features/comparisons.textproto

    *   features/logic.textproto

    *   features/string.textproto

    *   features/fp_math.textproto

    *   features/lists.textproto – List structure build and navigate operators

    *   features/fields.textproto – Mapping fields

    *   features/namespace.textproto

    *   features/conversions.textproto

    *   features/timestamps.textproto

    *   features/macros.textproto

-   All of the required overheads for open source (LICENSE, etc.) This includes mappings to the Go examples for use, as well as cloned documentation with appropriate Python notes.

-   Permit function overrides available via the run-time environment.

-   A Pythonic internal API that attempts to preserve the spirit of the Go version with compile/evaluate interface usable in a variety of contexts, most notably C7N, but not limited to C7N.
    examples from https://github.com/google/cel-go/tree/master/examples are rewritten and included.

Phase II – C7N Integration
--------------------------

-   Error messages show the operator and operands and provide better context. See https://github.com/google/cel-go#errors.

-   100% unit test coverage, including doctest examples in documentation.

-   Strict type hint coverage.

-   The CLI to duplicates `jq`, `bc`, `expr`, and `test` command-line apps to the extent possible. This is purely marketing and helpful as POC. Include REPL to read from CLI and evaluate expressions. Consider adding `set` (or `let`) command to create variables. Or perhaps an assignment statement. Gherkin for all CLI examples in documentation.

-   A C7N Utility Library to fetch data from cloud resources in various formats. This requires a survey of various data types and data sources in C7N objects.

    *   Common "type:" options where there's an "op:" field. These extract data from the cloud resource.

        #   type: value -- Resource.key *op* value. or Resource.key *op* value_type(value)

        #   type: value-from -- value_from("path").jmes_path("expression")

        #   type: marked-for-op – Resource.marked_key("name") function

        #   type: image-age – Resource.image() function gets associated resource

        #   type: event – Resource.event() function

        #   type: metrics – get_raw_metrics() and Resource.metrics() functions

        #   type: age – actually easy, requires a min() macro for cache-snapshot

        #   type: security-group – "id".security_group() function gets associated resource. Often used like this: `Resource.SecurityGroups.map(sg. sg.GroupId.security_group())`

        #   type: subnet - "id".subnet() gets associated resource. Often used like this: `"s3://whatever".value_from("jmespath").contains(Resource.Something.subnet().SubnetId)`

        #   type: flow-logs - size(Resource.flow_logs()) == 0

        #   type: tag-count - size(Resource["Tags"].filter(x, ! matches(x.Key, "^aws:.*"))) >= 8

        #   type: vpc - Resource.VpcId.vpc()

        #   type: credential - Resource.credentials()

        #   type: image - Resource.image()

        #   type: kms-alias - Resource.kms_alias()

        #   type: kms-key - Resource.SSEDescription.KMSMasterKeyArn.kms_key()


    *   A future release will have common "type:" options where there's no "op:" field. These are boolean computations that need to be exposed as data.
        Examples include "type: onhour", "type: offhour", "type: cross-account",
        "type: unused",  "type: used", "type: is-not-logging", "type: is-logging",
        "type: health-event",  "type: shield-enabled",  "type: waf-enabled",  "type: network-location".

    *   These rarely-used "type:" options may never be supported directly by CEL. They're used
        rarely, and the legacy syntax is still available.
        "type: launch-config",
        "type: instance-age",
        "type: listener",
        "type: vpc-id",
        "type: ebs",
        "type: instance-uptime",
        "type: state-age",
        "type: password-policy",
        "type: reserved-concurrency",
        "type: access-key",
        "type: mfa-device",
        "type: policy",
        "type: key-rotation-status",
        "type: skip-ami-snapshots",
        "type: missing-policy-statement",
        "type: ssl-policy",
        "type: service-limit",
        "type: global-grants",
        "type: last-write",
        "type: invalid",
        "type: not-encrypted",
        "type: is-log-target",
        "type: has-statement",
        "type: missing",
        "type: mismatch-s3-origin",
        "type: ingress",
        "type: egress",
        "type: valid",
        "type: latest",
        "type: capacity-delta",
        "type: check-cloudtrail",
        "type: check-config",
        "type: grant-count"

    *   There are a number of "type: " options defined within the C7N code base, but for which there are no
        ready examples.

Future Directions
=================


Phase III – Introduce JSON Schema validation to the extent possible. This is *not* a first-class feature of CEL,
but can be handy for some C7N integration efforts.

Phase IV – Further Conformance – protobuf integration. This is a first-class part of CEL, but unimportant
for current C7N compatibility. There are a few individual scenarios plus two complete features for protobuf2
and protobuf3 support in CEL. This will be an optional feature, likely not used by C7N.

Phase V – Optimization. Currently, the AST is not optimized in any way. Applying a transformer to eliminate
"do nothing" nodes will improve performance. Additionally, it may be sensible to emit a Python intermediate
result and used Python's ``compile()`` and ``eval()`` to produce byte-code
