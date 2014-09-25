"""Tests for the convert module."""

import datetime
import unittest

from googlemaps import convert


class ConvertTest(unittest.TestCase):

    def test_latlng(self):
        ll = {"lat": 1, "lng": 2}
        self.assertEqual("1.000000,2.000000", convert.latlng(ll))

        ll = [1, 2]
        self.assertEqual("1.000000,2.000000", convert.latlng(ll))

        ll = (1, 2)
        self.assertEqual("1.000000,2.000000", convert.latlng(ll))

        with self.assertRaises(TypeError):
            convert.latlng(1)

        with self.assertRaises(TypeError):
            convert.latlng("test")

    def test_join_list(self):
        self.assertEquals("asdf", convert.join_list("|", "asdf"))

        self.assertEquals("1,2,A", convert.join_list(",", ["1", "2", "A"]))

        self.assertEquals("", convert.join_list(",", []))

        self.assertEquals("a,B", convert.join_list(",", ("a", "B")))

    def test_as_list(self):
        self.assertEquals([1], convert.as_list(1))

        self.assertEquals([1, 2, 3], convert.as_list([1, 2, 3]))

        self.assertEquals(["string"], convert.as_list("string"))

        self.assertEquals((1, 2), convert.as_list((1, 2)))

    def test_time(self):
        self.assertEquals("1409810596", convert.time(1409810596))

        dt = datetime.datetime.fromtimestamp(1409810596)
        self.assertEquals("1409810596", convert.time(dt))

    def test_components(self):
        c = {"country": "US"}
        self.assertEquals("country:US", convert.components(c))

        c = {"country": "US", "foo": 1}
        self.assertEquals("country:US|foo:1", convert.components(c))

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
        self.assertEquals("3.000000,4.000000|1.000000,2.000000",
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
        self.assertAlmostEquals(-33.86746, points[0]["lat"])
        self.assertAlmostEquals(151.207090, points[0]["lng"])
        self.assertAlmostEquals(-37.814130, points[-1]["lat"])
        self.assertAlmostEquals(144.963180, points[-1]["lng"])

    def test_polyline_round_trip(self):
        test_polyline = ("gcneIpgxzRcDnBoBlEHzKjBbHlG`@`IkDxIi"
                         "KhKoMaLwTwHeIqHuAyGXeB~Ew@fFjAtIzExF")

        points = convert.decode_polyline(test_polyline)
        actual_polyline = convert.encode_polyline(points)
        self.assertEquals(test_polyline, actual_polyline)