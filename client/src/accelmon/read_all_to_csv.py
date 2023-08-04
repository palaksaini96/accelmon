import sys
sys.path.append('../src/accelmon')

import datetime
import logging
import threading
import time
import argparse
import board
from sinks import CsvSampleSink


ports = ["COM8","COM31"]
boards = []
sinks = []
threads = []


if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    
    parser = argparse.ArgumentParser(description='Read SAMD21 ADC over serial')
    parser.add_argument('-m','--max-count', type=int, default=0,  
            help='Maximum number of samples to record. Default 0 (no maximum)')
    parser.add_argument('-t','--timeout', type=int, default=0,  
            help='Collection time for sampling (s). Default is 0 (no timeout)')
#     parser.add_argument('-p', '--port', default='/dev/ttyACM0',  
#             help='Serial port name. Default is /dev/ttyACM0.')
#     parser.add_argument('filename', help='CSV file for data output')
    args = parser.parse_args()

    logging.info("Starting demo")
    logging.info(args)

#     logging.info("Creating sink {}".format(args.filename))
#     csv = CsvSampleSink(args.filename)
#     csv.open()
    
    
    for item in range(len(ports)):

            sinks.append(CsvSampleSink("{}-{}.csv".format(ports[item], datetime.datetime.now().strftime("%Y%m%d"))))
            sinks[item].open()
            boards.append(board.Controller(port=ports[item], sinks=[sinks[item]]))
            threads.append(threading.Thread(target = boards[item].collect_samples, args=(args.max_count,)))

#     mon = board.Controller(port=args.port, sinks=[csv])
#     logging.info("Board ID: {}".format(mon.board_id()))

#     logging.info("Main: creating thread")
#     x = threading.Thread(target=mon.collect_samples, args=(args.max_count,))
#     logging.info("Main: starting thread")
#     x.start()


    def allStopCollection():
            # map(methodcaller('stop_collection'), boards)
            # map(lambda thread: thread.stop_collection, threads)
            for board in boards:
                    board.stop_collection()
            return

    for item in threads:
            item.start()

    t = threading.Timer(args.timeout, allStopCollection)
    if args.timeout > 0:
        t.start()

    heartbeat = 0

    def allAlive():
        for thread in threads:
                if not thread.is_alive():
                        return False 
        return True
    
    while allAlive():
            heartbeat += 1
            logging.info("..{}".format(heartbeat))
            time.sleep(1.)

    # here either the timer expired and called halt or we processed 
    # max_steps messages and exited
    logging.info("Main: cancel timer")
    t.cancel()
    logging.info("Main: calling join")
    for thread in threads:
            thread.join()
    logging.info("Main: closing sink")
    for sink in sinks:
        sink.close()
    logging.info("Main: done")





