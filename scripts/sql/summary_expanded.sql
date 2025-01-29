-- refresh materialized view app.summary_expanded with data;

drop materialized view if exists app.summary_expanded;
create materialized view app.summary_expanded as
with
bottle_data as (
	select
		'Bottle' as data_type,
		provider,
		sampdocs.document_title,
		sampdocs.files,
		string_agg(
			distinct extract(year from sample_date)::text,
			'; ' order by extract(year from sample_date)::text
		) as years_sampled,
		string_agg(
			distinct coll_scheme, '; ' order by coll_scheme
		) as coll_scheme,
		analyte_name as parameter,
		string_agg(
			distinct units, '; ' order by units
		) as units,
		count(*) as n_measurements,
		min(result) as "min",
		max(result) as "max",
		PERCENTILE_CONT(0.25) WITHIN GROUP(ORDER BY result) as "25th_percentile",
		PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY result) as "median",
		PERCENTILE_CONT(0.75) WITHIN GROUP(ORDER BY result) as "75th_percentile"
	from app.bottle as s
	left join (
		select
			sd.study_id, sd.sample_id,
			df.document_title, df.files
		from d_sampdoc as sd
		left join (
			select
				doc.doc_id,
				doc.title as document_title,
				string_agg(distinct f.original_filename, '; ' order by f.original_filename) as files
			from d_document as doc
			left join d_docfile as docf on doc.doc_id=docf.doc_id
			left join d_file as f on docf.filename=f.filename
			group by
				doc.doc_id, doc.title
		) as df on sd.doc_id=df.doc_id
	) as sampdocs on s.study_id=sampdocs.study_id and s.sample_id=sampdocs.sample_id
	group by
		provider,
		analyte_name,
		sampdocs.document_title,
		sampdocs.files
),
sp_abund_data as (
	select
		'Species Abundance/Biovolume/Community' as data_type,
		provider,
		sampdocs.document_title,
		sampdocs.files,
		string_agg(
			distinct extract(year from sample_date)::text,
			'; ' order by extract(year from sample_date)::text
		) as years_sampled,
		string_agg(
			distinct coll_scheme, '; ' order by coll_scheme
		) as coll_scheme,
		parameter || ' - ' || species as parameter,
		string_agg(
			distinct units, '; ' order by units
		) as units,
		count(*) as n_measurements,
		min(result) as "min",
		max(result) as "max",
		PERCENTILE_CONT(0.25) WITHIN GROUP(ORDER BY result) as "25th_percentile",
		PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY result) as "median",
		PERCENTILE_CONT(0.75) WITHIN GROUP(ORDER BY result) as "75th_percentile"
	from app.sp_abund as s
	left join (
		select
			sd.study_id, sd.sample_id,
			df.document_title, df.files
		from d_sampdoc as sd
		left join (
			select
				doc.doc_id,
				doc.title as document_title,
				string_agg(distinct f.original_filename, '; ' order by f.original_filename) as files
			from d_document as doc
			left join d_docfile as docf on doc.doc_id=docf.doc_id
			left join d_file as f on docf.filename=f.filename
			group by
				doc.doc_id, doc.title
		) as df on sd.doc_id=df.doc_id
	) as sampdocs on s.study_id=sampdocs.study_id and s.sample_id=sampdocs.sample_id
	group by
		provider,
		parameter || ' - ' || species,
		sampdocs.document_title,
		sampdocs.files
),
ctd_data as (
	select
		'CTD' as data_type,
		provider,
		sampdocs.document_title,
		sampdocs.files,
		string_agg(
			distinct extract(year from sample_date)::text,
			'; ' order by extract(year from sample_date)::text
		) as years_sampled,
		string_agg(
			distinct coll_scheme, '; ' order by coll_scheme
		) as coll_scheme,
		parameter,
		string_agg(
			distinct units, '; ' order by units
		) as units,
		count(*) as n_measurements,
		min(result) as "min",
		max(result) as "max",
		PERCENTILE_CONT(0.25) WITHIN GROUP(ORDER BY result) as "25th_percentile",
		PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY result) as "median",
		PERCENTILE_CONT(0.75) WITHIN GROUP(ORDER BY result) as "75th_percentile"
	from app.ctd as s
	left join (
		select
			sd.study_id, sd.sample_id,
			df.document_title, df.files
		from d_sampdoc as sd
		left join (
			select
				doc.doc_id,
				doc.title as document_title,
				string_agg(distinct f.original_filename, '; ' order by f.original_filename) as files
			from d_document as doc
			left join d_docfile as docf on doc.doc_id=docf.doc_id
			left join d_file as f on docf.filename=f.filename
			group by
				doc.doc_id, doc.title
		) as df on sd.doc_id=df.doc_id
	) as sampdocs on s.study_id=sampdocs.study_id and s.sample_id=sampdocs.sample_id
	group by
		provider,
		parameter,
		sampdocs.document_title,
		sampdocs.files
),
mooring_data as (
	select
		'Mooring' as data_type,
		provider,
		sampdocs.document_title,
		sampdocs.files,
		string_agg(
			distinct extract(year from sample_date)::text,
			'; ' order by extract(year from sample_date)::text
		) as years_sampled,
		string_agg(
			distinct coll_scheme, '; ' order by coll_scheme
		) as coll_scheme,
		parameter,
		string_agg(
			distinct units, '; ' order by units
		) as units,
		count(*) as n_measurements,
		min(result) as "min",
		max(result) as "max",
		PERCENTILE_CONT(0.25) WITHIN GROUP(ORDER BY result) as "25th_percentile",
		PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY result) as "median",
		PERCENTILE_CONT(0.75) WITHIN GROUP(ORDER BY result) as "75th_percentile"
	from app.mooring as s
	left join (
		select
			sd.study_id, sd.sample_id,
			df.document_title, df.files
		from d_sampdoc as sd
		left join (
			select
				doc.doc_id,
				doc.title as document_title,
				string_agg(distinct f.original_filename, '; ' order by f.original_filename) as files
			from d_document as doc
			left join d_docfile as docf on doc.doc_id=docf.doc_id
			left join d_file as f on docf.filename=f.filename
			group by
				doc.doc_id, doc.title
		) as df on sd.doc_id=df.doc_id
	) as sampdocs on s.study_id=sampdocs.study_id and s.sample_id=sampdocs.sample_id
	group by
		provider,
		parameter,
		sampdocs.document_title,
		sampdocs.files
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
	provider, data_type, document_title, files as document_files,
	years_sampled, coll_scheme, parameter, units, n_measurements,
	"min", "max", "25th_percentile", "median", "75th_percentile"
from combined_data
order by
	provider, data_type, document_title, parameter
with data;
