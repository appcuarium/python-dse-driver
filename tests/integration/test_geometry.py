# Copyright 2016 DataStax, Inc.


from tests.integration import BasicGeometricUnitTestCase, use_single_node_with_graph
from cassandra.util import OrderedMap, sortedset
from collections import namedtuple

try:
    import unittest2 as unittest
except ImportError:
    import unittest  # noqa
from uuid import uuid1
from dse.util import Point, Circle, LineString, Polygon
from dse.cqltypes import CircleType, LineStringType, PointType, PolygonType


def setup_module():
    use_single_node_with_graph()


class AbstractGeometricTypeTest():
    original_value=""

    def test_should_insert_simple(self):
        """
        This tests will attempt to insert a point, polygon, circle, or line, using simple inline formating.
        @since 1.0.0
        @jira_ticket PYTHON-456
        @test_category dse geometric
        @expected_result geometric types should be able to be inserted and queried.
        """
        uuid_key = uuid1()
        self.session.execute("INSERT INTO tbl (k, g) VALUES (%s, %s)",[uuid_key, self.original_value])
        self.validate('g',uuid_key,self.original_value)

    def test_should_insert_simple_prepared(self):
        """
        This tests will attempt to insert a point, polygon, circle, or line, using prepared statements.
        @since 1.0.0
        @jira_ticket PYTHON-456
        @test_category dse geometric
        @expected_result geometric types should be able to be inserted and queried.
        """
        uuid_key = uuid1()
        prepared = self.session.prepare("INSERT INTO tbl (k, g) VALUES (?, ?)")
        self.session.execute(prepared, (uuid_key, self.original_value))
        self.validate('g',uuid_key,self.original_value)

    def test_should_insert_simple_prepared_with_bound(self):
        """
        This tests will attempt to insert a point, polygon, circle, or line, using prepared statements and bind.
        @since 1.0.0
        @jira_ticket PYTHON-456
        @test_category dse geometric
        @expected_result geometric types should be able to be inserted and queried.
        """
        uuid_key = uuid1()
        prepared = self.session.prepare("INSERT INTO tbl (k, g) VALUES (?, ?)")
        bound_statement=prepared.bind((uuid_key, self.original_value))
        self.session.execute(bound_statement)
        self.validate('g',uuid_key, self.original_value)

    def test_should_insert_as_list(self):
        """
        This tests will attempt to insert a point, polygon, circle, or line, as values of list.
        @since 1.0.0
        @jira_ticket PYTHON-456
        @test_category dse geometric
        @expected_result geometric types should be able to be inserted and queried as a list.
        """
        uuid_key = uuid1()
        prepared = self.session.prepare("INSERT INTO tbl (k, l) VALUES (?, ?)")
        bound_statement=prepared.bind((uuid_key, [self.original_value]))
        self.session.execute(bound_statement)
        self.validate('l',uuid_key, [self.original_value])

    def test_should_insert_as_set(self):
        """
        This tests will attempt to insert a point, polygon, circle, or line, as values of set.
        @since 1.0.0
        @jira_ticket PYTHON-456
        @test_category dse geometric
        @expected_result geometric types should be able to be inserted and queried as a set.
        """
        uuid_key = uuid1()
        prepared = self.session.prepare("INSERT INTO tbl (k, s) VALUES (?, ?)")
        bound_statement=prepared.bind((uuid_key, sortedset([self.original_value])))
        self.session.execute(bound_statement)
        self.validate('s',uuid_key, sortedset([self.original_value]))

    def test_should_insert_as_map_keys(self):
        """
        This tests will attempt to insert a point, polygon, circle, or line, as keys of a map.
        @since 1.0.0
        @jira_ticket PYTHON-456
        @test_category dse geometric
        @expected_result geometric types should be able to be inserted and queried as keys of a map.
        """
        uuid_key = uuid1()
        prepared = self.session.prepare("INSERT INTO tbl (k, m0) VALUES (?, ?)")
        bound_statement=prepared.bind((uuid_key, OrderedMap(zip([self.original_value],[1]))))
        self.session.execute(bound_statement)
        self.validate('m0',uuid_key, OrderedMap(zip([self.original_value],[1])))

    def test_should_insert_as_map_values(self):
        """
        This tests will attempt to insert a point, polygon, circle, or line, as values of a map.
        @since 1.0.0
        @jira_ticket PYTHON-456
        @test_category dse geometric
        @expected_result geometric types should be able to be inserted and queried as values of a map.
        """
        uuid_key = uuid1()
        prepared = self.session.prepare("INSERT INTO tbl (k, m1) VALUES (?, ?)")
        bound_statement=prepared.bind((uuid_key, OrderedMap(zip([1],[self.original_value]))))
        self.session.execute(bound_statement)
        self.validate('m1',uuid_key, OrderedMap(zip([1],[self.original_value])))

    def test_should_insert_as_tuple(self):
        """
        This tests will attempt to insert a point, polygon, circle, or line, as values of a tuple.
        @since 1.0.0
        @jira_ticket PYTHON-456
        @test_category dse geometric
        @expected_result geometric types should be able to be inserted and queried as values of a tuple.
        """
        uuid_key = uuid1()
        prepared = self.session.prepare("INSERT INTO tbl (k, t) VALUES (?, ?)")
        bound_statement=prepared.bind((uuid_key, (self.original_value, self.original_value, self.original_value)))
        self.session.execute(bound_statement)
        self.validate('t',uuid_key, (self.original_value, self.original_value, self.original_value))

    def test_should_insert_as_udt(self):
        """
        This tests will attempt to insert a point, polygon, circle, or line, as members of a udt.
        @since 1.0.0
        @jira_ticket PYTHON-456
        @test_category dse geometric
        @expected_result geometric types should be able to be inserted and queried as members of a udt.
        """
        UDT1 = namedtuple('udt1',('g'))
        self.cluster.register_user_type(self.ks_name, 'udt1', UDT1)
        uuid_key = uuid1()
        prepared = self.session.prepare("INSERT INTO tbl (k, u) values (?, ?)")
        bound_statement=prepared.bind((uuid_key, UDT1(self.original_value)))
        self.session.execute(bound_statement)
        rs=self.session.execute("SELECT {0} from {1} where k={2}".format('u','tbl',uuid_key))
        retrieved_udt = rs[0]._asdict()['u']

        self.assertEqual(retrieved_udt.g,self.original_value)

    def test_should_accept_as_partition_key(self):
        """
        This tests will attempt to insert a point, polygon, circle, or line, as a partition key.
        @since 1.0.0
        @jira_ticket PYTHON-456
        @test_category dse geometric
        @expected_result geometric types should be able to be inserted and queried as a partition key.
        """
        prepared = self.session.prepare("INSERT INTO tblpk (k, v) VALUES (?, ?)")
        bound_statement=prepared.bind((self.original_value, 1))
        self.session.execute(bound_statement)
        rs=self.session.execute("SELECT k,v FROM tblpk")
        foundpk=  rs[0]._asdict()['k']
        self.assertEqual(foundpk, self.original_value)

    def validate(self, value, key, expected):
        """
        Simple utility method used for validation of inserted types.
        """
        rs=self.session.execute("SELECT {0} from tbl where k={1}".format(value,key))
        retrieved=rs[0]._asdict()[value]
        self.assertEqual(expected, retrieved)


