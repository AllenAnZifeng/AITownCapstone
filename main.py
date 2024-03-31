import argparse
from models import Chat
from models import Benchmark

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="specify simulation case")
    parser.add_argument("sim_case", type=str, help="simulation case to run. Can be:\n   1. information_transfer\n   2. problem_solving\n    3. decision_making")
    parser.add_argument('-b', '--benchmark', type=int, nargs='?', default=None, help='Benchmark n simulations')
    parser.add_argument('-e', '--eval', action='store_true', help='Do evaluation')

    args = parser.parse_args()

    sim_case_options = ["information_transfer", "problem_solving", "decision_making"]
    if args.sim_case not in sim_case_options:
        parser.error('invalid simulation case')
    do_eval = bool(args.eval)
    do_benchmark = 0
    if args.benchmark is not None:
        do_benchmark = int(args.benchmark)

    if do_benchmark:
        bm = Benchmark(do_benchmark, args.sim_case)
        bm.run()
        bm.plot_distribution()
        bm.write_to_file()
        bm.visualizeJSON('benchmark.json')
    else:
        chat = Chat(0, str(args.sim_case))
        chat.start()
        if do_eval:
            chat.eval_agents()