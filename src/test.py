import argparse

parent_parser = argparse.ArgumentParser(description="The parent parser")
parent_parser.add_argument("-p", type=int, required=True,
                           help="set db parameter")
subparsers = parent_parser.add_subparsers(title="actions")
parser_create = subparsers.add_parser("create", parents=[parent_parser],
                                      add_help=False,
                                      description="The create parser",
                                      help="create the orbix environment")
parser_create.add_argument("--name", help="name of the environment")
parser_update = subparsers.add_parser("update", parents=[parent_parser],
                                      add_help=False,
                                      description="The update parser",
                                      help="update the orbix environment")

parent_parser.parse_args()