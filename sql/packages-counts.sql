select
	package,
	count(1)
from
	attributes_plus ap
group by
	package
order by
	count(1) desc;
