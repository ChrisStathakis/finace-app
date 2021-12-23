from django.db.models import Sum, Avg




def calculate_sum(my_string, qs):
    if qs.exists():
        return qs.aggregate(Sum(my_string))[f'{my_string}__sum']
    return 0

def calculate_avg(my_string, qs):
    if qs.exists():
        return qs.aggregate(Avg(my_string))[f'{my_string}__avg']
    return 0