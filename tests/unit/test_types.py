# Copyright 2016-2017 DataStax, Inc.
#
# Licensed under the DataStax DSE Driver License;
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at
#
# http://www.datastax.com/terms/datastax-dse-driver-license-terms
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # noqa

from binascii import unhexlify
import datetime
import tempfile
import six
import time

import dse
from dse.cqltypes import (BooleanType, lookup_casstype_simple, lookup_casstype,
                                LongType, DecimalType, SetType, cql_typename,
                                CassandraType, UTF8Type, parse_casstype_args,
                                SimpleDateType, TimeType, ByteType, ShortType,
                                EmptyValue, _CassandraType, DateType, int64_pack,
                                DateRangeType, int8_pack, int32_pack)
from dse.encoder import cql_quote
from dse.protocol import (write_string, read_longstring, write_stringmap,
                                read_stringmap, read_inet, write_inet,
                                read_string, write_longstring)
from dse import util
from dse.metadata import Token
from dse.hosts import Host
from dse.policies import SimpleConvictionPolicy, ConvictionPolicy
from dse.query import named_tuple_factory
from dse.util import Date, Time
from tests.unit.util import check_sequence_consistency


class TypeTests(unittest.TestCase):

    def test_lookup_casstype_simple(self):
        """
        Ensure lookup_casstype_simple returns the correct classes
        """

        self.assertEqual(lookup_casstype_simple('AsciiType'), dse.cqltypes.AsciiType)
        self.assertEqual(lookup_casstype_simple('LongType'), dse.cqltypes.LongType)
        self.assertEqual(lookup_casstype_simple('BytesType'), dse.cqltypes.BytesType)
        self.assertEqual(lookup_casstype_simple('BooleanType'), dse.cqltypes.BooleanType)
        self.assertEqual(lookup_casstype_simple('CounterColumnType'), dse.cqltypes.CounterColumnType)
        self.assertEqual(lookup_casstype_simple('DecimalType'), dse.cqltypes.DecimalType)
        self.assertEqual(lookup_casstype_simple('DoubleType'), dse.cqltypes.DoubleType)
        self.assertEqual(lookup_casstype_simple('FloatType'), dse.cqltypes.FloatType)
        self.assertEqual(lookup_casstype_simple('InetAddressType'), dse.cqltypes.InetAddressType)
        self.assertEqual(lookup_casstype_simple('Int32Type'), dse.cqltypes.Int32Type)
        self.assertEqual(lookup_casstype_simple('UTF8Type'), dse.cqltypes.UTF8Type)
        self.assertEqual(lookup_casstype_simple('DateType'), dse.cqltypes.DateType)
        self.assertEqual(lookup_casstype_simple('SimpleDateType'), dse.cqltypes.SimpleDateType)
        self.assertEqual(lookup_casstype_simple('ByteType'), dse.cqltypes.ByteType)
        self.assertEqual(lookup_casstype_simple('ShortType'), dse.cqltypes.ShortType)
        self.assertEqual(lookup_casstype_simple('TimeUUIDType'), dse.cqltypes.TimeUUIDType)
        self.assertEqual(lookup_casstype_simple('TimeType'), dse.cqltypes.TimeType)
        self.assertEqual(lookup_casstype_simple('UUIDType'), dse.cqltypes.UUIDType)
        self.assertEqual(lookup_casstype_simple('IntegerType'), dse.cqltypes.IntegerType)
        self.assertEqual(lookup_casstype_simple('MapType'), dse.cqltypes.MapType)
        self.assertEqual(lookup_casstype_simple('ListType'), dse.cqltypes.ListType)
        self.assertEqual(lookup_casstype_simple('SetType'), dse.cqltypes.SetType)
        self.assertEqual(lookup_casstype_simple('CompositeType'), dse.cqltypes.CompositeType)
        self.assertEqual(lookup_casstype_simple('ColumnToCollectionType'), dse.cqltypes.ColumnToCollectionType)
        self.assertEqual(lookup_casstype_simple('ReversedType'), dse.cqltypes.ReversedType)
        self.assertEqual(lookup_casstype_simple('DurationType'), dse.cqltypes.DurationType)
        self.assertEqual(lookup_casstype_simple('DateRangeType'), dse.cqltypes.DateRangeType)

        self.assertEqual(str(lookup_casstype_simple('unknown')), str(dse.cqltypes.mkUnrecognizedType('unknown')))

    def test_lookup_casstype(self):
        """
        Ensure lookup_casstype returns the correct classes
        """

        self.assertEqual(lookup_casstype('AsciiType'), dse.cqltypes.AsciiType)
        self.assertEqual(lookup_casstype('LongType'), dse.cqltypes.LongType)
        self.assertEqual(lookup_casstype('BytesType'), dse.cqltypes.BytesType)
        self.assertEqual(lookup_casstype('BooleanType'), dse.cqltypes.BooleanType)
        self.assertEqual(lookup_casstype('CounterColumnType'), dse.cqltypes.CounterColumnType)
        self.assertEqual(lookup_casstype('DateType'), dse.cqltypes.DateType)
        self.assertEqual(lookup_casstype('DecimalType'), dse.cqltypes.DecimalType)
        self.assertEqual(lookup_casstype('DoubleType'), dse.cqltypes.DoubleType)
        self.assertEqual(lookup_casstype('FloatType'), dse.cqltypes.FloatType)
        self.assertEqual(lookup_casstype('InetAddressType'), dse.cqltypes.InetAddressType)
        self.assertEqual(lookup_casstype('Int32Type'), dse.cqltypes.Int32Type)
        self.assertEqual(lookup_casstype('UTF8Type'), dse.cqltypes.UTF8Type)
        self.assertEqual(lookup_casstype('DateType'), dse.cqltypes.DateType)
        self.assertEqual(lookup_casstype('TimeType'), dse.cqltypes.TimeType)
        self.assertEqual(lookup_casstype('ByteType'), dse.cqltypes.ByteType)
        self.assertEqual(lookup_casstype('ShortType'), dse.cqltypes.ShortType)
        self.assertEqual(lookup_casstype('TimeUUIDType'), dse.cqltypes.TimeUUIDType)
        self.assertEqual(lookup_casstype('UUIDType'), dse.cqltypes.UUIDType)
        self.assertEqual(lookup_casstype('IntegerType'), dse.cqltypes.IntegerType)
        self.assertEqual(lookup_casstype('MapType'), dse.cqltypes.MapType)
        self.assertEqual(lookup_casstype('ListType'), dse.cqltypes.ListType)
        self.assertEqual(lookup_casstype('SetType'), dse.cqltypes.SetType)
        self.assertEqual(lookup_casstype('CompositeType'), dse.cqltypes.CompositeType)
        self.assertEqual(lookup_casstype('ColumnToCollectionType'), dse.cqltypes.ColumnToCollectionType)
        self.assertEqual(lookup_casstype('ReversedType'), dse.cqltypes.ReversedType)
        self.assertEqual(lookup_casstype('DurationType'), dse.cqltypes.DurationType)
        self.assertEqual(lookup_casstype('DateRangeType'), dse.cqltypes.DateRangeType)

        self.assertEqual(str(lookup_casstype('unknown')), str(dse.cqltypes.mkUnrecognizedType('unknown')))

        self.assertRaises(ValueError, lookup_casstype, 'AsciiType~')

    def test_casstype_parameterized(self):
        self.assertEqual(LongType.cass_parameterized_type_with(()), 'LongType')
        self.assertEqual(LongType.cass_parameterized_type_with((), full=True), 'org.apache.cassandra.db.marshal.LongType')
        self.assertEqual(SetType.cass_parameterized_type_with([DecimalType], full=True), 'org.apache.cassandra.db.marshal.SetType(org.apache.cassandra.db.marshal.DecimalType)')

        self.assertEqual(LongType.cql_parameterized_type(), 'bigint')

        subtypes = (dse.cqltypes.UTF8Type, dse.cqltypes.UTF8Type)
        self.assertEqual('map<text, text>',
                         dse.cqltypes.MapType.apply_parameters(subtypes).cql_parameterized_type())

    def test_datetype_from_string(self):
        # Ensure all formats can be parsed, without exception
        for format in dse.cqltypes.cql_timestamp_formats:
            date_string = str(datetime.datetime.now().strftime(format))
            dse.cqltypes.DateType.interpret_datestring(date_string)

    def test_cql_typename(self):
        """
        Smoke test cql_typename
        """

        self.assertEqual(cql_typename('DateType'), 'timestamp')
        self.assertEqual(cql_typename('org.apache.cassandra.db.marshal.ListType(IntegerType)'), 'list<varint>')

    def test_named_tuple_colname_substitution(self):
        colnames = ("func(abc)", "[applied]", "func(func(abc))", "foo_bar", "foo_bar_")
        rows = [(1, 2, 3, 4, 5)]
        result = named_tuple_factory(colnames, rows)[0]
        self.assertEqual(result[0], result.func_abc)
        self.assertEqual(result[1], result.applied)
        self.assertEqual(result[2], result.func_func_abc)
        self.assertEqual(result[3], result.foo_bar)
        self.assertEqual(result[4], result.foo_bar_)

    def test_parse_casstype_args(self):
        class FooType(CassandraType):
            typename = 'org.apache.cassandra.db.marshal.FooType'

            def __init__(self, subtypes, names):
                self.subtypes = subtypes
                self.names = names

            @classmethod
            def apply_parameters(cls, subtypes, names):
                return cls(subtypes, [unhexlify(six.b(name)) if name is not None else name for name in names])

        class BarType(FooType):
            typename = 'org.apache.cassandra.db.marshal.BarType'

        ctype = parse_casstype_args(''.join((
            'org.apache.cassandra.db.marshal.FooType(',
                '63697479:org.apache.cassandra.db.marshal.UTF8Type,',
                'BarType(61646472657373:org.apache.cassandra.db.marshal.UTF8Type),',
                '7a6970:org.apache.cassandra.db.marshal.UTF8Type',
            ')')))

        self.assertEqual(FooType, ctype.__class__)

        self.assertEqual(UTF8Type, ctype.subtypes[0])

        # middle subtype should be a BarType instance with its own subtypes and names
        self.assertIsInstance(ctype.subtypes[1], BarType)
        self.assertEqual([UTF8Type], ctype.subtypes[1].subtypes)
        self.assertEqual([b"address"], ctype.subtypes[1].names)

        self.assertEqual(UTF8Type, ctype.subtypes[2])
        self.assertEqual([b'city', None, b'zip'], ctype.names)

    def test_empty_value(self):
        self.assertEqual(str(EmptyValue()), 'EMPTY')

    def test_datetype(self):
        now_time_seconds = time.time()
        now_datetime = datetime.datetime.utcfromtimestamp(now_time_seconds)

        # Cassandra timestamps in millis
        now_timestamp = now_time_seconds * 1e3

        # same results serialized
        self.assertEqual(DateType.serialize(now_datetime, 0), DateType.serialize(now_timestamp, 0))

        # deserialize
        # epoc
        expected = 0
        self.assertEqual(DateType.deserialize(int64_pack(1000 * expected), 0), datetime.datetime.utcfromtimestamp(expected))

        # beyond 32b
        expected = 2 ** 33
        self.assertEqual(DateType.deserialize(int64_pack(1000 * expected), 0), datetime.datetime(2242, 3, 16, 12, 56, 32))

        # less than epoc (PYTHON-119)
        expected = -770172256
        self.assertEqual(DateType.deserialize(int64_pack(1000 * expected), 0), datetime.datetime(1945, 8, 5, 23, 15, 44))

        # work around rounding difference among Python versions (PYTHON-230)
        expected = 1424817268.274
        self.assertEqual(DateType.deserialize(int64_pack(int(1000 * expected)), 0), datetime.datetime(2015, 2, 24, 22, 34, 28, 274000))

        # Large date overflow (PYTHON-452)
        expected = 2177403010.123
        self.assertEqual(DateType.deserialize(int64_pack(int(1000 * expected)), 0), datetime.datetime(2038, 12, 31, 10, 10, 10, 123000))

    def test_write_read_string(self):
        with tempfile.TemporaryFile() as f:
            value = u'test'
            write_string(f, value)
            f.seek(0)
            self.assertEqual(read_string(f), value)

    def test_write_read_longstring(self):
        with tempfile.TemporaryFile() as f:
            value = u'test'
            write_longstring(f, value)
            f.seek(0)
            self.assertEqual(read_longstring(f), value)

    def test_write_read_stringmap(self):
        with tempfile.TemporaryFile() as f:
            value = {'key': 'value'}
            write_stringmap(f, value)
            f.seek(0)
            self.assertEqual(read_stringmap(f), value)

    def test_write_read_inet(self):
        with tempfile.TemporaryFile() as f:
            value = ('192.168.1.1', 9042)
            write_inet(f, value)
            f.seek(0)
            self.assertEqual(read_inet(f), value)

        with tempfile.TemporaryFile() as f:
            value = ('2001:db8:0:f101::1', 9042)
            write_inet(f, value)
            f.seek(0)
            self.assertEqual(read_inet(f), value)

    def test_cql_quote(self):
        self.assertEqual(cql_quote(u'test'), "'test'")
        self.assertEqual(cql_quote('test'), "'test'")
        self.assertEqual(cql_quote(0), '0')

