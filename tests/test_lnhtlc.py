from pprint import pprint
import unittest
from typing import NamedTuple

from electrum_cat.lnutil import RECEIVED, LOCAL, REMOTE, SENT, HTLCOwner, Direction
from electrum_cat.lnhtlc import HTLCManager
from electrum_cat.json_db import StoredDict

from . import ElectrumTestCase

class H(NamedTuple):
    owner : str
    htlc_id : int

class TestHTLCManager(ElectrumTestCase):
    def test_adding_htlcs_race(self):
        A = HTLCManager(StoredDict({}, None, []))
        B = HTLCManager(StoredDict({}, None, []))
        A.channel_open_finished()
        B.channel_open_finished()
        ah0, bh0 = H('A', 0), H('B', 0)
        B.recv_htlc(A.send_htlc(ah0))
        self.assertEqual(B.log[REMOTE]['locked_in'][0][LOCAL], 1)
        A.recv_htlc(B.send_htlc(bh0))
        self.assertEqual(B.get_htlcs_in_latest_ctx(LOCAL), [])
        self.assertEqual(A.get_htlcs_in_latest_ctx(LOCAL), [])
        self.assertEqual(B.get_htlcs_in_next_ctx(LOCAL), [(RECEIVED, ah0)])
        self.assertEqual(A.get_htlcs_in_next_ctx(LOCAL), [(RECEIVED, bh0)])
        A.send_ctx()
        B.recv_ctx()
        B.send_ctx()
        A.recv_ctx()
        self.assertEqual(B.get_htlcs_in_oldest_unrevoked_ctx(LOCAL), [])
        self.assertEqual(A.get_htlcs_in_oldest_unrevoked_ctx(LOCAL), [])
        self.assertEqual(B.get_htlcs_in_latest_ctx(LOCAL), [(RECEIVED, ah0)])
        self.assertEqual(A.get_htlcs_in_latest_ctx(LOCAL), [(RECEIVED, bh0)])
        B.send_rev()
        A.recv_rev()
        A.send_rev()
        B.recv_rev()
        self.assertEqual(B.get_htlcs_in_oldest_unrevoked_ctx(LOCAL), [(RECEIVED, ah0)])
        self.assertEqual(A.get_htlcs_in_oldest_unrevoked_ctx(LOCAL), [(RECEIVED, bh0)])
        self.assertEqual(B.get_htlcs_in_latest_ctx(LOCAL), [(RECEIVED, ah0)])
        self.assertEqual(A.get_htlcs_in_latest_ctx(LOCAL), [(RECEIVED, bh0)])
        A.send_ctx()
        B.recv_ctx()
        B.send_ctx()
        A.recv_ctx()
        self.assertEqual(B.get_htlcs_in_oldest_unrevoked_ctx(LOCAL), [(RECEIVED, ah0)])
        self.assertEqual(A.get_htlcs_in_oldest_unrevoked_ctx(LOCAL), [(RECEIVED, bh0)])
        self.assertEqual(B.get_htlcs_in_latest_ctx(LOCAL), [(RECEIVED, ah0), (SENT, bh0)][::-1])
        self.assertEqual(A.get_htlcs_in_latest_ctx(LOCAL), [(RECEIVED, bh0), (SENT, ah0)][::-1])
        B.send_rev()
        A.recv_rev()
        A.send_rev()
        B.recv_rev()
        self.assertEqual(B.get_htlcs_in_oldest_unrevoked_ctx(LOCAL), [(RECEIVED, ah0), (SENT, bh0)][::-1])
        self.assertEqual(A.get_htlcs_in_oldest_unrevoked_ctx(LOCAL), [(RECEIVED, bh0), (SENT, ah0)][::-1])
        self.assertEqual(B.get_htlcs_in_latest_ctx(LOCAL), [(RECEIVED, ah0), (SENT, bh0)][::-1])
        self.assertEqual(A.get_htlcs_in_latest_ctx(LOCAL), [(RECEIVED, bh0), (SENT, ah0)][::-1])

    def test_single_htlc_full_lifecycle(self):
        def htlc_lifecycle(htlc_success: bool):
            A = HTLCManager(StoredDict({}, None, []))
            B = HTLCManager(StoredDict({}, None, []))
            A.channel_open_finished()
            B.channel_open_finished()
            B.recv_htlc(A.send_htlc(H('A', 0)))
            self.assertEqual(len(B.get_htlcs_in_next_ctx(REMOTE)), 0)
            self.assertEqual(len(A.get_htlcs_in_next_ctx(REMOTE)), 1)
            self.assertEqual(len(B.get_htlcs_in_next_ctx(LOCAL)), 1)
            self.assertEqual(len(A.get_htlcs_in_next_ctx(LOCAL)), 0)
            A.send_ctx()
            B.recv_ctx()
            B.send_rev()
            A.recv_rev()
            B.send_ctx()
            A.recv_ctx()
            A.send_rev()
            B.recv_rev()
            self.assertEqual(len(A.get_htlcs_in_latest_ctx(LOCAL)), 1)
            self.assertEqual(len(B.get_htlcs_in_latest_ctx(LOCAL)), 1)
            if htlc_success:
                B.send_settle(0)
                A.recv_settle(0)
            else:
                B.send_fail(0)
                A.recv_fail(0)
            self.assertEqual(list(A.htlcs_by_direction(REMOTE, RECEIVED).values()), [H('A', 0)])
            self.assertNotEqual(A.get_htlcs_in_latest_ctx(LOCAL), [])
            self.assertNotEqual(B.get_htlcs_in_latest_ctx(REMOTE), [])

            self.assertEqual(A.get_htlcs_in_next_ctx(LOCAL), [])
            self.assertNotEqual(A.get_htlcs_in_next_ctx(REMOTE), [])
            self.assertEqual(A.get_htlcs_in_next_ctx(REMOTE), A.get_htlcs_in_latest_ctx(REMOTE))

            self.assertEqual(B.get_htlcs_in_next_ctx(REMOTE), [])
            B.send_ctx()
            A.recv_ctx()
            A.send_rev() # here pending_htlcs(REMOTE) should become empty
            self.assertEqual(A.get_htlcs_in_next_ctx(REMOTE), [])

            B.recv_rev()
            A.send_ctx()
            B.recv_ctx()
            B.send_rev()
            A.recv_rev()
            self.assertEqual(B.get_htlcs_in_latest_ctx(LOCAL), [])
            self.assertEqual(A.get_htlcs_in_latest_ctx(LOCAL), [])
            self.assertEqual(A.get_htlcs_in_latest_ctx(REMOTE), [])
            self.assertEqual(B.get_htlcs_in_latest_ctx(REMOTE), [])
            self.assertEqual(len(A.all_settled_htlcs_ever(LOCAL)), int(htlc_success))
            self.assertEqual(len(A.sent_in_ctn(2)), int(htlc_success))
            self.assertEqual(len(B.received_in_ctn(2)), int(htlc_success))

            A.recv_htlc(B.send_htlc(H('B', 0)))
            self.assertEqual(A.get_htlcs_in_next_ctx(REMOTE), [])
            self.assertNotEqual(A.get_htlcs_in_next_ctx(LOCAL), [])
            self.assertNotEqual(B.get_htlcs_in_next_ctx(REMOTE), [])
            self.assertEqual(B.get_htlcs_in_next_ctx(LOCAL), [])

            B.send_ctx()
            A.recv_ctx()
            A.send_rev()
            B.recv_rev()

            self.assertNotEqual(A.get_htlcs_in_next_ctx(REMOTE), A.get_htlcs_in_latest_ctx(REMOTE))
            self.assertEqual(A.get_htlcs_in_next_ctx(LOCAL), A.get_htlcs_in_latest_ctx(LOCAL))
            self.assertEqual(B.get_htlcs_in_next_ctx(REMOTE), B.get_htlcs_in_latest_ctx(REMOTE))
            self.assertNotEqual(B.get_htlcs_in_next_ctx(LOCAL), B.get_htlcs_in_next_ctx(REMOTE))

        htlc_lifecycle(htlc_success=True)
        htlc_lifecycle(htlc_success=False)

    def test_remove_htlc_while_owing_commitment(self):
        def htlc_lifecycle(htlc_success: bool):
            A = HTLCManager(StoredDict({}, None, []))
            B = HTLCManager(StoredDict({}, None, []))
            A.channel_open_finished()
            B.channel_open_finished()
            ah0 = H('A', 0)
            B.recv_htlc(A.send_htlc(ah0))
            A.send_ctx()
            B.recv_ctx()
            B.send_rev()
            A.recv_rev()
            if htlc_success:
                B.send_settle(0)
                A.recv_settle(0)
            else:
                B.send_fail(0)
                A.recv_fail(0)
            self.assertEqual([], A.get_htlcs_in_oldest_unrevoked_ctx(LOCAL))
            self.assertEqual([(Direction.RECEIVED, ah0)], A.get_htlcs_in_oldest_unrevoked_ctx(REMOTE))
            self.assertEqual([], A.get_htlcs_in_latest_ctx(LOCAL))
            self.assertEqual([(Direction.RECEIVED, ah0)], A.get_htlcs_in_latest_ctx(REMOTE))
            self.assertEqual([], A.get_htlcs_in_next_ctx(LOCAL))
            self.assertEqual([(Direction.RECEIVED, ah0)], A.get_htlcs_in_next_ctx(REMOTE))
            B.send_ctx()
            A.recv_ctx()
            A.send_rev()
            B.recv_rev()
            self.assertEqual([], A.get_htlcs_in_oldest_unrevoked_ctx(LOCAL))
            self.assertEqual([(Direction.RECEIVED, ah0)], A.get_htlcs_in_oldest_unrevoked_ctx(REMOTE))
            self.assertEqual([], A.get_htlcs_in_latest_ctx(LOCAL))
            self.assertEqual([(Direction.RECEIVED, ah0)], A.get_htlcs_in_latest_ctx(REMOTE))
            self.assertEqual([], A.get_htlcs_in_next_ctx(LOCAL))
            self.assertEqual([], A.get_htlcs_in_next_ctx(REMOTE))

        htlc_lifecycle(htlc_success=True)
        htlc_lifecycle(htlc_success=False)

    def test_adding_htlc_between_send_ctx_and_recv_rev(self):
        A = HTLCManager(StoredDict({}, None, []))
        B = HTLCManager(StoredDict({}, None, []))
        A.channel_open_finished()
        B.channel_open_finished()
        A.send_ctx()
        B.recv_ctx()
        B.send_rev()
        ah0 = H('A', 0)
        B.recv_htlc(A.send_htlc(ah0))
        self.assertEqual([], A.get_htlcs_in_latest_ctx(LOCAL))
        self.assertEqual([], A.get_htlcs_in_latest_ctx(REMOTE))
        self.assertEqual([], A.get_htlcs_in_next_ctx(LOCAL))
        self.assertEqual([(Direction.RECEIVED, ah0)], A.get_htlcs_in_next_ctx(REMOTE))
        A.recv_rev()
        self.assertEqual([], A.get_htlcs_in_latest_ctx(LOCAL))
        self.assertEqual([], A.get_htlcs_in_latest_ctx(REMOTE))
        self.assertEqual([], A.get_htlcs_in_next_ctx(LOCAL))
        self.assertEqual([(Direction.RECEIVED, ah0)], A.get_htlcs_in_next_ctx(REMOTE))
        A.send_ctx()
        B.recv_ctx()
        self.assertEqual([], A.get_htlcs_in_latest_ctx(LOCAL))
        self.assertEqual([(Direction.RECEIVED, ah0)], A.get_htlcs_in_latest_ctx(REMOTE))
        self.assertEqual([], A.get_htlcs_in_next_ctx(LOCAL))
        self.assertEqual([(Direction.RECEIVED, ah0)], A.get_htlcs_in_next_ctx(REMOTE))
        B.send_rev()
        A.recv_rev()
        self.assertEqual([], A.get_htlcs_in_latest_ctx(LOCAL))
        self.assertEqual([(Direction.RECEIVED, ah0)], A.get_htlcs_in_latest_ctx(REMOTE))
        self.assertEqual([(Direction.SENT, ah0)], A.get_htlcs_in_next_ctx(LOCAL))
        self.assertEqual([(Direction.RECEIVED, ah0)], A.get_htlcs_in_next_ctx(REMOTE))
        B.send_ctx()
        A.recv_ctx()
        self.assertEqual([], A.get_htlcs_in_oldest_unrevoked_ctx(LOCAL))
        self.assertEqual([(Direction.SENT, ah0)], A.get_htlcs_in_latest_ctx(LOCAL))
        self.assertEqual([(Direction.RECEIVED, ah0)], A.get_htlcs_in_latest_ctx(REMOTE))
        self.assertEqual([(Direction.SENT, ah0)], A.get_htlcs_in_next_ctx(LOCAL))
        self.assertEqual([(Direction.RECEIVED, ah0)], A.get_htlcs_in_next_ctx(REMOTE))
        A.send_rev()
        B.recv_rev()
        self.assertEqual([(Direction.SENT, ah0)], A.get_htlcs_in_oldest_unrevoked_ctx(LOCAL))
        self.assertEqual([(Direction.SENT, ah0)], A.get_htlcs_in_latest_ctx(LOCAL))
        self.assertEqual([(Direction.RECEIVED, ah0)], A.get_htlcs_in_latest_ctx(REMOTE))
        self.assertEqual([(Direction.SENT, ah0)], A.get_htlcs_in_next_ctx(LOCAL))
        self.assertEqual([(Direction.RECEIVED, ah0)], A.get_htlcs_in_next_ctx(REMOTE))

    def test_unacked_local_updates(self):
        A = HTLCManager(StoredDict({}, None, []))
        B = HTLCManager(StoredDict({}, None, []))
        A.channel_open_finished()
        B.channel_open_finished()
        self.assertEqual({}, A.get_unacked_local_updates())

        ah0 = H('A', 0)
        B.recv_htlc(A.send_htlc(ah0))
        A.store_local_update_raw_msg(b"upd_msg0", is_commitment_signed=False)
        self.assertEqual({1: [b"upd_msg0"]}, A.get_unacked_local_updates())

        ah1 = H('A', 1)
        B.recv_htlc(A.send_htlc(ah1))
        A.store_local_update_raw_msg(b"upd_msg1", is_commitment_signed=False)
        self.assertEqual({1: [b"upd_msg0", b"upd_msg1"]}, A.get_unacked_local_updates())

        A.send_ctx()
        B.recv_ctx()
        A.store_local_update_raw_msg(b"ctx1", is_commitment_signed=True)
        self.assertEqual({1: [b"upd_msg0", b"upd_msg1", b"ctx1"]}, A.get_unacked_local_updates())

        ah2 = H('A', 2)
        B.recv_htlc(A.send_htlc(ah2))
        A.store_local_update_raw_msg(b"upd_msg2", is_commitment_signed=False)
        self.assertEqual({1: [b"upd_msg0", b"upd_msg1", b"ctx1"], 2: [b"upd_msg2"]}, A.get_unacked_local_updates())

        B.send_rev()
        A.recv_rev()
        self.assertEqual({2: [b"upd_msg2"]}, A.get_unacked_local_updates())
