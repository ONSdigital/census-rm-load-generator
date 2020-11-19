from utilities.rabbit_context import RabbitContext

QUEUES = ['Action.Printer', 'case.fulfilments', 'case.refusals', 'case.rh.uac.dlq', 'notify.fulfilments',
          'case.rm.updated', 'RM.Field', 'case.ccsPropertyListedQueue', 'Gateway.ActionsDLQ', 'Action.Field',
          'case.rh.case', 'case.action', 'unaddressedRequestQueue', 'case.rh.case.dlq', 'case.field.update',
          'case.fulfilmentConfirmed', 'pubsub.quarantine', 'case.questionnairelinked', 'FieldworkAdapter.caseUpdated',
          'RM.FieldDLQ', 'case.rm.unInvalidateAddress', 'survey.launched', 'action.fulfilment',
          'case.undeliveredMailQueue', 'action.events', 'case.rh.uac', 'Gateway.Actions', 'Case.Responses',
          'case.addressQueue', 'notify.enriched.fulfilment', 'delayedRedeliveryQueue', 'case.deactivate-uac',
          'case.sample.inbound', 'case.uac-qid-created']


def purge_queues(queues):
    with RabbitContext() as rabbit_connection:
        for queue in queues:
            rabbit_connection.channel.queue_purge(queue=queue)


def main():
    purge_queues(QUEUES)
if __name__ == "__main__":
    main()
