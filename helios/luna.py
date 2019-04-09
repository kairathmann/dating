# -*- coding: utf-8 -*-

from __future__ import division

# This script *must* be located in the application root because Django is based on relative
# filepaths and can't handle things being called from other folders

import os, signal, sys, json, time, timeit, subprocess, settings

from django.conf import settings
from setproctitle import setproctitle
from supervisor.supervisord import main

from plant_hermes.hsm.keyring import HSMkeyring

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")


def start():
    """
        Starts the LUNA services supervisor
    """

    for line in os.popen("ps xa"):

        fields = line.split()
        process = ' '.join(fields[4:])

        if process.find('LUNA - SUPERVISOR') != -1:
            print "\nLUNA is already running\n"
            return

    print " "
    print "██╗      ██╗   ██╗ ███╗   ██╗  █████╗ "
    print "██║      ██║   ██║ ████╗  ██║ ██╔══██╗"
    print "██║      ██║   ██║ ██╔██╗ ██║ ███████║"
    print "██║      ██║   ██║ ██║╚██╗██║ ██╔══██║"
    print "███████╗ ╚██████╔╝ ██║ ╚████║ ██║  ██║"
    print "╚══════╝  ╚═════╝  ╚═╝  ╚═══╝ ╚═╝  ╚═╝"
    print "═════════════════════════════════════════════════════════════════════════════"

    if True or settings.RUNNING_ON_PROD:

        print ""
        print "WARNING: LUNA THINKS THIS IS A PRODUCTION SERVER"
        print ""
        print "Starting LUNA in production mode will arm the EOS (email) and HERMES (blockchain)"
        print "services, causing emails to be sent to real users and tokens transferred between"
        print "wallets. Enter the launch key, or hit enter to abort."
        print ""

        # sys.stdout.write("LAUNCH KEY: ")
        #
        # choice = raw_input()
        #
        # keyring = HSMkeyring(master_key=choice)
        #
        # settings.keyring = keyring
        # settings.DATABASES = keyring.get_key('DATABASES')
        #
        # os.environ["MASTERKEY"] = choice

        print "\nEMERGENCY SHUTDOWN: 'service luna scram'"
        print "NORMAL SHUTDOWN: 'service luna stop'\n"
        print "[PLANT UP] LUNA is operating in PRODUCTION MODE\n\n"

        setproctitle("LUNA - SUPERVISOR [ARMED]")

        # Pass the supervisord arguments through to simulate calling it from terminal. This bypasses
        # the bash log, preventing the launch key from being saved

        main(args=['-c', '/srv/luna/config/supervisord.conf'])


    else:

        print ""
        print "LUNA THINKS THIS IS A DEVELOPMENT SERVER"
        print ""
        print "When running on a development server, LUNA runs the EOS (email) and HERMES (blockchain)"
        print "services in SAFE mode. As a result, EOS will only send emails to whitelisted addresses,"
        print "and HERMES will not post transactions to the blockchain."
        print ""
        print "EMERGENCY SHUTDOWN: 'service luna scram'"
        print "NORMAL SHUTDOWN: 'service luna stop'\n"

        setproctitle("LUNA - SUPERVISOR [SAFE]")

        print "[PLANT UP] LUNA is operating in SAFE MODE\n\n"

        # Pass the supervisord arguments through to simulate calling it from terminal
        main(args=['-c', '/srv/luna/config/supervisord.conf'])


def stop():
    """
        Shuts down the LUNA plant and all of its workers in an orderly manner

        :return: True on successful stop. Otherwise False.
    """

    process_killed = False

    for line in os.popen("ps xa"):

        fields = line.split()

        pid = fields[0]
        process = ' '.join(fields[4:])

        if process.find('LUNA - SUPERVISOR') != -1:
            os.kill(int(pid), signal.SIGKILL)

            process_killed = True
            break

    if not process_killed:

        print "\nLUNA supervisor is not running\n"
        return True

    else:

        print "\n[SHUTTING DOWN] Performing plant shutdown. May take up to 30 seconds."

        time.sleep(10)

        for line in os.popen("ps xa"):

            fields = line.split()
            process = ' '.join(fields[4:])

            if process.find('LUNA - SUPERVISOR') != -1:
                print "\nWARNING: one or more workers failed to shut down. Use 'service luna scram' to terminate them\n"
                return False

    print "[PLANT DOWN] LUNA was successfully stopped\n"
    return True


def scram():
    """
        Instantly shuts down the LUNA plant by terminating all related processes
    """

    print ""
    print "WARNING: SCRAMMING LUNA WILL INSTANTLY STOP ALL SERVICES."
    print "THIS MAY RESULT IN LOST OR DUPLICATE EMAILS; AND MISSING OR DUPLICATE BLOCKCHAIN TRANSACTIONS."
    print ""

    sys.stdout.write("Do you want to SCRAM Luna [y/N]? ")  # N is deliberately capitalized to indicate default
    # of 'No' as per Linux UI standards

    choice = raw_input().lower()

    if choice == 'y':

        subprocess.call(["pkill", "-f", "gunicorn"])
        subprocess.call(["pkill", "-f", "qtumd"])

        print "\n[PLANT DOWN] Luna was successfully scrammed\n\n"

    else:
        print "Aborted. LUNA is still running.\n"


def restart():
    """
        Restarts the LUNA plant
    """

    if stop():
        start()


def map_command(command):
    if command == 'start':
        start()

    elif command == 'stop':
        stop()

    elif command == 'scram':
        scram()

    elif command == 'restart':
        restart()

    else:
        print "Invalid command\n"


def print_purple(prt): print("\033[95m {}\033[00m".format(prt))


def print_light_purple(prt): print("\033[94m {}\033[00m".format(prt))


def print_spaceship(): print("\xF0\x9F\x9A\x80")


def print_help():
    print_spaceship()

    print_purple('Luna can be used with the following args:')
    print_light_purple('python luna.py start')
    print_light_purple('python luna.py stop')
    print_light_purple('python luna.py scram')
    print_light_purple('python luna.py restart')


if (len(sys.argv) < 2):
    print_help()
else:
    map_command(sys.argv[1])
