# Copyright 2016 DataStax, Inc.
#
# Licensed under the DataStax DSE Driver License;
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at
#
# http://www.datastax.com/terms/datastax-dse-driver-license-terms

import mock
from uuid import uuid4

from dse import ConsistencyLevel as CL, ConsistencyLevel
from dse.cluster import Session
from dse.cqlengine import columns
from dse.cqlengine import connection
from dse.cqlengine.management import sync_table, drop_table
from dse.cqlengine.models import Model
from dse.cqlengine.query import BatchQuery

from tests.integration.cqlengine.base import BaseCassEngTestCase

class TestConsistencyModel(Model):

    id      = columns.UUID(primary_key=True, default=lambda:uuid4())
    count   = columns.Integer()
    text    = columns.Text(required=False)

class BaseConsistencyTest(BaseCassEngTestCase):

    @classmethod
    def setUpClass(cls):
        super(BaseConsistencyTest, cls).setUpClass()
        sync_table(TestConsistencyModel)

    @classmethod
    def tearDownClass(cls):
        super(BaseConsistencyTest, cls).tearDownClass()
        drop_table(TestConsistencyModel)


class TestConsistency(BaseConsistencyTest):
    def test_create_uses_consistency(self):

        qs = TestConsistencyModel.consistency(CL.ALL)
        with mock.patch.object(self.session, 'execute') as m:
            qs.create(text="i am not fault tolerant this way")

        args = m.call_args
        self.assertEqual(CL.ALL, args[0][0].consistency_level)

    def test_queryset_is_returned_on_create(self):
        qs = TestConsistencyModel.consistency(CL.ALL)
        self.assertTrue(isinstance(qs, TestConsistencyModel.__queryset__), type(qs))

    def test_update_uses_consistency(self):
        t = TestConsistencyModel.create(text="bacon and eggs")
        t.text = "ham sandwich"

        with mock.patch.object(self.session, 'execute') as m:
            t.consistency(CL.ALL).save()

        args = m.call_args
        self.assertEqual(CL.ALL, args[0][0].consistency_level)

    def test_batch_consistency(self):

        with mock.patch.object(self.session, 'execute') as m:
            with BatchQuery(consistency=CL.ALL) as b:
                TestConsistencyModel.batch(b).create(text="monkey")

        args = m.call_args

        self.assertEqual(CL.ALL, args[0][0].consistency_level)

        with mock.patch.object(self.session, 'execute') as m:
            with BatchQuery() as b:
                TestConsistencyModel.batch(b).create(text="monkey")

        args = m.call_args
        self.assertNotEqual(CL.ALL, args[0][0].consistency_level)

    def test_blind_update(self):
        t = TestConsistencyModel.create(text="bacon and eggs")
        t.text = "ham sandwich"
        uid = t.id

        with mock.patch.object(self.session, 'execute') as m:
            TestConsistencyModel.objects(id=uid).consistency(CL.ALL).update(text="grilled cheese")

        args = m.call_args
        self.assertEqual(CL.ALL, args[0][0].consistency_level)

    def test_delete(self):
        # ensures we always carry consistency through on delete statements
        t = TestConsistencyModel.create(text="bacon and eggs")
        t.text = "ham and cheese sandwich"
        uid = t.id

        with mock.patch.object(self.session, 'execute') as m:
            t.consistency(CL.ALL).delete()

        with mock.patch.object(self.session, 'execute') as m:
            TestConsistencyModel.objects(id=uid).consistency(CL.ALL).delete()

        args = m.call_args
        self.assertEqual(CL.ALL, args[0][0].consistency_level)

    def test_default_consistency(self):
        # verify global assumed default
        self.assertEqual(Session._default_consistency_level, ConsistencyLevel.LOCAL_ONE)

        # verify that this session default is set according to connection.setup
        # assumes tests/cqlengine/__init__ setup uses CL.ONE
        session = connection.get_session()
        self.assertEqual(session.cluster.profile_manager.default.consistency_level, ConsistencyLevel.ONE)
