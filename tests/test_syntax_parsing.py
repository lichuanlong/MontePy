from io import StringIO
from unittest import TestCase

import mcnpy
from mcnpy.input_parser import input_syntax_reader
from mcnpy.input_parser.mcnp_input import Input, Jump, Message, ReadInput, Title
from mcnpy.input_parser.block_type import BlockType
from mcnpy.input_parser import syntax_node
from mcnpy.particle import Particle


class TestSyntaxNode(TestCase):
    def test_valuenoode_init(self):
        for type, token, answer in [
            (str, "hi", "hi"),
            (float, "1.2300", 1.23),
            (int, "1", 1),
            (float, "1.23e-3", 1.23e-3),
            (float, "6.02+23", 6.02e23),
        ]:
            for padding in [None, syntax_node.PaddingNode(" ")]:
                node = syntax_node.ValueNode(token, type, padding)
                self.assertEqual(node.value, answer)
                self.assertEqual(node.token, token)
                if padding:
                    self.assertEqual(node.padding, padding)
                else:
                    self.assertIsNone(node.padding)
        # test with None values
        for type in {str, float, int}:
            node = syntax_node.ValueNode(None, type)
            self.assertIsNone(node.value)
            node = syntax_node.ValueNode(Jump(), type)
            self.assertIsNone(node.value)

    def test_valuenode_convert_to_int(self):
        node = syntax_node.ValueNode("1", float)
        node._convert_to_int()
        self.assertEqual(node.type, int)
        self.assertEqual(node.value, 1)
        # test 1.0
        node = syntax_node.ValueNode("1.0", float)
        node._convert_to_int()
        self.assertEqual(node.type, int)
        self.assertEqual(node.value, 1)
        # test wrong type
        with self.assertRaises(ValueError):
            node = syntax_node.ValueNode("hi", str)
            node._convert_to_int()
        # test real float
        with self.assertRaises(ValueError):
            node = syntax_node.ValueNode("1.23", float)
            node._convert_to_int()

    def test_valuenode_convert_to_enum(self):
        node = syntax_node.ValueNode("1", float)
        lat = mcnpy.data_inputs.lattice.Lattice
        node._convert_to_enum(lat)
        self.assertEqual(node.type, lat)
        self.assertEqual(node.value, lat(1))
        # test with None
        with self.assertRaises(ValueError):
            node = syntax_node.ValueNode(None, float)
            node._convert_to_enum(lat)
        node._convert_to_enum(lat, allow_none=True)
        self.assertIsNone(node.value)
        st = mcnpy.surfaces.surface_type.SurfaceType
        node = syntax_node.ValueNode("p", str)
        node._convert_to_enum(st, switch_to_upper=True)
        self.assertEqual(node.type, st)
        self.assertEqual(node.value, st("P"))

    def test_is_negat_identifier(self):
        node = syntax_node.ValueNode("-1", float)
        self.assertTrue(not node.is_negatable_identifier)
        self.assertIsNone(node.is_negative)
        node.is_negatable_identifier = True
        self.assertTrue(node.is_negatable_identifier)
        self.assertEqual(node.type, int)
        self.assertTrue(node.value > 0)
        self.assertTrue(node.is_negative)
        # test with positive number
        node = syntax_node.ValueNode("1", float)
        node.is_negatable_identifier = True
        self.assertEqual(node.type, int)
        self.assertTrue(node.value > 0)
        self.assertTrue(not node.is_negative)
        # test with none
        node = syntax_node.ValueNode(None, float)
        node.is_negatable_identifier = True
        self.assertEqual(node.type, int)
        self.assertIsNone(node.value)
        self.assertIsNone(node.is_negative)
        node.value = 1
        self.assertEqual(node.value, 1)
        self.assertTrue(not node.is_negative)

    def test_is_negat_float(self):
        node = syntax_node.ValueNode("-1.23", float)
        self.assertTrue(not node.is_negatable_float)
        self.assertIsNone(node.is_negative)
        node.is_negatable_float = True
        self.assertEqual(node.type, float)
        self.assertTrue(node.value > 0)
        self.assertTrue(node.is_negative)
        self.assertTrue(node.is_negatable_float)
        # test with positive number
        node = syntax_node.ValueNode("1.23", float)
        node.is_negatable_float = True
        self.assertEqual(node.type, float)
        self.assertTrue(not node.is_negative)
        # test with None
        node = syntax_node.ValueNode(None, float)
        node.is_negatable_float = True
        self.assertEqual(node.type, float)
        self.assertIsNone(node.value)
        self.assertIsNone(node.is_negative)
        node.value = 1
        self.assertEqual(node.value, 1)
        self.assertTrue(not node.is_negative)

    def test_is_negative(self):
        node = syntax_node.ValueNode("-1.23", float)
        node.is_negatable_float = True
        self.assertTrue(node.is_negative)
        node.is_negative = False
        self.assertTrue(node.value > 0)
        self.assertTrue(not node.is_negative)
        node = syntax_node.ValueNode("hi", str)
        node.is_negative = True
        self.assertIsNone(node.is_negative)

    def test_valuenode_int_format(self):
        node = syntax_node.ValueNode("-1", int)
        answer = "-1"
        output = node.format()
        self.assertEqual(output, answer)
        for input, val, answer in [
            ("1", 5, "5"),
            ("-1", 2, " 2"),
            ("-1", -2, "-2"),
            ("+1", 5, "+5"),
            ("0001", 5, "0005"),
            (Jump(), 5, "5"),
        ]:
            node = syntax_node.ValueNode(input, int)
            node.value = val
            self.assertEqual(node.format(), answer)
            node = syntax_node.ValueNode(input, int)
            node.is_negatable_identifier = True
            node.value = val
            node.is_negative = val < 0
            self.assertEqual(node.format(), answer)
        # test messing around with padding
        for padding, val, answer in [
            ([" "], 10, "10 "),
            (["  "], 10, "10 "),
            (["\n"], 10, "10\n"),
            ([" ", "\n", "c hi"], 10, "10\nc hi"),
            ([" ", " "], 10, "10 "),
        ]:
            pad_node = syntax_node.PaddingNode(padding[0])
            for pad in padding[1:]:
                pad_node.append(pad)
            node = syntax_node.ValueNode("1", int, pad_node)
            node.value = val
            self.assertEqual(node.format(), answer)

    def test_value_has_changed(self):
        # test None no change
        node = syntax_node.ValueNode(None, int)
        self.assertTrue(not node._value_changed)
        # test None changed
        node.value = 5
        self.assertTrue(node._value_changed)
        node = syntax_node.ValueNode("1.23", float)
        self.assertTrue(not node._value_changed)
        node.value = 1.25
        self.assertTrue(node._value_changed)
        node = syntax_node.ValueNode("hi", str)
        self.assertTrue(not node._value_changed)
        node.value = "foo"
        self.assertTrue(node._value_changed)


