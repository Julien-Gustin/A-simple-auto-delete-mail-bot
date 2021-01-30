import time

def get_current_ms():
    return int(round(time.time() * 1000))


def elapsed_time_to_ms(nb_year=0, nb_month=0, nb_day=0, nb_hour=0, nb_min=0):
    ms = 31536000000*nb_year
    ms += 2629800000*nb_month
    ms += 86400000*nb_day
    ms += 3600000*nb_hour
    ms += 60000*nb_min

    return ms