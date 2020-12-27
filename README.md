# workload-calendar

## Restrictions
*These will be fixed eventually, but as this is not an enterprise product, you will have to work around them until they are.*

1. Does not handle times that cross midnight very well (will stop at 23:59 one one day and resume at 00:00 the next day), so try to have a sane sleep rythm that does not involve being awake past midnight.

1. Task-Deadlines that are further in the future the pre-cached day-count (default: 1000 days / ~3 years) **will** cause unpredictable behaviour when calculating a schedule.