
-- The MIT License (MIT)

-- Copyright (c) 2016 Dan "Ducky" Little

-- Permission is hereby granted, free of charge, to any person obtaining a copy
-- of this software and associated documentation files (the "Software"), to deal
-- in the Software without restriction, including without limitation the rights
-- to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
-- copies of the Software, and to permit persons to whom the Software is
-- furnished to do so, subject to the following conditions:

-- The above copyright notice and this permission notice shall be included in all
-- copies or substantial portions of the Software.

-- THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
-- IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
-- FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
-- AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
-- LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
-- OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
-- SOFTWARE.

-- Add the appropriate cost columns to the route-able dataset
--
alter table hh_2po_4pgr add column tortuosity float;
alter table hh_2po_4pgr add column tortuosity_cost float;
alter table hh_2po_4pgr add column speed_adjusted_cost float;

-- "zero" out the costs with null
--
update hh_2po_4pgr
 set speed_adjusted_cost = null, tortuosity_cost = null;

-- Calculate the tortousity
--
update hh_2po_4pgr
 set tortuosity = (st_length(geom_way) / st_length(st_makeline(st_startpoint(geom_way), st_endpoint(geom_way)))) 
 where st_length(st_makeline(st_startpoint(geom_way), st_endpoint(geom_way))) != 0;

-- Convert that intoa more routing friendly cost
update hh_2po_4pgr topo
  set tortuosity_cost = (
  	case 
	when tortuosity > 1.5 then 0
	when tortuosity > 1.0001 then .1
	else 1 end
	)
  where topo.tortuosity is not null;

-- clean up stragglers that had issues
update hh_2po_4pgr topo set tortuosity_cost = 1 where topo.tortuosity is null;

-- calculate a time-travel cost, this is used to find the "fast" route.
update hh_2po_4pgr
 set speed_adjusted_cost = km / kmh;
