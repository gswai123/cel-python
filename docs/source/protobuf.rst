..  comment
    # Copyright 2020 The Cloud Custodian Authors.
    # SPDX-License-Identifier: Apache-2.0


######################
Protobuf Support
######################

Background
==========

See https://github.com/google/cel-spec/blob/master/proto/test/v1/proto3/test_all_types.proto
and https://github.com/google/cel-spec/blob/master/proto/test/v1/proto2/test_all_types.proto

These two definitions create two packages:

- ``package google.api.expr.test.v1.proto2``

- ``package google.api.expr.test.v1.proto3``

These packages are referenced by a number of conformance tests. As a small example, see
the ``parse.feature``, where there are three protobuf-specific tests.

-   nest - "message_literal", uses ``NestedTestAllTypes``

    ::

        Scenario: "message_literal"
          "Member = Member '{' [FieldInits] '}'"
        Given container is "google.api.expr.test.v1.proto3"


-   repeat - "select", uses ``NestedTestAllTypes``

    ::

        Scenario: "select"
          "Member = Member '.' IDENT ['(' [ExprList] ')']"
        Given container is "google.api.expr.test.v1.proto3"

-   repeat - "message_literal", uses ``TestAllTypes``

    ::

        Scenario: "message_literal"
          "Member = Member '{' [FieldInits] '}'"
        Given container is "google.api.expr.test.v1.proto3"

These examples rely on a specific protobuf package being available.

The protobuf package path is used to bind protobuf definitions into the CEL environment.
Given the package path as a namespace, then, references to a name like ``NestedTestAllTypes`` or ``TestAllTypes``
is resolved via the namespace.

See https://github.com/google/cel-spec/blob/master/doc/langdef.md#evaluation-environment. The protobuf is
part of the environment used to compile (and statically type check.)


A ``Provider`` defines the various protobuf classes themselves.
(See https://github.com/google/cel-go/blob/master/common/types/provider.go)
In Python, this seems to map to ``import``.

A ``Container`` is the namespace, defining how names are resolved.
This will handle a container name ``a.b.c.M.N`` and a type name ``R.s``
to make sure that ``R.s`` can be found within the container after stripping
away layers of quaified names.
(See https://github.com/google/cel-go/blob/master/common/containers/container.go)
A Python implementation is required to traverse CEL names and map them to imported
class definitions.

The protobuf class definitions (in Python) need to follow the style set by Go.
We should be able to do the following:

1.  Resolve the protobuf class definition. This means the CEL-standard protobuf
    package path needs to be resolved to an imported Python class name through the
    environment's definitions of names.

2.  Work with protobuf class definitions in general to navigate to fields and create
    new instances. These definitions are adjacent to the ``celtypes`` definitions.

3.  Create protobuf instances.
    CEL expressions should be able to populate protobuf instances.
    This uses the ``fieldinits`` construct.

4.  Navigate into protobuf instances loaded into the CEL activation.
    This is nearly identical to working with mappings.

5.  Load protobuf instances into the CEL activation. Return protobuf objects as a valid stream of bytes.
    See https://pypi.org/project/pure-protobuf/. This is the API we'll expect. If other is required,
    it will be an extension of some kind. (An alternative is https://github.com/appnexus/pyrobuf)

6.  Handle the "well-known" types. https://developers.google.com/protocol-buffers/docs/reference/google.protobuf

Implementation
==============

Environment needs:

::

    import R

    decls: Dict[str, celpy.Annotation] = {
        "Resource": celpy.celtypes.MapType,
        "Now": celpy.celtypes.TimestampType,
        "a.b.c.M.N.R.s": R.s,
    }
    env = celpy.Environment(annotations=decls)

Activation needs:

::

        import R

        activation = {
            "Resource": celpy.adapter.json_to_cel(document),
            "Now": celpy.celtypes.TimestampType(now),
            "some_object": R.s.load(some_bytes)
        }
        try:
            result = prgm.evaluate(activation)
            return result.dump()
        except Exception as ex:
            print(ex)
            return None

To pass the unit tests, the above concepts becomes the following implementation:

::

    from proto.v1.proto3_proto import NestedTestAllTypes, TestAllTypes
    decls: Dict[str, celpy.Annotation] = {
        "Resource": celpy.celtypes.MapType,
        "Now": celpy.celtypes.TimestampType,
        "google.api.expr.test.v1.proto3.NestedTestAllTypes": NestedTestAllTypes,
        "google.api.expr.test.v1.proto3.TestAllTypes": TestAllTypes,
    }
