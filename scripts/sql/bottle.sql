-- refresh materialized view app.bottle with data;

drop materialized view if exists app.bottle;
create materialized view app.bottle as
select
    reg.area_id,
    loc.location_id,
    loc.description as loc_desc,
    lt.description as loc_type,
    loc.loc_geom,
    st_x(loc.loc_geom) as x_coord,
    st_y(loc.loc_geom) as y_coord,
    st_srid(loc.loc_geom) as srid,
    loc.coord_sys,
    locm.description as loc_method,
    st.contact as "provider",
    st.study_id,
    st.full_name as study_name,
    sdoc.sample_doc,
    sc.sample_date,
    cs.description as coll_scheme,
    sm.sample_material,
    sm.sample_id,
    sm.description as sample_desc,
    sm.original_id as original_sample_id,
    sm.upper_depth,
    sm.lower_depth,
    sm.depth_units,
    ss.split_type::text,
    ss.sample_no,
    el.lab_name as lab,
    lr.lab_pkg,
    resmat.material,
    lr.material_analyzed,
    lr.labsample,
    lr.lab_rep,
    lr.method_code,
    am.description as method_desc,
    ea.chem_class,
    ea.cas_rn,
    lr.analyte,
    ea.full_name as analyte_name,
    (lr.meas_value).value as result,
    case
        when
            not (lr.meas_value).undetected
        and not (lr.meas_value).estimated
        and not (lr.meas_value).rejected
        and not (lr.meas_value).greater_than
        then null
        else
            case
            when (lr.meas_value).undetected then 'U'
            else ''
        end
                || case
            when (lr.meas_value).estimated then 'J'
            else ''
        end
                || case
            when (lr.meas_value).rejected then 'R'
            else ''
        end
                || case
            when (lr.meas_value).greater_than then '>'
            else ''
        end
    end as qualifiers,
    lr.lab_flags,
    lr.validator_flags,
    case
        when (lr.meas_value).undetected then 'False'
        else 'True'
    end::text as detected,
    lr.detection_limit,
    lr.quantification_limit,
    lr.reporting_limit,
    lr.units,
    lr.meas_basis,
    lr.fraction,
    lr.dilution_factor,
    lr.data_quality,
    qa.description as qa_level,
    lr.date_analyzed,
    lr.date_extracted,
    lrdoc.doc_file,
    lr.comments
from
    d_labresult as lr
inner join d_labsample as ls on
    lr.labsample = ls.labsample
    and lr.lab = ls.lab
inner join d_sampsplit as ss on
    ls.sample_no = ss.sample_no
    and ls.study_id = ss.study_id
inner join d_sampmain as sm on
    ss.sample_id = sm.sample_id
    and ss.study_id = sm.study_id
inner join d_sampcoll as sc on
    sm.sampcoll_id = sc.sampcoll_id
    and sm.study_id = sc.study_id
inner join d_studylocation as sl on
    sc.study_loc_id = sl.study_loc_id
    and sc.study_id = sl.study_id
inner join d_location as loc on
    sl.location_id = loc.location_id
inner join d_study as st on
    sl.study_id = st.study_id
inner join e_lab as el on
    lr.lab = el.lab
inner join e_analyte as ea on
    lr.analyte = ea.analyte
inner join e_analmethod as am on
    lr.method_code = am.method_code
inner join e_sampmaterial as resmat on
    lr.material_analyzed = resmat.sample_material
left join e_qalevel as qa on
    lr.qa_level = qa.qa_level
left join e_loctype as lt on
    loc.loc_type = lt.loc_type
left join e_locmethod as locm on
    sl.loc_method = locm.loc_method
left join e_collscheme as cs on
    sc.coll_scheme = cs.coll_scheme
left join (
        select
            sd.study_id,
            sd.sample_id,
            string_agg(
                doc.title,
                '; '
            ) as sample_doc
        from
            d_sampdoc as sd
        inner join d_document as doc on
            sd.doc_id = doc.doc_id
        group by
            sd.study_id,
            sd.sample_id
    ) as sdoc on
    sm.study_id = sdoc.study_id
    and sm.sample_id = sdoc.sample_id
left join (
        select
            df.doc_id,
            df.filename,
            f.original_filename as doc_file
        from
            d_docfile as df
        inner join d_file as f on
            df.filename = f.filename
    ) lrdoc on
    lr.doc_id = lrdoc.doc_id
    and lr.doc_file = lrdoc.filename
    left join (
            select
                *
            from
                d_area
            where
                d_area.area_type::text = 'Region'::text
        ) reg on
        st_intersects(
            loc.loc_geom,
            reg.area_geom
        )
left join e_unit as u1 on u1.unit = sm.depth_units
cross join (select * from e_unit where unit = 'm') as u2
where
    lr.reportable
order by
    loc.location_id,
    sc.sample_date,
    sm.sample_material,
    sm.upper_depth,
    sm.lower_depth,
    sm.sample_id,
    ss.sample_no,
    lr.lab,
    lr.labsample,
    lr.method_code,
    ea.chem_class,
    lr.analyte,
    lr.meas_basis,
    lr.fraction
with data;
