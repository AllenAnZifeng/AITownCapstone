import argparse
from models import Chat

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="specify simulation case")
    parser.add_argument("sim_case", type=str, help="simulation case to run. Can be:\n   1. information_transfer\n   2. problem_solving\n    3. decision_making")
    parser.add_argument('-e', '--eval', action='store_true', help='Inlcude labels')

    args = parser.parse_args()

    sim_case_options = ["information_transfer", "problem_solving", "decision_making"]
    if args.sim_case not in sim_case_options:
        parser.error('invalid simulation case')
    do_eval = bool(args.eval)

    chat = Chat(str(args.sim_case))
    chat.start()
    if do_eval:
        chat.eval_agents()