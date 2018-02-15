import shlex
import subprocess
import time
from helpers.AsynchronousFileReaderHelper import AsynchronousFileReader
from multiprocessing import Queue


class CommandExecutionHelper:

    def __init__(self, state=None):
        self.state = state


    def consume(self, command):
        '''
        Consume standard output and standard error of a
        subprocess asynchronously without risk on deadlocking.
        '''

        args = shlex.split(command)
        # Launch the command as subprocess.
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Launch the asynchronous readers of the process' stdout and stderr.
        stdout_queue = Queue()
        stdout_reader = AsynchronousFileReader(process.stdout, stdout_queue)
        stdout_reader.start()
        stderr_queue = Queue()
        stderr_reader = AsynchronousFileReader(process.stderr, stderr_queue)
        stderr_reader.start()

        events = []

        # Check the queues if we received some output (until there is nothing more to get).
        while not stdout_reader.eof() or not stderr_reader.eof():
            # Show what we received from standard output.
            while not stdout_queue.empty():
                line = stdout_queue.get()
                if line.find('aaaa'):
                    print(line)
                    # return line
                # output =  output_management(line)
                # if output is not None:
                #     events.append(output_management(line))
                # print 'Received line on standard output: ' + repr(line)
                # json_line = json.loads(line)
                # for key in json_line:
                #     if key == "event":
                #         events.append(json_line)
            # Show what we received from standard error.
            while not stderr_queue.empty():
                line = stderr_queue.get()
                print('Received line on standard error: ' + repr(line))

            # Sleep a bit before asking the readers again.
            time.sleep(.1)

        # Let's be tidy and join the threads we've started.
        stdout_reader.join()
        stderr_reader.join()

        # Close subprocess' file descriptors.
        process.stdout.close()
        process.stderr.close()

        return events

    def execute(self, command):

        task = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        data = task.stdout.read()
        # assert task.wait() == 0
        return data
