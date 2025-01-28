-- refresh materialized view app.summary with data;

drop materialized view if exists app.summary;
create materialized view app.summary as
with
bottle_data as (
	select
		'Bottle' as data_type,
		provider,
		string_agg(
			distinct extract(year from sample_date)::text,
			'; ' order by extract(year from sample_date)::text
		) as years_sampled,
		analyte_name as parameter,
		count(*) as n_measurements
	from app.bottle
	group by
		provider, analyte_name
),
sp_abund_data as (
	select
		'Species Abundance/Biovolume/Community' as data_type,
		provider,
		string_agg(
			distinct extract(year from sample_date)::text,
			'; ' order by extract(year from sample_date)::text
		) as years_sampled,
		parameter || ' - ' || species as parameter,
		count(*) as n_measurements
	from app.sp_abund
	group by
		provider, parameter || ' - ' || species
),
ctd_data as (
	select
		'CTD' as data_type,
		provider,
		string_agg(
			distinct extract(year from sample_date)::text,
			'; ' order by extract(year from sample_date)::text
		) as years_sampled,
		parameter,
		count(*) as n_measurements
	from app.ctd
	group by
		provider, parameter
),
mooring_data as (
	select
		'Mooring' as data_type,
		provider,
		string_agg(
			distinct extract(year from sample_date)::text,
			'; ' order by extract(year from sample_date)::text
		) as years_sampled,
		parameter,
		count(*) as n_measurements
	from app.mooring
	group by
		provider, parameter
),
combined_data as (
	select * from bottle_data
	union all
	select * from sp_abund_data
	union all
	select * from ctd_data
	union all
	select * from mooring_data
)
select
	provider, data_type, years_sampled, parameter, n_measurements
from combined_data
order by
	provider, data_type, parameter
with data;
