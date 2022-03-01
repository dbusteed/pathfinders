#
# lil script for putting together the map
# that connects the 256 different tile combination
# to the 47 unique combos used for tiles.
# 
# this is done by ignoring corner bits if they aren't
# next to the corresponding vertical/horizontal neighbors 
#

def has_bit(num, mask):
    return num & mask > 0
    
data = {}
for i in range(256):
    j = i
    if has_bit(i, 1) and not (has_bit(i, 2) and has_bit(i, 8)):
        j -= 1
    if has_bit(i, 4) and not (has_bit(i, 2) and has_bit(i, 16)):
        j -= 4
    if has_bit(i, 32) and not (has_bit(i, 8) and has_bit(i, 64)):
        j -= 32
    if has_bit(i, 128) and not (has_bit(i, 64) and has_bit(i, 16)):
        j -= 128
    data[i] = j

print(data)
