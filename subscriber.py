#!/usr/bin/env python

# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This application demonstrates how to perform basic operations on
subscriptions with the Cloud Pub/Sub API.

For more information, see the README.md under /pubsub and the documentation
at https://cloud.google.com/pubsub/docs.
"""

import argparse


def receive_messages(project_id, subscription_id, timeout=None):
    """Receives messages from a pull subscription."""
    # [START pubsub_subscriber_async_pull]
    # [START pubsub_quickstart_subscriber]
    from concurrent.futures import TimeoutError
    from google.cloud import pubsub_v1

    # TODO(developer)
    # project_id = "your-project-id"
    # subscription_id = "your-subscription-id"
    # Number of seconds the subscriber should listen for messages
    # timeout = 5.0

    subscriber = pubsub_v1.SubscriberClient()
    # The `subscription_path` method creates a fully qualified identifier
    # in the form `projects/{project_id}/subscriptions/{subscription_id}`
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    def callback(message):
        print(f"Received {message}.")
        message.ack()

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for messages on {subscription_path}..\n")

    # Wrap subscriber in a 'with' block to automatically call close() when done.
    with subscriber:
        try:
            # When `timeout` is not set, result() will block indefinitely,
            # unless an exception is encountered first.
            streaming_pull_future.result(timeout=timeout)
        except TimeoutError:
            streaming_pull_future.cancel()
    # [END pubsub_subscriber_async_pull]
    # [END pubsub_quickstart_subscriber]


def receive_messages_with_custom_attributes(project_id, subscription_id, timeout=None):
    """Receives messages from a pull subscription."""
    # [START pubsub_subscriber_async_pull_custom_attributes]
    from concurrent.futures import TimeoutError
    from google.cloud import pubsub_v1
    #credential_path = (r"C:\Users\Shree\Desktop\python\pubsub-python\service-account.json")
    #os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
    # TODO(developer)
    # project_id = "your-project-id"
    # subscription_id = "your-subscription-id"
    # Number of seconds the subscriber should listen for messages
    # timeout = 5.0

    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    def callback(message):
        print(f"Received {message.data}.")
        if message.attributes:
            print("Attributes:")
            for key in message.attributes:
                value = message.attributes.get(key)
                print(f"{key}: {value}")
        message.ack()

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for messages on {subscription_path}..\n")

    # Wrap subscriber in a 'with' block to automatically call close() when done.
    with subscriber:
        try:
            # When `timeout` is not set, result() will block indefinitely,
            # unless an exception is encountered first.
            streaming_pull_future.result(timeout=timeout)
        except TimeoutError:
            streaming_pull_future.cancel()
    # [END pubsub_subscriber_async_pull_custom_attributes]


def receive_messages_with_flow_control(project_id, subscription_id, timeout=None):
    """Receives messages from a pull subscription with flow control."""
    # [START pubsub_subscriber_flow_settings]
    from concurrent.futures import TimeoutError
    from google.cloud import pubsub_v1

    # TODO(developer)
    # project_id = "your-project-id"
    # subscription_id = "your-subscription-id"
    # Number of seconds the subscriber should listen for messages
    # timeout = 5.0

    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    def callback(message):
        print(f"Received {message.data}.")
        message.ack()
        print(f"Sending to publisher method to push")

    # Limit the subscriber to only have ten outstanding messages at a time.
    flow_control = pubsub_v1.types.FlowControl(max_messages=10)

    streaming_pull_future = subscriber.subscribe(
        subscription_path, callback=callback, flow_control=flow_control
    )
    print(f"Listening for messages on {subscription_path}..\n")

    # Wrap subscriber in a 'with' block to automatically call close() when done.
    with subscriber:
        try:
            # When `timeout` is not set, result() will block indefinitely,
            # unless an exception is encountered first.
            streaming_pull_future.result(timeout=timeout)
        except TimeoutError:
            streaming_pull_future.cancel()
    # [END pubsub_subscriber_flow_settings]


def receive_messages_with_blocking_shutdown(project_id, subscription_id, timeout=5.0):
    """Shuts down a pull subscription by awaiting message callbacks to complete."""
    # [START pubsub_subscriber_blocking_shutdown]
    import time
    from concurrent.futures import TimeoutError
    from google.cloud import pubsub_v1

    # TODO(developer)
    # project_id = "your-project-id"
    # subscription_id = "your-subscription-id"
    # Number of seconds the subscriber should listen for messages
    # timeout = 5.0

    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    def callback(message):
        print(f"Received {message.data}.")
        time.sleep(timeout + 5.0)  # Pocess longer than streaming pull future timeout.
        message.ack()
        print(f"Done processing the message {message.data}.")

    streaming_pull_future = subscriber.subscribe(
        subscription_path, callback=callback, await_callbacks_on_shutdown=True,
    )
    print(f"Listening for messages on {subscription_path}..\n")

    # Wrap subscriber in a 'with' block to automatically call close() when done.
    with subscriber:
        try:
            # When `timeout` is not set, result() will block indefinitely,
            # unless an exception is encountered first.
            streaming_pull_future.result(timeout=timeout)
        except TimeoutError:
            streaming_pull_future.cancel()
            print("Streaming pull future canceled.")
            streaming_pull_future.result()  # Blocks until shutdown complete.
            print("Done waiting for the stream shutdown.")

    # The "Done waiting..." message is only printed *after* the processing of all
    # received messages has completed.
    # [END pubsub_subscriber_blocking_shutdown]


def synchronous_pull(project_id, subscription_id):
    """Pulling messages synchronously."""
    # [START pubsub_subscriber_sync_pull]
    from google.api_core import retry
    from google.cloud import pubsub_v1

    # TODO(developer)
    # project_id = "your-project-id"
    # subscription_id = "your-subscription-id"

    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    NUM_MESSAGES = 3

    # Wrap the subscriber in a 'with' block to automatically call close() to
    # close the underlying gRPC channel when done.
    with subscriber:
        # The subscriber pulls a specific number of messages. The actual
        # number of messages pulled may be smaller than max_messages.
        response = subscriber.pull(
            request={"subscription": subscription_path, "max_messages": NUM_MESSAGES},
            retry=retry.Retry(deadline=300),
        )

        ack_ids = []
        for received_message in response.received_messages:
            print(f"Received: {received_message.message.data}.")
            ack_ids.append(received_message.ack_id)

        # Acknowledges the received messages so they will not be sent again.
        subscriber.acknowledge(
            request={"subscription": subscription_path, "ack_ids": ack_ids}
        )

        print(
            f"Received and acknowledged {len(response.received_messages)} messages from {subscription_path}."
        )
    # [END pubsub_subscriber_sync_pull]


def synchronous_pull_with_lease_management(project_id, subscription_id):
    """Pulling messages synchronously with lease management"""
    # [START pubsub_subscriber_sync_pull_with_lease]
    import logging
    import multiprocessing
    import sys
    import time

    from google.api_core import retry
    from google.cloud import pubsub_v1

    multiprocessing.log_to_stderr()
    logger = multiprocessing.get_logger()
    logger.setLevel(logging.INFO)
    processes = dict()

    # TODO(developer)
    # project_id = "your-project-id"
    # subscription_id = "your-subscription-id"

    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    response = subscriber.pull(
        request={"subscription": subscription_path, "max_messages": 3},
        retry=retry.Retry(deadline=300),
    )

    # Start a process for each message based on its size modulo 10.
    for message in response.received_messages:
        process = multiprocessing.Process(
            target=time.sleep, args=(sys.getsizeof(message) % 10,)
        )
        processes[process] = (message.ack_id, message.message.data)
        process.start()

    while processes:
        # Take a break every second.
        if processes:
            time.sleep(1)

        for process in list(processes):
            ack_id, msg_data = processes[process]
            # If the process is running, reset the ack deadline.
            if process.is_alive():
                subscriber.modify_ack_deadline(
                    request={
                        "subscription": subscription_path,
                        "ack_ids": [ack_id],
                        # Must be between 10 and 600.
                        "ack_deadline_seconds": 15,
                    }
                )
                logger.info(f"Reset ack deadline for {msg_data}.")

            # If the process is complete, acknowledge the message.
            else:
                subscriber.acknowledge(
                    request={"subscription": subscription_path, "ack_ids": [ack_id]}
                )
                logger.info(f"Acknowledged {msg_data}.")
                processes.pop(process)
    print(
        f"Received and acknowledged {len(response.received_messages)} messages from {subscription_path}."
    )

    # Close the underlying gPRC channel. Alternatively, wrap subscriber in
    # a 'with' block to automatically call close() when done.
    subscriber.close()
    # [END pubsub_subscriber_sync_pull_with_lease]


def listen_for_errors(project_id, subscription_id, timeout=None):
    """Receives messages and catches errors from a pull subscription."""
    # [START pubsub_subscriber_error_listener]
    from google.cloud import pubsub_v1

    # TODO(developer)
    # project_id = "your-project-id"
    # subscription_id = "your-subscription-id"
    # Number of seconds the subscriber should listen for messages
    # timeout = 5.0

    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    def callback(message):
        print(f"Received {message}.")
        message.ack()

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for messages on {subscription_path}..\n")

    # Wrap subscriber in a 'with' block to automatically call close() when done.
    with subscriber:
        # When `timeout` is not set, result() will block indefinitely,
        # unless an exception is encountered first.
        try:
            streaming_pull_future.result(timeout=timeout)
        except Exception as e:
            streaming_pull_future.cancel()
            print(
                f"Listening for messages on {subscription_path} threw an exception: {e}."
            )
    # [END pubsub_subscriber_error_listener]


def receive_messages_with_delivery_attempts(project_id, subscription_id, timeout=None):
    # [START pubsub_dead_letter_delivery_attempt]
    from concurrent.futures import TimeoutError
    from google.cloud import pubsub_v1

    # TODO(developer)
    # project_id = "your-project-id"
    # subscription_id = "your-subscription-id"

    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    def callback(message):
        print(f"Received {message}.")
        print(f"With delivery attempts: {message.delivery_attempt}.")
        message.ack()

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for messages on {subscription_path}..\n")

    # Wrap subscriber in a 'with' block to automatically call close() when done.
    with subscriber:
        # When `timeout` is not set, result() will block indefinitely,
        # unless an exception is encountered first.
        try:
            streaming_pull_future.result(timeout=timeout)
        except TimeoutError:
            streaming_pull_future.cancel()
    # [END pubsub_dead_letter_delivery_attempt]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("project_id", help="Your Google Cloud project ID")

    subparsers = parser.add_subparsers(dest="command")

    receive_parser = subparsers.add_parser("receive", help=receive_messages.__doc__)
    receive_parser.add_argument("subscription_id")
    receive_parser.add_argument("timeout", default=None, type=float, nargs="?")

    receive_with_custom_attributes_parser = subparsers.add_parser(
        "receive-custom-attributes",
        help=receive_messages_with_custom_attributes.__doc__,
    )
    receive_with_custom_attributes_parser.add_argument("subscription_id")
    receive_with_custom_attributes_parser.add_argument(
        "timeout", default=None, type=float, nargs="?"
    )

    receive_with_flow_control_parser = subparsers.add_parser(
        "receive-flow-control", help=receive_messages_with_flow_control.__doc__
    )
    receive_with_flow_control_parser.add_argument("subscription_id")
    receive_with_flow_control_parser.add_argument(
        "timeout", default=None, type=float, nargs="?"
    )

    receive_with_blocking_shutdown_parser = subparsers.add_parser(
        "receive-blocking-shutdown",
        help=receive_messages_with_blocking_shutdown.__doc__,
    )
    receive_with_blocking_shutdown_parser.add_argument("subscription_id")
    receive_with_blocking_shutdown_parser.add_argument(
        "timeout", default=None, type=float, nargs="?"
    )

    synchronous_pull_parser = subparsers.add_parser(
        "receive-synchronously", help=synchronous_pull.__doc__
    )
    synchronous_pull_parser.add_argument("subscription_id")

    synchronous_pull_with_lease_management_parser = subparsers.add_parser(
        "receive-synchronously-with-lease",
        help=synchronous_pull_with_lease_management.__doc__,
    )
    synchronous_pull_with_lease_management_parser.add_argument("subscription_id")

    listen_for_errors_parser = subparsers.add_parser(
        "listen-for-errors", help=listen_for_errors.__doc__
    )
    listen_for_errors_parser.add_argument("subscription_id")
    listen_for_errors_parser.add_argument(
        "timeout", default=None, type=float, nargs="?"
    )

    receive_messages_with_delivery_attempts_parser = subparsers.add_parser(
        "receive-messages-with-delivery-attempts",
        help=receive_messages_with_delivery_attempts.__doc__,
    )
    receive_messages_with_delivery_attempts_parser.add_argument("subscription_id")
    receive_messages_with_delivery_attempts_parser.add_argument(
        "timeout", default=None, type=float, nargs="?"
    )

    args = parser.parse_args()

    if args.command == "list-in-topic":
        list_subscriptions_in_topic(args.project_id, args.topic_id)
    elif args.command == "list-in-project":
        list_subscriptions_in_project(args.project_id)
    elif args.command == "create":
        create_subscription(args.project_id, args.topic_id, args.subscription_id)
    elif args.command == "create-with-dead-letter-policy":
        create_subscription_with_dead_letter_topic(
            args.project_id,
            args.topic_id,
            args.subscription_id,
            args.dead_letter_topic_id,
            args.max_delivery_attempts,
        )
    elif args.command == "create-push":
        create_push_subscription(
            args.project_id, args.topic_id, args.subscription_id, args.endpoint,
        )
    elif args.command == "create-with-ordering":
        create_subscription_with_ordering(
            args.project_id, args.topic_id, args.subscription_id
        )
    elif args.command == "delete":
        delete_subscription(args.project_id, args.subscription_id)
    elif args.command == "update-push":
        update_push_subscription(
            args.project_id, args.topic_id, args.subscription_id, args.endpoint,
        )
    elif args.command == "update-dead-letter-policy":
        update_subscription_with_dead_letter_policy(
            args.project_id,
            args.topic_id,
            args.subscription_id,
            args.dead_letter_topic_id,
            args.max_delivery_attempts,
        )
    elif args.command == "remove-dead-letter-policy":
        remove_dead_letter_policy(args.project_id, args.topic_id, args.subscription_id)
    elif args.command == "receive":
        receive_messages(args.project_id, args.subscription_id, args.timeout)
    elif args.command == "receive-custom-attributes":
        receive_messages_with_custom_attributes(
            args.project_id, args.subscription_id, args.timeout
        )
    elif args.command == "receive-flow-control":
        receive_messages_with_flow_control(
            args.project_id, args.subscription_id, args.timeout
        )
    elif args.command == "receive-blocking-shutdown":
        receive_messages_with_blocking_shutdown(
            args.project_id, args.subscription_id, args.timeout
        )
    elif args.command == "receive-synchronously":
        synchronous_pull(args.project_id, args.subscription_id)
    elif args.command == "receive-synchronously-with-lease":
        synchronous_pull_with_lease_management(args.project_id, args.subscription_id)
    elif args.command == "listen-for-errors":
        listen_for_errors(args.project_id, args.subscription_id, args.timeout)
    elif args.command == "receive-messages-with-delivery-attempts":
        receive_messages_with_delivery_attempts(
            args.project_id, args.subscription_id, args.timeout
        )
