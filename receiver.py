#!/usr/bin/python3

import boto3
import json
import subprocess


def main():
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='IRCommands.fifo')
    print('Waiting for messages...')
    
    # rc5, rc5x_20, rc5_sz, jvc, sony12, sony15, sony20, nec, necx, nec32, 
    # sanyo, rc6_0, rc6_6a_20, rc6_6a_24, rc6_6a_32,  rc6_mce,  sharp
    # http://manpages.ubuntu.com/manpages/bionic/man1/ir-ctl.1.html
    # to determine the protocol execute `ir-keytable -t -s rc0`
    protocol = 'nec'

    while True:
        for message in queue.receive_messages(WaitTimeSeconds=20):
            print(message.body)
            event = json.loads(message.body)
            scancode_value = event["value"]
            result = subprocess.run(['ir-ctl', '-d', '/dev/lirc0', f'-S {protocol}:{scancode_value}'], check=True, text=True)
            print(result)
            message.delete()


if __name__ == '__main__':
    main()