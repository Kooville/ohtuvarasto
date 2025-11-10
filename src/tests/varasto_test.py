import unittest
from varasto import Varasto


class TestVarasto(unittest.TestCase):
    def setUp(self):
        self.varasto = Varasto(10)

    def test_konstruktori_luo_tyhjan_varaston(self):
        # https://docs.python.org/3/library/unittest.html#unittest.TestCase.assertAlmostEqual
        self.assertAlmostEqual(self.varasto.saldo, 0)

    def test_uudella_varastolla_oikea_tilavuus(self):
        self.assertAlmostEqual(self.varasto.tilavuus, 10)

    def test_lisays_lisaa_saldoa(self):
        self.varasto.lisaa_varastoon(8)

        self.assertAlmostEqual(self.varasto.saldo, 8)

    def test_lisays_lisaa_pienentaa_vapaata_tilaa(self):
        self.varasto.lisaa_varastoon(8)

        # vapaata tilaa pitäisi vielä olla tilavuus-lisättävä määrä eli 2
        self.assertAlmostEqual(self.varasto.paljonko_mahtuu(), 2)

    def test_ottaminen_palauttaa_oikean_maaran(self):
        self.varasto.lisaa_varastoon(8)

        saatu_maara = self.varasto.ota_varastosta(2)

        self.assertAlmostEqual(saatu_maara, 2)

    def test_ottaminen_lisaa_tilaa(self):
        self.varasto.lisaa_varastoon(8)

        self.varasto.ota_varastosta(2)

        # varastossa pitäisi olla tilaa 10 - 8 + 2 eli 4
        self.assertAlmostEqual(self.varasto.paljonko_mahtuu(), 4)

    def test_konstruktori_negatiivinen_tilavuus_nollataan(self):
        v = Varasto(-1, 5)
        self.assertEqual(v.tilavuus, 0.0)
        # alku_saldo > tilavuus (tilavuus was set to 0.0) -> saldo should be tilavuus (0.0)
        self.assertEqual(v.saldo, 0.0)

    def test_konstruktori_negatiivinen_alkusaldo_nollataan(self):
        v = Varasto(10, -5)
        self.assertEqual(v.tilavuus, 10)
        self.assertEqual(v.saldo, 0.0)

    def test_konstruktori_alkusaldo_suurempi_kuin_tilavuus_tayttaa_varaston(self):
        v = Varasto(5, 10)
        self.assertEqual(v.tilavuus, 5)
        self.assertEqual(v.saldo, 5)

    def test_lisaa_varastoon_negatiivinen_maara_ei_muuta(self):
        v = Varasto(10, 3)
        v.lisaa_varastoon(-4)
        self.assertEqual(v.saldo, 3)

    def test_lisaa_varastoon_liikaa_tayttaa_varaston(self):
        v = Varasto(10, 7)
        v.lisaa_varastoon(10)  # yli tilavuuden
        self.assertEqual(v.saldo, 10)
        self.assertEqual(v.paljonko_mahtuu(), 0)

    def test_ota_varastosta_negatiivinen_palauttaa_nolla_ei_muuta(self):
        v = Varasto(10, 4)
        ret = v.ota_varastosta(-3)
        self.assertEqual(ret, 0.0)
        self.assertEqual(v.saldo, 4)

    def test_ota_varastosta_liikaa_palauttaa_kaiken_ja_nollaa(self):
        v = Varasto(10, 6)
        ret = v.ota_varastosta(20)
        self.assertEqual(ret, 6)
        self.assertEqual(v.saldo, 0.0)

    def test_str_palauttaa_odotetun_muodon(self):
        v = Varasto(8, 3)
        # expected: "saldo = 3, vielä tilaa 5"
        self.assertEqual(
            str(v), f"saldo = {v.saldo}, vielä tilaa {v.paljonko_mahtuu()}")

    def test_alkusaldo_tarkka_yhtasuuruus_mahtuu(self):
        v = Varasto(4, 4)  # alku_saldo == tilavuus uses elif-path
        self.assertEqual(v.saldo, 4)
        self.assertEqual(v.paljonko_mahtuu(), 0)
