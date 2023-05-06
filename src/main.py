import argparse
import json

from fuzzer.fuzzer import Fuzzer

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fuzzer for JPacman')
    parser.add_argument('--config', type=str, help='Config file path', default="data/config/config.json")
    parser.add_argument('--max_iterations', type=int, help='Max number of iterations')
    parser.add_argument('--max_time', type=int, help='Max time in seconds')
    parser.add_argument('--generate_report', type=bool, help='Generate report', default=True)
    args = parser.parse_args()

    config = json.load(open(args.config))

    fuzzer = Fuzzer(config=config, max_iterations=args.max_iterations, max_time=args.max_time)

    fuzzer.run(report=args.generate_report)
