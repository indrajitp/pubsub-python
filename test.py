def implicit():
    from google.cloud import pubsub_v1

    # If you don't specify credentials when constructing the client, the
    # client library will look for credentials in the environment.
    #storage_client = storage.Client()
    subscriber = pubsub_v1.SubscriberClient()
    print(f"Received")
    # Make an authenticated API request
    subs = list(subscriber.list_subscriptions())
    print(buckets)

implicit()