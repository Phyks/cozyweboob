"""
This module contains all the conversion functions associated to the Document
capability.
"""
from cozyweboob.capabilities.base import clean_object
from weboob.capabilities.bill import Bill


def fetch_subscriptions(document):
    """
    Fetch the list of subscriptions

    Args:
        document: The CapDocument object to handle.
    Returns: A list of subscriptions
    """
    try:
        subscriptions = list(document.iter_subscription())
    except NotImplementedError:
        subscriptions = None
    return subscriptions


def fetch_documents(document, subscriptions):
    """
    Fetch and clean the list of bills

    Bills are formatted final documents emitted by the third party (typically
    monthly bills for a phone service provider)
    Documents are more general and can be contracts, terms etc.

    Args:
        document: The CapDocument object to handle.
        subscriptions: A list of subscriptions for the CapDocument object.
    Returns: A tuple of cleaned list of documents and bills.
    """
    # Get the BASEURL to generate absolute URLs
    base_url = document.browser.BASEURL
    try:
        assert subscriptions
        raw_documents = {
            subscription.id: list(document.iter_documents(subscription))
            for subscription in subscriptions
        }
        raw_bills = {
            subscription: [
                bill for bill in documents if isinstance(bill, Bill)
            ]
            for subscription, documents in raw_documents.items()
        }
        bills = {
            subscription: [
                clean_object(bill, base_url=base_url)
                for bill in bills_list
            ]
            for subscription, bills_list in raw_bills.items()
        }
        documents = {
            subscription: [
                clean_object(bill, base_url=base_url)
                for bill in documents_list
                if bill not in raw_bills[subscription]
            ]
            for subscription, documents_list in raw_documents.items()
        }
    except (NotImplementedError, AssertionError):
        documents = None
        bills = None
    return documents, bills


def fetch_details(document, subscriptions):
    """
    Fetch and clean the list of details of the subscription (detailed
    consumption)

    Details are aggregated billing counts (typically aggregated counts by
    communication type for a phone service provider)

    Args:
        document: The CapDocument object to handle.
        subscriptions: A list of subscriptions for the CapDocument object.
    Returns: A cleaned list of detailed bills.
    """
    # Get the BASEURL to generate absolute URLs
    base_url = document.browser.BASEURL
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
    return detailed_bills


def fetch_history(document, subscriptions):
    """
    Fetch and clean the list of history bills

    History bills are detailed bills for any event that resulted in a bill
    (typically any communication for a phone service provider)

    Args:
        document: The CapDocument object to handle.
        subscriptions: A list of subscriptions for the CapDocument object.
    Returns: A cleaned list of history bills.
    """
    # Get the BASEURL to generate absolute URLs
    base_url = document.browser.BASEURL
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
    return history_bills


def fetch(document, fetch_actions):
    """
    Fetch all required items from a CapDocument object.

    Args:
        document: The CapDocument object to fetch from.
        fetch_actions: A dict describing what should be fetched (see README.md)
    Returns:
        A tuple of fetched subscriptions, documents, bills, detailed bills and
        history bills.
    """
    subscriptions = fetch_subscriptions(document)

    if fetch_actions is True or "documents" in fetch_actions:
        documents, bills = fetch_documents(document, subscriptions)
    else:
        documents, bills = None, None

    if fetch_actions is True or "detailed_bills" in fetch_actions:
        detailed_bills = fetch_details(document, subscriptions)
    else:
        detailed_bills = None

    if fetch_actions is True or "history_bills" in fetch_actions:
        history_bills = fetch_history(document, subscriptions)
    else:
        history_bills = None

    return (subscriptions, documents, bills, detailed_bills, history_bills)


def to_cozy(document, actions=None):
    """
    Export a CapDocument object to a JSON-serializable dict, to pass it to Cozy
    instance.

    Args:
        document: The CapDocument object to handle.
        actions: A dict describing what should be fetched (see README.md).
    Returns: A JSON-serializable dict for the input object.
    """
    # Handle default parameters
    if actions is None:
        actions = {"fetch": True, "download": False}

    # Get the BASEURL to generate absolute URLs
    base_url = document.browser.BASEURL

    # Handle fetch actions
    if actions["fetch"] is True or "CapDocument" in actions["fetch"]:
        if actions["fetch"] is True:
            fetch_actions = actions["fetch"]
        else:
            fetch_actions = actions["fetch"]["CapDocument"]
        subscriptions, documents, bills, detailed_bills, history_bills = fetch(
            document, fetch_actions)

    # Return a formatted dict with all the infos
    return {
        "subscriptions": [  # Clean the subscriptions list
            clean_object(subscription, base_url=base_url)
            for subscription in subscriptions
        ],
        "bills": bills,
        "detailed_bills": detailed_bills,
        "documents": documents,
        "history_bills": history_bills
    }