class BasicGeometricCircleTypeTest(AbstractGeometricTypeTest, BasicGeometricUnitTestCase):
    """
    Runs all the geometric tests against CircleType
    """
    cql_type_name = "'{0}'".format(CircleType.typename)
    original_value = Circle(.4, .8, 10000)


class BasicGeometricPointTypeTest(AbstractGeometricTypeTest, BasicGeometricUnitTestCase):
    """
    Runs all the geometric tests against PointType
    """
    cql_type_name = "'{0}'".format(PointType.typename)
    original_value = Point(.5, .13)


class BasicGeometricLineStringTypeTest(AbstractGeometricTypeTest, BasicGeometricUnitTestCase):
    """
    Runs all the geometric tests against LineStringType
    """
    cql_type_name =  cql_type_name = "'{0}'".format(LineStringType.typename)
    original_value = LineString(((1,2), (3,4), (9871234, 1235487215)))


class BasicGeometricPolygonTypeTest(AbstractGeometricTypeTest, BasicGeometricUnitTestCase):
    """
    Runs all the geometric tests against PolygonType
    """
    cql_type_name =  cql_type_name = "'{0}'".format(PolygonType.typename)
    original_value = Polygon([(10.0, 10.0), (110.0, 10.0), (110., 110.0), (10., 110.0), (10., 10.0)], [[(20., 20.0), (20., 30.0), (30., 30.0), (30., 20.0), (20., 20.0)], [(40., 20.0), (40., 30.0), (50., 30.0), (50., 20.0), (40., 20.0)]])



