"""
This module contains all the conversion functions associated to the Document
capability.
"""
from base import clean_object


def to_cozy(document):
    """
    Export a CapDocument object to a JSON-serializable dict, to pass it to Cozy
    instance.

    Args:
        document: The CapDocument object to handle.
    Returns: A JSON-serializable dict for the input object.
    """
    # Get the BASEURL to generate absolute URLs
    base_url = document.browser.BASEURL
    # Fetch the list of subscriptions
    try:
        subscriptions = list(document.iter_subscription())
    except NotImplementedError:
        subscriptions = None

    # Fetch and clean the list of bills
    # Bills are formatted final documents emitted by the third party (typically
    # monthly bills for a phone service provider)
    try:
        assert subscriptions
        bills = {
            subscription.id: [
                clean_object(bill, base_url=base_url)
                for bill in document.iter_documents(subscription)
            ]
            for subscription in subscriptions
        }
    except (NotImplementedError, AssertionError):
        bills = None

    # Fetch and clean the list of details of the subscription (detailed
    # consumption)
    # Details are aggregated billing counts (typically aggregated counts by
    # communication type for a phone service provider)
    try:
        assert subscriptions
        detailed_bills = {
            subscription.id: [
                clean_object(detailed_bill, base_url=base_url)
                for detailed_bill in document.get_details(subscription)
            ]
            for subscription in subscriptions
        }
    except (NotImplementedError, AssertionError):
        detailed_bills = None

    # Fetch and clean the list of history bills
    # History bills are detailed bills for any event that resulted in a bill
    # (typically any communication for a phone service provider)
    try:
        assert subscriptions
        history_bills = {
            subscription.id: [
                clean_object(history_bill, base_url=base_url)
                for history_bill in
                document.iter_documents_history(subscription)
            ]
            for subscription in subscriptions
        }
    except (NotImplementedError, AssertionError):
        history_bills = None

    # Return a formatted dict with all the infos
    return {
        "subscriptions": [  # Clean the subscriptions list
            clean_object(subscription, base_url=base_url)
            for subscription in subscriptions
        ],
        "bills": bills,
        "detailed_bills": detailed_bills,
        "history_bills": history_bills
    }
