import argparse
import sys
from cli_functions import *
"""
Command line inteface
t <recipient_address> <amount> : sends a certain amount of noobcash to the given address
view						   : show last verified block of transactions
balance     				   : show the balance of the user's wallet
help
"""
if __name__ == '__main__':
	parser = argparse.ArgumentParser(prog='cli.py', conflict_handler='resolve', description='NoobCash Wallet CLI:Command Line inteface for the owner of a NoobCash wallet.')
	subparsers = parser.add_subparsers(dest='scope')
	# transaction
	t_parser = subparsers.add_parser('t', description='t : Send NoobCash. New transaction between current user and a given IP address.')
	t_parser.add_argument('-sender_addr', nargs=1, help='The IP address of the sender in the new transaction.')
	t_parser.add_argument('-recip_addr', nargs=1, help='The IP address of the recipient in the new transaction.')
	t_parser.add_argument('-amount', nargs=1, help='The amount of NoobCash you wish to pay to the given address.')
	t_parser.set_defaults(func=transaction)
	# view
	v_parser = subparsers.add_parser('view', description='View  : View last transactions in the last validated block.')
	v_parser.set_defaults(func=view)
	# balance
	b_parser = subparsers.add_parser('balance', description='Balance : View your balance, the amount of NoobCash in your wallet.')
	b_parser.set_defaults(func=balance)
	#
	# Parse
	args = parser.parse_args()

	if not len(sys.argv) > 1:
		parser.print_help(sys.stderr)
		sys.exit(1)

	args.func(args)
