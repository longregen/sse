import os

def display_help():
    help_text = """
    semsearch-edge: semantic search on the edge (alias sse)

    sse crawl <project> <dir> [--include pattern] [--exclude pattern]
        - Crawls the given project directory, including or excluding files that match certain patterns.

    sse query <project> <query> [--limit number]
        - Runs a query on a specific project.

    sse help
        - Displays this help message.
    """
    print(help_text)

def cli_main(settings, args):
    if "project" not in settings:
        settings["project"] = {}
    if "query" not in settings:
        settings["query"] = {}
    from .db import get_conn
    db_conn = get_conn(settings)

    # Run the appropriate function based on the provided command
    if args.command == 'crawl':
        settings["project"]["name"] = args.project
        if args.include:
            for x in args.include:
                settings["crawl"]["include"].append(x)
        if args.exclude:
            for x in args.exclude:
                settings["crawl"]["exclude"].append(x)
        from .crawl import crawl
        crawl(settings, db_conn, args.dir)

    elif args.command == 'query':
        settings["project"]["name"] = args.project
        settings["query"]["limit"] = args.limit
        from .query import query
        res = query(settings, db_conn, args.query)
        common_path = os.path.commonprefix([x[1] for x in res])
        for f in res:
            print(f'    {f[1].replace(common_path, "")} [score {f[8]:.5}]')

    elif args.command == 'server':
        from .server import run_server
        run_server(args.host, args.port)

    elif args.command == 'help':
        display_help()
