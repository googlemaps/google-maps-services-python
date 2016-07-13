#
# Copyright 2014 Google Inc. All rights reserved.
#
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
#

"""Tests for the convert module."""

import datetime
import unittest

from googlemaps import convert


class ConvertTest(unittest.TestCase):

    def test_latlng(self):
        expected = "1,2"
        ll = {"lat": 1, "lng": 2}
        self.assertEqual(expected, convert.latlng(ll))

        ll = [1, 2]
        self.assertEqual(expected, convert.latlng(ll))

        ll = (1, 2)
        self.assertEqual(expected, convert.latlng(ll))

        self.assertEqual(expected, convert.latlng(expected))

        with self.assertRaises(TypeError):
            convert.latlng(1)

    def test_location_list(self):
        expected = "1,2|1,2"
        ll = [{"lat": 1, "lng": 2}, {"lat": 1, "lng": 2}]
        self.assertEqual(expected, convert.location_list(ll))

        ll = [[1, 2], [1, 2]]
        self.assertEqual(expected, convert.location_list(ll))

        ll = [(1, 2), [1, 2]]
        self.assertEqual(expected, convert.location_list(ll))

        self.assertEqual(expected, convert.location_list(expected))

        with self.assertRaises(TypeError):
            convert.latlng(1)

    def test_join_list(self):
        self.assertEqual("asdf", convert.join_list("|", "asdf"))

        self.assertEqual("1,2,A", convert.join_list(",", ["1", "2", "A"]))

        self.assertEqual("", convert.join_list(",", []))

        self.assertEqual("a,B", convert.join_list(",", ("a", "B")))

    def test_as_list(self):
        self.assertEqual([1], convert.as_list(1))

        self.assertEqual([1, 2, 3], convert.as_list([1, 2, 3]))

        self.assertEqual(["string"], convert.as_list("string"))

        self.assertEqual((1, 2), convert.as_list((1, 2)))

        a_dict = {"a": 1}
        self.assertEqual([a_dict], convert.as_list(a_dict))

    def test_time(self):
        self.assertEqual("1409810596", convert.time(1409810596))

        dt = datetime.datetime.fromtimestamp(1409810596)
        self.assertEqual("1409810596", convert.time(dt))

    def test_components(self):
        c = {"country": "US"}
        self.assertEqual("country:US", convert.components(c))

        c = {"country": "US", "foo": 1}
        self.assertEqual("country:US|foo:1", convert.components(c))

        c = {"country": ["US", "AU"], "foo": 1}
        self.assertEqual("country:AU|country:US|foo:1", convert.components(c))

        with self.assertRaises(TypeError):
            convert.components("test")

        with self.assertRaises(TypeError):
            convert.components(1)

        with self.assertRaises(TypeError):
            convert.components(("c", "b"))

    def test_bounds(self):
        ne = {"lat": 1, "lng": 2}
        sw = (3, 4)
        b = {"northeast": ne, "southwest": sw}
        self.assertEqual("3,4|1,2",
                          convert.bounds(b))

        with self.assertRaises(TypeError):
            convert.bounds("test")

    def test_polyline_decode(self):
        syd_mel_route = ("rvumEis{y[`NsfA~tAbF`bEj^h{@{KlfA~eA~`AbmEghAt~D|e@j"
                         "lRpO~yH_\\v}LjbBh~FdvCxu@`nCplDbcBf_B|wBhIfhCnqEb~D~"
                         "jCn_EngApdEtoBbfClf@t_CzcCpoEr_Gz_DxmAphDjjBxqCviEf}"
                         "B|pEvsEzbE~qGfpExjBlqCx}BvmLb`FbrQdpEvkAbjDllD|uDldD"
                         "j`Ef|AzcEx_Gtm@vuI~xArwD`dArlFnhEzmHjtC~eDluAfkC|eAd"
                         "hGpJh}N_mArrDlr@h|HzjDbsAvy@~~EdTxpJje@jlEltBboDjJdv"
                         "KyZpzExrAxpHfg@pmJg[tgJuqBnlIarAh}DbN`hCeOf_IbxA~uFt"
                         "|A|xEt_ArmBcN|sB|h@b_DjOzbJ{RlxCcfAp~AahAbqG~Gr}AerA"
                         "`dCwlCbaFo]twKt{@bsG|}A~fDlvBvz@tw@rpD_r@rqB{PvbHek@"
                         "vsHlh@ptNtm@fkD[~xFeEbyKnjDdyDbbBtuA|~Br|Gx_AfxCt}Cj"
                         "nHv`Ew\\lnBdrBfqBraD|{BldBxpG|]jqC`mArcBv]rdAxgBzdEb"
                         "{InaBzyC}AzaEaIvrCzcAzsCtfD~qGoPfeEh]h`BxiB`e@`kBxfA"
                         "v^pyA`}BhkCdoCtrC~bCxhCbgEplKrk@tiAteBwAxbCwuAnnCc]b"
                         "{FjrDdjGhhGzfCrlDruBzSrnGhvDhcFzw@n{@zxAf}Fd{IzaDnbD"
                         "joAjqJjfDlbIlzAraBxrB}K~`GpuD~`BjmDhkBp{@r_AxCrnAjrC"
                         "x`AzrBj{B|r@~qBbdAjtDnvCtNzpHxeApyC|GlfM`fHtMvqLjuEt"
                         "lDvoFbnCt|@xmAvqBkGreFm~@hlHw|AltC}NtkGvhBfaJ|~@riAx"
                         "uC~gErwCttCzjAdmGuF`iFv`AxsJftD|nDr_QtbMz_DheAf~Buy@"
                         "rlC`i@d_CljC`gBr|H|nAf_Fh{G|mE~kAhgKviEpaQnu@zwAlrA`"
                         "G~gFnvItz@j{Cng@j{D{]`tEftCdcIsPz{DddE~}PlnE|dJnzG`e"
                         "G`mF|aJdqDvoAwWjzHv`H`wOtjGzeXhhBlxErfCf{BtsCjpEjtD|"
                         "}Aja@xnAbdDt|ErMrdFh{CzgAnlCnr@`wEM~mE`bA`uD|MlwKxmB"
                         "vuFlhB|sN`_@fvBp`CxhCt_@loDsS|eDlmChgFlqCbjCxk@vbGxm"
                         "CjbMba@rpBaoClcCk_DhgEzYdzBl\\vsA_JfGztAbShkGtEhlDzh"
                         "C~w@hnB{e@yF}`D`_Ayx@~vGqn@l}CafC")

        points = convert.decode_polyline(syd_mel_route)
        self.assertAlmostEqual(-33.86746, points[0]["lat"])
        self.assertAlmostEqual(151.207090, points[0]["lng"])
        self.assertAlmostEqual(-37.814130, points[-1]["lat"])
        self.assertAlmostEqual(144.963180, points[-1]["lng"])

    def test_polyline_round_trip(self):
        test_polyline = ("gcneIpgxzRcDnBoBlEHzKjBbHlG`@`IkDxIi"
                         "KhKoMaLwTwHeIqHuAyGXeB~Ew@fFjAtIzExF")

        points = convert.decode_polyline(test_polyline)
        actual_polyline = convert.encode_polyline(points)
        self.assertEqual(test_polyline, actual_polyline)
