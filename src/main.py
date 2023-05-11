import argparse
import json

from fuzzer.fuzzer import Fuzzer

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fuzzer for JPacman')
    parser.add_argument('--config', type=str, help='Config file path', default="data/config/config.json")
    parser.add_argument('--max_iterations', type=int, help='Max number of iterations')
    parser.add_argument('--max_time', type=int, help='Max time in seconds')
    parser.add_argument('--generate_report', type=bool, help='Generate report', default=True)
    parser.add_argument('--initial_map_path', type=str, help='Initial map path for a mutation run')
    parser.add_argument('--initial_action_sequence', type=str, help='Initial action sequence for a mutation run')
    parser.add_argument('--mutate_run', type=bool, help='Mutation run', default=False)
    parser.add_argument('--progress_bar', type=bool, help='Whether a progress bar should be displayed', default=True)
    parser.add_argument('--partial_reports', type=bool,
                        help='Generate partial reports during a run, every update interval', default=False)
    parser.add_argument('--partial_report_interval', type=int, help='Partial report interval', default=20)
    args = parser.parse_args()

    config = json.load(open(args.config))

    fuzzer = Fuzzer(config=config, max_iterations=args.max_iterations, max_time=args.max_time)

    if args.mutate_run:
        if not args.initial_map_path or not args.initial_action_sequence:
            raise Exception("Initial map path and initial action sequence must be provided for a mutation run")

        initial_map_string = open(args.initial_map_path).read()

        fuzzer.mutate_run(initial_map_string=initial_map_string, initial_action_sequence=args.initial_action_sequence,
                          generate_report=args.generate_report, partial_report_interval=args.partial_report_interval,
                          partial_reports=args.partial_reports, progress_bar=args.progress_bar)
    else:
        fuzzer.run(generate_report=args.generate_report, partial_report_interval=args.partial_report_interval,
                   partial_reports=args.partial_reports, progress_bar=args.progress_bar)
