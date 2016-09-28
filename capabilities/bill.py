from base import clean_object


def to_cozy(document):
    """
    Export a CapDocument object to JSON, to pass it to Cozy instance.
    """
    # Fetch the list of subscriptions
    subscriptions = list(document.iter_subscription())
    # Return a formatted dict with all the infos
    return {
        "subscriptions": [  # List of subscriptions
            clean_object(subscription) for subscription in subscriptions
        ],
        "bills": {  # List of bills for each subscription
            subscription.id: [
                clean_object(bill) for bill in document.iter_bills(subscription)
            ]
            for subscription in subscriptions
        }
    }
