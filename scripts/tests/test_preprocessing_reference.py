import struct
import tempfile
import unittest
from pathlib import Path

from preprocessing_reference import beta, read_means, signals


class IndependentOracleTests(unittest.TestCase):
    def test_type_i_channels_use_two_addresses_in_the_selected_channel(self) -> None:
        green, red = {11: 4000, 12: 6000}, {11: 9000, 12: 1000}
        self.assertEqual(signals("G", 11, 12, green, red), (4000, 6000))
        self.assertEqual(signals("R", 11, 12, green, red), (9000, 1000))
        self.assertEqual(beta(*signals("G", 11, 12, green, red)), 0.4)
        self.assertEqual(beta(*signals("R", 11, 12, green, red)), 0.9)

    def test_type_ii_uses_u_address_in_both_channels_and_ignores_m(self) -> None:
        self.assertEqual(signals("2", 999, 12, {12: 3000}, {12: 1000}), (3000, 1000))
        self.assertEqual(beta(*signals("2", None, 12, {12: 3000}, {12: 1000})), 0.75)

    def test_r_floors_and_missingness_are_explicit(self) -> None:
        for m, u, expected in [
            (0, 0, 0.5),
            (0, 1, 0.5),
            (1, 0, 0.5),
            (0, 10, 0.1),
            (10, 0, 1.0),
            (3, 1, 0.75),
        ]:
            with self.subTest(m=m, u=u):
                self.assertEqual(beta(m, u), expected)
        self.assertIsNone(beta(None, 10))
        self.assertIsNone(beta(10, None))
        self.assertEqual(signals("2", None, 99, {}, {}), (None, None))
        with self.assertRaises(ValueError):
            signals("X", 11, 12, {}, {})

    def test_idat_directory_resolves_fields_independently_of_field_order(self) -> None:
        fields = [
            (1000, struct.pack("<i", 2)),
            (104, struct.pack("<HH", 65535, 17)),
            (102, struct.pack("<II", 70001, 90002)),
        ]
        offset = 16 + 10 * len(fields)
        table = bytearray()
        for code, value in fields:
            table.extend(struct.pack("<Hq", code, offset))
            offset += len(value)
        data = b"IDAT" + struct.pack("<qi", 3, len(fields)) + table + b"".join(v for _, v in fields)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.idat"
            path.write_bytes(data)
            self.assertEqual(read_means(path), ((70001, 90002), {70001: 65535, 90002: 17}))
            path.write_bytes(data[:-1])
            with self.assertRaisesRegex(ValueError, "truncated"):
                read_means(path)
            corrupt = bytearray(data)
            struct.pack_into("<q", corrupt, 18, len(data) + 1)
            path.write_bytes(corrupt)
            with self.assertRaisesRegex(ValueError, "offset"):
                read_means(path)


if __name__ == "__main__":
    unittest.main()
