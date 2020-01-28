def verboseprint(at_verbosity, *args, end='\n'):
    if 0 >= at_verbosity:
        for message in args:
            print(message, end=end)
