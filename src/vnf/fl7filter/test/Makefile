IPADDR=localhost
PORT=9999
RULE_ID=1

get-policies:
	curl http://${IPADDR}:${PORT}/getRules/v1
set-policies:
	curl -X POST -F 'data=@mspl.sample' http://${IPADDR}:${PORT}/setRules/v1
delete-policy:
	curl -X DELETE http://${IPADDR}:${PORT}/flushRule/v1/${RULE_ID}
delete-policies:
	curl -X DELETE http://${IPADDR}:${PORT}/flushRules/v1