class DateRangeTypeTests(unittest.TestCase):
    dt = datetime.datetime(1990, 2, 3, 13, 58, 45, 777777)
    timestamp = 1485963732404

    def test_decode_precision(self):
        self.assertEqual(DateRangeType._decode_precision(6), 'MILLISECOND')

    def test_decode_precision_error(self):
        with self.assertRaises(ValueError):
            DateRangeType._decode_precision(-1)

    def test_encode_precision(self):
        self.assertEqual(DateRangeType._encode_precision('SECOND'), 5)

    def test_encode_precision_error(self):
        with self.assertRaises(ValueError):
            DateRangeType._encode_precision('INVALID')

    def test_deserialize_single_value(self):
        serialized = (int8_pack(0) +
                      int64_pack(self.timestamp) +
                      int8_pack(3))
        self.assertEqual(
            DateRangeType.deserialize(serialized, 5),
            util.DateRange(value=util.DateRangeBound(
                value=datetime.datetime(2017, 2, 1, 15, 42, 12, 404000),
                precision='HOUR')
            )
        )

    def test_deserialize_closed_range(self):
        serialized = (int8_pack(1) +
                      int64_pack(self.timestamp) +
                      int8_pack(2) +
                      int64_pack(self.timestamp) +
                      int8_pack(6))
        self.assertEqual(
            DateRangeType.deserialize(serialized, 5),
            util.DateRange(
                lower_bound=util.DateRangeBound(
                    value=datetime.datetime(2017, 2, 1, 0, 0),
                    precision='DAY'
                ),
                upper_bound=util.DateRangeBound(
                    value=datetime.datetime(2017, 2, 1, 15, 42, 12, 404000),
                    precision='MILLISECOND'
                )
            )
        )

    def test_deserialize_open_high(self):
        serialized = (int8_pack(2) +
                      int64_pack(self.timestamp) +
                      int8_pack(3))
        deserialized = DateRangeType.deserialize(serialized, 5)
        self.assertEqual(
            deserialized,
            util.DateRange(
                lower_bound=util.DateRangeBound(
                    value=datetime.datetime(2017, 2, 1, 15, 0),
                    precision='HOUR'
                ),
                upper_bound=util.OPEN_BOUND
            )
        )

    def test_deserialize_open_low(self):
        serialized = (int8_pack(3) +
                      int64_pack(self.timestamp) +
                      int8_pack(4))
        deserialized = DateRangeType.deserialize(serialized, 5)
        self.assertEqual(
            deserialized,
            util.DateRange(
                lower_bound=util.OPEN_BOUND,
                upper_bound=util.DateRangeBound(
                    value=datetime.datetime(2017, 2, 1, 15, 42, 20, 1000),
                    precision='MINUTE'
                )
            )
        )

    def test_deserialize_single_open(self):
        self.assertEqual(
            util.DateRange(value=util.OPEN_BOUND),
            DateRangeType.deserialize(int8_pack(5), 5)
        )

    def test_serialize_single_value(self):
        serialized = (int8_pack(0) +
                      int64_pack(self.timestamp) +
                      int8_pack(5))
        deserialized = DateRangeType.deserialize(serialized, 5)
        self.assertEqual(
            deserialized,
            util.DateRange(
                value=util.DateRangeBound(
                    value=datetime.datetime(2017, 2, 1, 15, 42, 12),
                    precision='SECOND'
                )
            )
        )

    def test_serialize_closed_range(self):
        serialized = (int8_pack(1) +
                      int64_pack(self.timestamp) +
                      int8_pack(5) +
                      int64_pack(self.timestamp) +
                      int8_pack(0))
        deserialized = DateRangeType.deserialize(serialized, 5)
        self.assertEqual(
            deserialized,
            util.DateRange(
                lower_bound=util.DateRangeBound(
                    value=datetime.datetime(2017, 2, 1, 15, 42, 12),
                    precision='SECOND'
                ),
                upper_bound=util.DateRangeBound(
                    value=datetime.datetime(2017, 12, 31),
                    precision='YEAR'
                )
            )
        )

    def test_serialize_open_high(self):
        serialized = (int8_pack(2) +
                      int64_pack(self.timestamp) +
                      int8_pack(2))
        deserialized = DateRangeType.deserialize(serialized, 5)
        self.assertEqual(
            deserialized,
            util.DateRange(
                lower_bound=util.DateRangeBound(
                    value=datetime.datetime(2017, 2, 1),
                    precision='DAY'
                ),
                upper_bound=util.OPEN_BOUND
            )
        )

    def test_serialize_open_low(self):
        serialized = (int8_pack(2) +
                      int64_pack(self.timestamp) +
                      int8_pack(3))
        deserialized = DateRangeType.deserialize(serialized, 5)
        self.assertEqual(
            deserialized,
            util.DateRange(
                lower_bound=util.DateRangeBound(
                    value=datetime.datetime(2017, 2, 1, 15),
                    precision='HOUR'
                ),
                upper_bound=util.OPEN_BOUND
            )
        )

    def test_deserialize_both_open(self):
        serialized = (int8_pack(4))
        deserialized = DateRangeType.deserialize(serialized, 5)
        self.assertEqual(
            deserialized,
            util.DateRange(
                lower_bound=util.OPEN_BOUND,
                upper_bound=util.OPEN_BOUND
            )
        )

    def test_serialize_single_open(self):
        serialized = DateRangeType.serialize(util.DateRange(
            value=util.OPEN_BOUND,
        ), 5)
        self.assertEqual(int8_pack(5), serialized)

    def test_serialize_both_open(self):
        serialized = DateRangeType.serialize(util.DateRange(
            lower_bound=util.OPEN_BOUND,
            upper_bound=util.OPEN_BOUND
        ), 5)
        self.assertEqual(int8_pack(4), serialized)

    def test_failure_to_serialize_no_value_object(self):
        self.assertRaises(ValueError, DateRangeType.serialize, object(), 5)

    def test_failure_to_serialize_no_bounds_object(self):
        class no_bounds_object(object):
            value = lower_bound = None
        self.assertRaises(ValueError, DateRangeType.serialize, no_bounds_object, 5)

    def test_serialized_value_round_trip(self):
        vals = [six.b('\x01\x00\x00\x01%\xe9a\xf9\xd1\x06\x00\x00\x01v\xbb>o\xff\x00'),
                six.b('\x01\x00\x00\x00\xdcm\x03-\xd1\x06\x00\x00\x01v\xbb>o\xff\x00')]
        for serialized in vals:
            self.assertEqual(
                serialized,
                DateRangeType.serialize(DateRangeType.deserialize(serialized, 0), 0)
            )

    def test_serialize_zero_datetime(self):
        """
        Test serialization where timestamp = 0

        Companion test for test_deserialize_zero_datetime

        @since 2.0.0
        @jira_ticket PYTHON-729
        @expected_result serialization doesn't raise an error

        @test_category data_types
        """
        DateRangeType.serialize(util.DateRange(
            lower_bound=(datetime.datetime(1970, 1, 1), 'YEAR'),
            upper_bound=(datetime.datetime(1970, 1, 1), 'YEAR')
        ), 5)

    def test_deserialize_zero_datetime(self):
        """
        Test deserialization where timestamp = 0

        Reproduces PYTHON-729

        @since 2.0.0
        @jira_ticket PYTHON-729
        @expected_result deserialization doesn't raise an error

        @test_category data_types
        """
        DateRangeType.deserialize(
            (int8_pack(1) +
             int64_pack(0) + int8_pack(0) +
             int64_pack(0) + int8_pack(0)),
            5
        )


