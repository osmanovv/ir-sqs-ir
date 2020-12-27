#!/usr/bin/python3

from evdev import InputDevice 
import boto3


def sqs_send(queue, event):
    """Sends IR event to queue.

    Args:
        queue: A FIFO queue name.
        event: Captured IR event.

    """
    response = queue.send_message(MessageBody=f"{{'sec':'{event.sec}','usec':'{event.usec}','type':'{event.type}','code':'{event.code}','value':'{event.value}'}}", MessageGroupId='IR-0001', MessageDeduplicationId=str(event.timestamp()))


def main():
    # create IR reciever
    irr = InputDevice('/dev/input/event0')
    print(f'Device created:\n{irr}')

    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='IRCommands.fifo')
    
    print('Press remote IR buttons, Ctrl-C to quit')
    
    prev_msg_time = 0

    # handle IR events
    for event in irr.read_loop():
        # prevent sending the same messages at the same time by comparing they timestamps
        # API Reference - events: https://python-evdev.readthedocs.io/en/latest/apidoc.html#module-evdev.events
        if event.type == 4 and prev_msg_time != event.sec:
            sqs_send(queue, event)
            print(event)
            prev_msg_time = event.sec


if __name__ == '__main__':
    main()