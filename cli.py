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
	t_parser.add_argument('-sender_ip', nargs=1, help='The IP address of the sender in the new transaction.', default='127.0.0.1')
	t_parser.add_argument('-sender_port', type=int, help='The port of the sender in the new transaction.')
	t_parser.add_argument('-sender_id', nargs=1, help='The ID of the sender in the new transaction.')
	t_parser.add_argument('-recip_addr', nargs=1, help='The IP address of the recipient in the new transaction.')
	t_parser.add_argument('-recip_port', nargs=1, help='The port of the recipient in the new transaction.')
	t_parser.add_argument('-recip_id', nargs=1, help='The port of the recipient in the new transaction.')
	t_parser.add_argument('-amount', nargs=1, help='The amount of NoobCash you wish to pay to the given address.')
	t_parser.set_defaults(func=transaction)
	# view
	v_parser = subparsers.add_parser('view', description='View  : View last transactions in the last validated block.')
	v_parser.set_defaults(func=view)
	# balance
	b_parser = subparsers.add_parser('balance', description='Balance : View your balance, the amount of NoobCash in your wallet.')
	b_parser.add_argument('-my_addr', help='The IP address you run your NoobCash service in', default='127.0.0.1')
	b_parser.add_argument('-my_port', type=int, help='The PORT you run your NoobCash service in', default='5000')
	b_parser.set_defaults(func=balance)
	#
	# Parse
	args = parser.parse_args()

	if not len(sys.argv) > 1:
		parser.print_help(sys.stderr)
		sys.exit(1)

	args.func(args)
