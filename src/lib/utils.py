def decimal_to_rgb(decimal_number: int):
    h = "%06x" % (decimal_number)
    h = "0" * (6 - len(h)) + h # zero padding

    return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
