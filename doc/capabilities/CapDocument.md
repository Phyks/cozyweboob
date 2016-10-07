CapDocument
===========

This capability is used for modules that have billing support.

| Key             | Value                                                                                                                                                                             | Type         |
|-----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------|
| subscriptions   | List of subscriptions (contracts)                                                                                                                                                 | Subscription |
| bills           | Map of bills for each subscription. Bills are final document produced by the third party.                                                                                         | Bill         |
| documents       | Map of documents for each subscription. Documents are final document produced by the third party, but not bills (typically contract, terms, etc).                                 | Document     |
| history_bills   | Map of history bills for each subscription. History bills are detailed counts for any event resulting in a transaction (typically any communication for a phone service provider) | Detail       |
| detailed_bills  | Map of detailed bills for each subscription. Detailed bills are aggregated counts by facturation type (typically voice and texts for a phone service provider)                    | Detail       |

The fields available for any type are listed [in the Weboob
doc](http://dev.weboob.org/api/capabilities/bill).
