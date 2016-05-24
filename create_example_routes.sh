#!/bin/bash


# The MIT License (MIT)

# Copyright (c) 2016 Dan "Ducky" Little

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.



CONN="dbname=gis user=gis password=gis15fun host=localhost"
TABLE_PREFIX="duluth_to_ely"

# starbucks in duluth
START="-92.07286,46.816695"

# Boathouse brew pub in Ely
FINISH="-91.865675,47.903252"

# Create the duluth->ely run
echo ./create_route.py -- "$CONN" "$START" "$FINISH" $TABLE_PREFIX


# Create the jordan -> green isle 
TABLE_PREFIX="jordan_to_green_isle"

# carasim coffee shop
START="-93.625839,44.665346"

# grey fox tavern, green isle, mn
FINISH="-94.004829,44.677612"

echo ./create_route.py -- "$CONN" "$START" "$FINISH" $TABLE_PREFIX
