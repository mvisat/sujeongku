#!/usr/bin/python3

import argparse

from server import listener

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int, help="port to bind")
    args = parser.parse_args()

    listener.listener(port=args.port).serve_forever()

