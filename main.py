import argparse
import sys
import os
import time

from sse.load_settings import load_settings
from sse.cli import display_help, cli_main
from sse.http_client import http_main, http_health

def main():
    settings = load_settings()

    # Create a top-level parser
    parser = argparse.ArgumentParser(prog='sse')
    subparsers = parser.add_subparsers(title='commands', dest='command')

    # Create a parser for the "crawl" command
    crawl_parser = subparsers.add_parser('crawl', help='crawl a project directory')
    crawl_parser.add_argument('project', help='name of the project to crawl')
    crawl_parser.add_argument('dir', help='directory of the project to crawl')
    crawl_parser.add_argument('--include', dest='include', help='file pattern to include in the crawl', action='append')
    crawl_parser.add_argument('--exclude', dest='exclude', help='file pattern to exclude from the crawl', action='append')

    # Create a parser for the "query" command
    query_parser = subparsers.add_parser('query', help='query a project')
    query_parser.add_argument('project', help='name of the project to query')
    query_parser.add_argument('query', help='query to perform on the project')
    query_parser.add_argument('--limit', '-l', dest='limit', help='limit number of results to show', default=5)

    server_parser = subparsers.add_parser('server', help='run a sse server')
    server_parser.add_argument('--port', dest='port', help='port to listen to', default=settings["server"]["port"])
    server_parser.add_argument('--host', dest='host', help='host to listen in', default=settings["server"]["host"])

    # Create a parser for the "help" command
    subparsers.add_parser('help', help='display a help message')

    args = parser.parse_args()
    # Parse the arguments. Easy debug with:
    # print(json.dumps(args, indent=2, sort_keys=True, default=str))

    # Check if no command is provided
    if args.command is None:
        print('No command provided. Please provide a command.', file=sys.stderr)
        display_help()
        sys.exit(1)

    target = f'{args.host if "host" in args else settings["server"]["host"]}:{args.port if "port" in args else settings["server"]["port"]}'

    # If daemonize mode is enabled, try to start the server
    if settings.get("server", {}).get("daemonize") == "start":
        # Check if server is running
        if not http_health(target):
            print("Server is not running. Starting it now...")
            pid = os.fork()
            if pid > 0:
                from sse.server import run_server
                run_server(args.host, args.port)
                return
            else:
                time.sleep(5)  # Give server time to start
        # Use the HTTP client code here
        return http_main(target, settings, args)
    else:
        return cli_main(settings, args)

if __name__ == '__main__':
    main()

