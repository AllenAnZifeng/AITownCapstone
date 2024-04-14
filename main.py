import argparse
from models import Chat
from models import Benchmark

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="specify simulation case")
    parser.add_argument("sim_case", type=str, help="simulation case to run. Can be:\n   1. information_transfer\n   2. problem_solving\n   3. decision_making")
    parser.add_argument("order", type=str, help="conversation order strategy. Can be:\n   1. round_robin\n   2. moderator")
    parser.add_argument("ending", type=str, help="conversation ending strategy. Can be:\n   1. agent\n   2. moderator")
    parser.add_argument('-m', '--moderate', action='store_true', help='Add moderator to conversation')
    parser.add_argument('-e', '--eval', action='store_true', help='Do evaluation')
    parser.add_argument('-b', '--benchmark', type=int, nargs='?', default=None, help='Benchmark n simulations')

    args = parser.parse_args()

    sim_case_options = ["information_transfer", "problem_solving", "decision_making"]
    order_options = ["round_robin", "moderator"]
    ending_options = ["agent", "moderator"]
    if args.sim_case not in sim_case_options:
        parser.error("invalid simulation case")
    if args.order not in order_options:
        parser.error("invalid order strategy")
    if args.ending not in ending_options:
        parser.error("invalid ending strategy")
    do_moderate = bool(args.moderate)
    do_eval = bool(args.eval)
    do_benchmark = 0
    if args.benchmark is not None:
        do_benchmark = int(args.benchmark)

    if do_benchmark:
        bm = Benchmark(do_benchmark, str(args.sim_case), str(args.order), str(args.ending), do_moderate)
        bm.run()
        bm.plot_distribution()
        bm.write_to_file()
        bm.visualizeJSON('benchmark.json')
    else:
        chat = Chat(0, str(args.sim_case), str(args.order), str(args.ending), do_moderate)
        chat.start()
        if do_eval:
            chat.eval_agents()