#!venv/bin/python
from reddstackrest import core, config
import argparse
import sys
import os
import subprocess
import time
import signal

rest_server = None  # server subprocess handle

def die_handler_server(signal, frame):
    """
    Handle Ctrl+C for server subprocess
    """

    stop_server(True)
    sys.exit(0)

def start_server(foreground = False):
    global rest_server

    port = config.port
    access_logfile = config.get_working_dir() + '/access.log'
    server_logfile = config.get_working_dir() + '/server.log'
    module = "reddstackrest.core.resource"
    pid_file = get_pidfile_path()

    if not foreground:
        start_cmd = ('twistd -no --pidfile= web --class={0} --logfile {1} -p {2}'.format(module, access_logfile, port)).split()

        try:
            if os.path.exists(server_logfile):
                logfile = open(server_logfile, "a")
            else:
                logfile = open(server_logfile, "a+")
        except OSError, oe:
            print("Failed to open '%s': %s" % (server_logfile, oe.strerror))
            sys.exit(1)

        # become a daemon
        child_pid = os.fork()
        if child_pid == 0:

            # child! detach, setsid, and make a new child to be adopted by init
            sys.stdin.close()
            os.dup2(logfile.fileno(), sys.stdout.fileno())
            os.dup2(logfile.fileno(), sys.stderr.fileno())
            os.setsid()

            daemon_pid = os.fork()
            if daemon_pid == 0:

                # daemon!
                os.chdir("/")

            elif daemon_pid > 0:

                # parent (intermediate child)
                sys.exit(0)

            else:

                # error
                sys.exit(1)

        elif child_pid > 0:

            # grand-parent
            # wait for intermediate child
            pid, status = os.waitpid(child_pid, 0)
            sys.exit(status)
    else:
        # foreground
        start_cmd = ('twistd -no --pidfile= web --class={0} -p {2}'.format(module, access_logfile, port)).split()

    # correctly die on fatal signals
    for sig in [signal.SIGINT, signal.SIGQUIT, signal.SIGTERM]:
        signal.signal( sig, die_handler_server )

    # start REST server
    print("\n\n\n### Starting server ###\n\n")
    #put_pidfile(pid_file, os.getpid())
    rest_server = subprocess.Popen(start_cmd, shell=False)
    put_pidfile(pid_file, rest_server.pid)

    # wait for the REST server to die
    rest_server.wait()

    return rest_server.returncode


def get_pidfile_path():
    working_dir = config.get_working_dir()
    pid_filename = config.get_pid_filename() + ".pid"
    return os.path.join(working_dir, pid_filename)


def get_pid_from_pidfile(pidfile_path):

    with open(pidfile_path, "r") as f:
        txt = f.read()

    try:
        pid = int(txt.strip())
    except:
        raise Exception("Invalid PID '%s'" % pid)

    return pid


def put_pidfile(pidfile_path, pid):

    with open(pidfile_path, "w") as f:
        f.write("%s" % pid)

    return


def stop_server(from_signal):
    global rest_server

    pid_file = get_pidfile_path()

    if from_signal:
        print('Caught fatal signal; exiting reststack-rest server')
        time.sleep(3.0)
        if rest_server is not None:
            print('Stopping Rest Server')
            rest_server.send_signal(signal.SIGTERM)
            rest_server.wait()
            print('Stopped Rest Server')

    else:
        try:
            fin = open(pid_file, "r")
        except Exception, e:
            pass

        else:
            pid_data = fin.read().strip()
            fin.close()

            pid = int(pid_data)

            try:
                os.kill(pid, signal.SIGTERM)
            except Exception, e:
                pass

            # takes at most 3 seconds
            time.sleep(3.0)

    print("Reddstack-rest server stopped")


def run_reddstackrestd():
    """
    Run the Reddstack Rest server
    """

    argparser = argparse.ArgumentParser()
    subparsers = argparser.add_subparsers(dest='action', help='the action to be taken')

    parser = subparsers.add_parser('start', help='start the REST server')
    parser.add_argument('--foreground', action='store_true', help='start the server in the foreground')
    parser = subparsers.add_parser('stop', help='stop the REST server')
    parser = subparsers.add_parser('version', help='Print version and exit')
    args, _ = argparser.parse_known_args()

    if args.action == 'version':
        print config.VERSION
        sys.exit(0)

    if args.action == 'start':
        if args.foreground:
            print ("starting server in the foreground...")
            exit_status = start_server(foreground=True)
            print (exit_status)
            # while(1):
            #     stay_alive = True

        else:
            print ("starting server")
            start_server()

    if args.action == 'stop':
        print ("stopping server")
        stop_server(False)
