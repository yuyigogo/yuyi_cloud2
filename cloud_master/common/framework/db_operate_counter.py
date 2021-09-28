"""
all db operations are following these rules:
C: invoke model.save
R: invoke QuerySet.__call__
D: invoke QuerySet.__call__
U:  1. update(xx) -> filter(xx) -> QuerySet.__call__
    2. model.save

so, if we need to calculate CRUD times,
just handle 'model.save' and 'QuerySet.__call__'.

1. modify GinerativDocument.save
2. modify GinerativDocument's metaclass in order to use DBOperateCounterQuerySetManager
   which will invoke DBOperateCounterQuerySet.__call__
"""

g_db_operate_count = 0


def reset_db_operate_counter():
    global g_db_operate_count
    g_db_operate_count = 0


def increase_db_operate_count(c=1):
    global g_db_operate_count
    g_db_operate_count += c
