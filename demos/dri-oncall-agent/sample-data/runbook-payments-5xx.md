# Runbook — payments-api 5xx spikes

**Service:** payments-api  
**Owner:** @alicez (primary), @rmehta (secondary)  
**Last updated:** 2026-05-14

## Symptoms

- Elevated 5xx rate on `POST /charge` or `POST /refund`.
- P95 latency > 300ms on affected endpoints.
- Sudden onset within 5 minutes, often correlated with a deploy or config change.

## Common causes

1. **Idempotency-key cache misconfiguration** *(most common after deploy)*  
   The idempotency-key TTL or eviction policy changed and the cache is thrashing, causing duplicate-request errors to surface as 5xx.
2. **Downstream ledger timeouts.** Check `payments-ledger` health first.
3. **Secret rotation lag.** New signing key not yet propagated to all pods.
4. **DB connection pool exhaustion** during traffic spikes.

## Diagnostic queries (KQL)

```kql
AppRequests
| where TimeGenerated > ago(30m)
| where AppRoleName == "payments-api"
| where OperationName in ("POST /charge","POST /refund")
| summarize req=count(), errs=countif(ResultCode >= 500) by bin(TimeGenerated, 1m), OperationName
| extend err_rate = todouble(errs) / req
| order by TimeGenerated desc
```

```kql
AppTraces
| where TimeGenerated > ago(30m)
| where AppRoleName == "payments-api"
| where Message contains "idempotency"
| summarize count() by SeverityLevel, bin(TimeGenerated, 1m)
```

## Mitigation (in priority order)

1. **Rollback deploy** if 5xx onset correlates with a deploy in the last 30 minutes.
   ```
   az deployment group create \
     --resource-group rg-payments-prod \
     --template-file rollback.bicep \
     --parameters targetVersion=<previous-version>
   ```
2. **Bypass idempotency cache** (feature flag `payments.idempotency.bypass=true`) — only if rollback is not viable and cause is confirmed.
3. **Scale out** by 50% while investigating (does not fix root cause).

## Validation after mitigation

Re-run the diagnostic KQL above. Expect `err_rate < 0.005` sustained for 5 minutes.

## Related retros

- retro-2025-11-18 — idempotency TTL regression.
- retro-2025-08-02 — ledger timeout cascading to charge.
