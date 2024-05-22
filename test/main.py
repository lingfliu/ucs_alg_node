from alg_wrapper import AlgWrapper
from src.ucs_alg_node.alg import Alg

import argparse

class MyAlg(Alg):
    def infer(self):
        for i in range(10):
            yield i
def main(port=8888, model='', mode='batch', source='', mq=''):
    # start http server with port
    alg_wrapper = AlgWrapper(alg=None, source=source, mode=mode)
    x = [i for i in range(10)]
    for d in x:
        for res in alg_wrapper.infer(d):
            print(res)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Algorithm parser')
    parser.add_argument('--port', type=int, help='server port, default is 8888')
    parser.add_argument('--source', type=str, help='Source of data')
    parser.add_argument('--mode', type=str, help='Mode of inference')
    parser.add_argument('--model', type=str, help='Loaded model')
    parser.add_argument('--mq', type=str, help='MQ url') # MQ if alg result is uploaded in publish-subscribe mode
    args = parser.parse_args()

    # if len(args.mq) < 0:
    #     exit(-1)
    if args.mode and len(args.mode) > 0:
        if args.mode != 'batch' and args.mode != 'stream':
            exit(-2)
        elif args.mode == 'stream' and len(args.source) < 0:
            exit(-3)

    main(port=args.port, model=args.model, mode=args.mode, source=args.source, mq=args.mq)