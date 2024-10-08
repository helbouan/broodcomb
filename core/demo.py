from topo import SimpleTopo
from infra import Infrastructure
from mapper import Mapper
from net import Network
from time import sleep
import argparse
from threading import Event
import signal 

SSH_KEY = '/home/helbouan/.ssh/id_rsa'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Workers' ip addresses")
    parser.add_argument("--workers", type=str, required=True, 
                        help="A comma-separated list of IP addresses. Example: --ip_addresses=10.0.0.1,10.0.0.2")
    args = parser.parse_args()
    workers = args.workers.split(",")

    topo = SimpleTopo()
    infra = Infrastructure()
    for worker in workers:
        infra.add_worker(worker, key=SSH_KEY)
    mapper = Mapper(infra, topo)
    net = Network(mapper)

    def handle_interrupt(sig, frame):
        net.stop()
        net.clean()
        infra.shutdown()

    try:
        net.start()

        # n = 1
        print("Start")
        print(mapper)


        signal.signal(signal.SIGINT, handle_interrupt)
        print('Press Ctrl+C')
        signal.pause()
        
        # for i in range(n):
        #     t = 60 * (n-i)
        #     print("%i seconds remaining" % t)
        #     sleep(60)
    
    except Exception as e:
        print(e)
        net.stop()
        net.clean()
        infra.shutdown()


    