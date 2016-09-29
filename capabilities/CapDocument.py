from base import clean_object


def to_cozy(document):
    """
    Export a CapDocument object to JSON, to pass it to Cozy instance.
    """
    # Fetch the list of subscriptions
    try:
        subscriptions = list(document.iter_subscription())
    except NotImplementedError:
        subscriptions = None
    # Fetch and clean the list of bills
    try:
        assert(subscriptions)
        bills = {
            subscription.id: [
                clean_object(bill) for bill in document.iter_documents(subscription)
            ]
            for subscription in subscriptions
        }
    except (NotImplementedError, AssertionError):
        bills = None
    # Fetch and clean the list of history bills (detailed consumption)
    try:
        assert(subscriptions)
        detailed_bills = {
            subscription.id: [
                clean_object(detailed_bill)
                for detailed_bill in document.get_details(subscription)
            ]
            for subscription in subscriptions
        }
    except (NotImplementedError, AssertionError):
        detailed_bills = None
    # Return a formatted dict with all the infos
    ret = {
        "subscriptions": [  # Clean the subscriptions list
            clean_object(subscription) for subscription in subscriptions
        ],
        "bills": bills,
        "detailed_bills": detailed_bills
    }
    return ret