class TestSyntaxParsing(TestCase):
    def testCardInit(self):
        with self.assertRaises(TypeError):
            Input("5", BlockType.CELL)
        with self.assertRaises(TypeError):
            Input([5], BlockType.CELL)
        with self.assertRaises(TypeError):
            Input(["5"], "5")

    def testMessageInit(self):
        with self.assertRaises(TypeError):
            Message(["hi"], "5")
        with self.assertRaises(TypeError):
            Message(["hi"], [5])

    def testTitleInit(self):
        with self.assertRaises(TypeError):
            Title(["hi"], 5)

    def testMessageFinder(self):
        test_message = "this is a message"
        test_string = f"""message: {test_message}

test title
"""
        for tester, validator in [
            (test_string, test_message),
            (test_string.upper(), test_message.upper()),
        ]:
            with StringIO(tester) as fh:
                generator = input_syntax_reader.read_front_matters(fh, (6, 2, 0))
                card = next(generator)
                self.assertIsInstance(card, mcnpy.input_parser.mcnp_input.Message)
                self.assertEqual(card.lines[0], validator)
                self.assertEqual(len(card.lines), 1)

    def testReadCardStr(self):
        card = ReadInput(["Read file=hi.imcnp"], BlockType.CELL)
        self.assertEqual(str(card), "READ INPUT: Block_Type: BlockType.CELL")
        self.assertEqual(
            repr(card),
            "READ INPUT: BlockType.CELL: ['Read file=hi.imcnp'] File: hi.imcnp",
        )

    def testTitleFinder(self):
        test_title = "Richard Stallman writes GNU"
        test_string = f"""{test_title}
1 0 -1
"""
        for tester, validator in [
            (test_string, test_title),
            (test_string.upper(), test_title.upper()),
        ]:
            with StringIO(tester) as fh:
                generator = input_syntax_reader.read_front_matters(fh, (6, 2, 0))
                card = next(generator)
                self.assertIsInstance(card, mcnpy.input_parser.mcnp_input.Title)
                self.assertEqual(card.title, validator)

    def testCardFinder(self):
        test_string = """1 0 -1
     5"""
        for i in range(5):
            tester = " " * i + test_string
            with StringIO(tester) as fh:
                generator = input_syntax_reader.read_data(fh, (6, 2, 0))
                card = next(generator)
                self.assertIsInstance(card, mcnpy.input_parser.mcnp_input.Input)
                answer = [" " * i + "1 0 -1", "     5"]
                self.assertEqual(len(answer), len(card.input_lines))
                for j, line in enumerate(card.input_lines):
                    self.assertEqual(line, answer[j])
                self.assertEqual(
                    card.block_type, mcnpy.input_parser.block_type.BlockType.CELL
                )

    # TODO ensure this is tested in Input parsers
    """
    def testCommentFinder(self):
        for i in range(5):
            tester = " " * i + test_string
            with StringIO(tester) as fh:
                card = next(input_syntax_reader.read_data(fh, (6, 2, 0)))
                self.assertIsInstance(card, mcnpy.input_parser.mcnp_input.Comment)
                self.assertEqual(len(card.lines), 5)
                self.assertEqual(card.lines[0], "foo")
                self.assertEqual(card.lines[1], "bar")
                self.assertEqual(card.lines[3], "bop")
    """

    def testReadCardFinder(self):
        test_string = "read file=foo.imcnp "
        with StringIO(test_string) as fh:
            card = next(input_syntax_reader.read_data(fh, (6, 2, 0)))
            self.assertIsNone(card)  # the read input is hidden from the user

    def testBlockId(self):
        test_string = "1 0 -1"
        for i in range(3):
            tester = "\n" * i + test_string
            with StringIO(tester) as fh:
                for card in input_syntax_reader.read_data(fh, (6, 2, 0)):
                    pass
                self.assertEqual(
                    mcnpy.input_parser.block_type.BlockType(i), card.block_type
                )

    def testCommentFormatInput(self):
        in_strs = ["c foo", "c bar"]
        card = mcnpy.input_parser.syntax_node.CommentNode(in_strs[0])
        output = card.format()
        answer = "c foo"
        str_answer = """COMMENT:
c foo"""
        self.assertEqual(repr(card), str_answer)
        self.assertEqual("c foo", str(card))
        self.assertEqual(len(answer), len(output))
        for i, line in enumerate(output):
            self.assertEqual(answer[i], line)

    def testMessageFormatInput(self):
        answer = ["MESSAGE: foo", "bar", ""]
        card = mcnpy.input_parser.mcnp_input.Message(answer, ["foo", "bar"])
        str_answer = """MESSAGE:
foo
bar
"""
        self.assertEqual(str_answer, repr(card))
        self.assertEqual("MESSAGE: 2 lines", str(card))
        output = card.format_for_mcnp_input((6, 2, 0))
        self.assertEqual(len(answer), len(output))
        for i, line in enumerate(output):
            self.assertEqual(answer[i], line)

    def testTitleFormatInput(self):
        card = mcnpy.input_parser.mcnp_input.Title(["foo"], "foo")
        answer = ["foo"]
        str_answer = "TITLE: foo"
        self.assertEqual(str(card), str_answer)
        output = card.format_for_mcnp_input((6, 2, 0))
        self.assertEqual(len(answer), len(output))
        for i, line in enumerate(output):
            self.assertEqual(answer[i], line)

    def testReadInput(self):
        # TODO ensure comments are properly glued to right input
        generator = input_syntax_reader.read_input_syntax("tests/inputs/test.imcnp")
        mcnp_in = mcnpy.input_parser.mcnp_input
        input_order = [mcnp_in.Message, mcnp_in.Title]
        input_order += [mcnp_in.Input] * 17
        for i, input in enumerate(generator):
            print(input.input_lines)
            print(input_order[i])
            self.assertIsInstance(input, input_order[i])

    def testReadInputWithRead(self):
        generator = input_syntax_reader.read_input_syntax("tests/inputs/testRead.imcnp")
        next(generator)  # skip title
        next(generator)  # skip read none
        card = next(generator)
        answer = ["1 0 -1"]
        self.assertEqual(answer, card.input_lines)

    def testReadInputWithVertMode(self):
        generator = input_syntax_reader.read_input_syntax(
            "tests/inputs/testVerticalMode.imcnp"
        )
        next(generator)
        next(generator)
        with self.assertRaises(mcnpy.errors.UnsupportedFeature):
            next(generator)

    def testCardStringRepr(self):
        in_str = "1 0 -1"
        card = mcnpy.input_parser.mcnp_input.Input(
            [in_str], mcnpy.input_parser.block_type.BlockType.CELL
        )
        self.assertEqual(str(card), "INPUT: BlockType.CELL")
        self.assertEqual(repr(card), "INPUT: BlockType.CELL: ['1 0 -1']")

    def testShortcutExpansion(self):
        tests = {
            ("M", "1", "3M", "2r"): ["M", "1", "3", "3", "3"],
            ("M", "0.01", "2ILOG", "10"): ["M", "0.01", "0.1", "1", "10"],
            ("M", "1", "3M", "I", "4"): ["M", "1", "3", "3.5", "4"],
            ("M", "1", "3M", "3M"): ["M", "1", "3", "9"],
            ("M", "1", "2R", "2I", "2.5"): ["M", "1", "1", "1", "1.5", "2", "2.5"],
            ("M", "1", "R", "2m"): ["M", "1", "1", "2"],
            ("M", "1", "R", "R"): ["M", "1", "1", "1"],
            ("M", "1", "2i", "4", "3m"): ["M", "1", "2", "3", "4", "12"],
            ("M", "1", "i", "3"): ["M", "1", "2", "3"],
            ("M", "1", "ilog", "100"): ["M", "1", "10", "100"],
            ("M", "1", "2i", "4", "2i", "10"): [
                "M",
                "1",
                "2",
                "3",
                "4",
                "6",
                "8",
                "10",
            ],
            (
                "M",
                "1",
                "2j",
                "4",
            ): ["M", "1", mcnpy.Jump(), mcnpy.Jump(), "4"],
        }
        invalid = [
            ("M", "3J", "4R"),
            ("M", "1", "4I", "3M"),
            ("M", "1", "4I", "J"),
            ("M", "1", "2Ilog", "J"),
            ("M", "3J", "2M"),
            ("M", "10", "M"),
            (
                "M5",
                "2R",
            ),
        ]

        parser = mcnpy.input_parser.mcnp_input.parse_input_shortcuts
        for test, answer in tests.items():
            print(test)
            parsed = parser(list(test))
            self.assertEqual(parsed, answer)
        for test in invalid:
            print(test)
            with self.assertRaises(mcnpy.errors.MalformedInputError):
                parser(list(test))

    def testDataInputNameParsing(self):
        tests = {
            "kcOde": {"prefix": "kcode", "number": None, "classifier": None},
            "M300": {"prefix": "m", "number": 300, "classifier": None},
            "IMP:N,P,E": {
                "prefix": "imp",
                "number": None,
                "classifier": [Particle.NEUTRON, Particle.PHOTON, Particle.ELECTRON],
            },
            "F1004:n,P": {
                "prefix": "f",
                "number": 1004,
                "classifier": [Particle.NEUTRON, Particle.PHOTON],
            },
        }
        for in_str, answer in tests.items():
            # Testing parsing the names
            card = mcnpy.input_parser.mcnp_input.Input(
                [in_str], mcnpy.input_parser.block_type.BlockType.DATA
            )
            data_input = mcnpy.data_inputs.data_input.DataInput(card, fast_parse=True)
            self.assertEqual(data_input.prefix, answer["prefix"])
            if answer["number"]:
                self.assertEqual(data_input._input_number.value, answer["number"])
            if answer["classifier"]:
                self.assertEqual(
                    sorted(data_input.particle_classifiers),
                    sorted(answer["classifier"]),
                )

    def testDataInputNameEnforcement(self):
        tests = {
            "kcOde5": {"prefix": "kcode", "number": False, "classifier": 0},
            "M-300": {"prefix": "m", "number": True, "classifier": 0},
            "M": {"prefix": "m", "number": True, "classifier": 0},
            "f4m": {"prefix": "fm", "number": True, "classifier": 1},
            "IMP:N,P,E": {"prefix": "imp", "number": False, "classifier": 0},
            "IMP": {"prefix": "imp", "number": False, "classifier": 2},
        }
        valid = {
            "IMP:N,P,E": {"prefix": "imp", "number": False, "classifier": 2},
            "F1004:n,P": {"prefix": "f", "number": True, "classifier": 1},
        }
        # tests invalid names
        for in_str, answer in tests.items():
            with self.assertRaises(mcnpy.errors.MalformedInputError):
                card = mcnpy.input_parser.mcnp_input.Input(
                    [in_str], mcnpy.input_parser.block_type.BlockType.DATA
                )
                Fixture = DataInputTestFixture
                Fixture._class_prefix1 = answer["prefix"]
                Fixture._has_number1 = answer["number"]
                Fixture._has_classifier1 = answer["classifier"]
                card = Fixture(card)

        # tests valid names
        for in_str, answer in valid.items():
            card = mcnpy.input_parser.mcnp_input.Input(
                [in_str], mcnpy.input_parser.block_type.BlockType.DATA
            )
            print(card.input_lines)
            print(
                "Prefix",
                answer["prefix"],
                "number",
                answer["number"],
                "classifier",
                answer["classifier"],
            )
            Fixture = DataInputTestFixture
            Fixture._class_prefix1 = answer["prefix"]
            Fixture._has_number1 = answer["number"]
            Fixture._has_classifier1 = answer["classifier"]
            card = Fixture(card)

    def test_get_line_numbers(self):
        answers = {
            (5, 1, 60): 80,
            (6, 1, 0): 80,
            (6, 2, 0): 128,
            (6, 2, 3): 128,
            (6, 3, 0): 128,
            (7, 4, 0): 128,
        }
        for version, answer in answers.items():
            self.assertEqual(answer, mcnpy.constants.get_max_line_length(version))
        with self.assertRaises(mcnpy.errors.UnsupportedFeature):
            mcnpy.constants.get_max_line_length((5, 1, 38))

    def test_jump(self):
        jump = Jump()
        self.assertEqual("J", str(jump))
        jump2 = Jump()
        self.assertEqual(jump, jump2)
        with self.assertRaises(TypeError):
            bool(jump)

    def test_jump_and_a_hop(self):
        jump = Jump()
        # first you need to hop
        self.assertEqual("j", jump.lower())
        # then you need to skip
        self.assertEqual("Jump", jump.title())
        # before you can jump
        self.assertEqual("J", jump.upper())


class DataInputTestFixture(mcnpy.data_inputs.data_input.DataInputAbstract):
    _class_prefix1 = None
    _has_number1 = None
    _has_classifier1 = None

    def __init__(self, input_card=None):
        """
        :param input_card: the Card object representing this data input
        :type input_card: Input
        """
        super().__init__(input_card, fast_parse=True)

    def _class_prefix(self):
        return self._class_prefix1

    def _has_number(self):
        return self._has_number1

    def _has_classifier(self):
        return self._has_classifier1