class TestOrdering(unittest.TestCase):
    def _shuffle_lists(self, *args):
        return [item for sublist in zip(*args) for item in sublist]

    def test_host_order(self):
        """
        Test Host class is ordered consistently

        @since 3.9
        @jira_ticket PYTHON-714
        @expected_result the hosts are ordered correctly

        @test_category data_types
        """
        hosts = [Host(addr, SimpleConvictionPolicy) for addr in
                 ("127.0.0.1", "127.0.0.2", "127.0.0.3", "127.0.0.4")]
        hosts_equal = [Host(addr, SimpleConvictionPolicy) for addr in
                       ("127.0.0.1", "127.0.0.1")]
        hosts_equal_conviction = [Host("127.0.0.1", SimpleConvictionPolicy), Host("127.0.0.1", ConvictionPolicy)]
        check_sequence_consistency(self, hosts)
        check_sequence_consistency(self, hosts_equal, equal=True)
        check_sequence_consistency(self, hosts_equal_conviction, equal=True)

    def test_date_order(self):
        """
        Test Date class is ordered consistently

        @since 3.9
        @jira_ticket PYTHON-714
        @expected_result the dates are ordered correctly

        @test_category data_types
        """
        dates_from_string = [Date("2017-01-01"), Date("2017-01-05"), Date("2017-01-09"), Date("2017-01-13")]
        dates_from_string_equal = [Date("2017-01-01"), Date("2017-01-01")]
        check_sequence_consistency(self, dates_from_string)
        check_sequence_consistency(self, dates_from_string_equal, equal=True)

        date_format = "%Y-%m-%d"

        dates_from_value = [
            Date((datetime.datetime.strptime(dtstr, date_format) -
                  datetime.datetime(1970, 1, 1)).days)
            for dtstr in ("2017-01-02", "2017-01-06", "2017-01-10", "2017-01-14")
        ]
        dates_from_value_equal = [Date(1), Date(1)]
        check_sequence_consistency(self, dates_from_value)
        check_sequence_consistency(self, dates_from_value_equal, equal=True)

        dates_from_datetime = [Date(datetime.datetime.strptime(dtstr, date_format))
                               for dtstr in ("2017-01-03", "2017-01-07", "2017-01-11", "2017-01-15")]
        dates_from_datetime_equal = [Date(datetime.datetime.strptime("2017-01-01", date_format)),
                               Date(datetime.datetime.strptime("2017-01-01", date_format))]
        check_sequence_consistency(self, dates_from_datetime)
        check_sequence_consistency(self, dates_from_datetime_equal, equal=True)

        dates_from_date = [
            Date(datetime.datetime.strptime(dtstr, date_format).date()) for dtstr in
            ("2017-01-04", "2017-01-08", "2017-01-12", "2017-01-16")
        ]
        dates_from_date_equal = [datetime.datetime.strptime(dtstr, date_format) for dtstr in
                                 ("2017-01-09", "2017-01-9")]

        check_sequence_consistency(self, dates_from_date)
        check_sequence_consistency(self, dates_from_date_equal, equal=True)

        check_sequence_consistency(self, self._shuffle_lists(dates_from_string, dates_from_value,
                                                             dates_from_datetime, dates_from_date))

    def test_timer_order(self):
        """
        Test Time class is ordered consistently

        @since 3.9
        @jira_ticket PYTHON-714
        @expected_result the times are ordered correctly

        @test_category data_types
        """
        time_from_int = [Time(1000), Time(4000), Time(7000), Time(10000)]
        time_from_int_equal = [Time(1), Time(1)]
        check_sequence_consistency(self, time_from_int)
        check_sequence_consistency(self, time_from_int_equal, equal=True)

        time_from_datetime = [Time(datetime.time(hour=0, minute=0, second=0, microsecond=us))
                              for us in (2, 5, 8, 11)]
        time_from_datetime_equal = [Time(datetime.time(hour=0, minute=0, second=0, microsecond=us))
                                    for us in (1, 1)]
        check_sequence_consistency(self, time_from_datetime)
        check_sequence_consistency(self, time_from_datetime_equal, equal=True)

        time_from_string = [Time("00:00:00.000003000"), Time("00:00:00.000006000"),
                            Time("00:00:00.000009000"), Time("00:00:00.000012000")]
        time_from_string_equal = [Time("00:00:00.000004000"), Time("00:00:00.000004000")]
        check_sequence_consistency(self, time_from_string)
        check_sequence_consistency(self, time_from_string_equal, equal=True)

        check_sequence_consistency(self, self._shuffle_lists(time_from_int, time_from_datetime, time_from_string))

    def test_token_order(self):
        """
        Test Token class is ordered consistently

        @since 3.9
        @jira_ticket PYTHON-714
        @expected_result the tokens are ordered correctly

        @test_category data_types
        """
        tokens = [Token(1), Token(2), Token(3), Token(4)]
        tokens_equal = [Token(1), Token(1)]
        check_sequence_consistency(self, tokens)
        check_sequence_consistency(self, tokens_equal, equal=True)
