-- refresh materialized view app.ctd with data;

drop materialized view if exists app.ctd;
create materialized view app.ctd as
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
    sl.study_loc_id,
    sdoc.sample_doc,
    sc.sample_date,
    sch.description as coll_scheme,
    sm.sample_material,
    sm.sample_id,
    sm.description as sample_desc,
    sm.upper_depth,
    sm.lower_depth,
    sm.depth_units,
    cs.comments,
    smc.description as parameter,
    fmm.description as meas_method,
    cs.replicate,
    (cs.meas_value).value as result,
    cs.units as units,
    case
        when (cs.meas_value).undetected then 'False'
        else 'True'
        end::text as detected,
    case
        when
            not (cs.meas_value).undetected
        and not (cs.meas_value).estimated
        and not (cs.meas_value).rejected
        and not (cs.meas_value).greater_than
        then null
        else
            case
            when (cs.meas_value).undetected then 'U'
            else ''
        end
                || case
            when (cs.meas_value).estimated then 'J'
            else ''
        end
                || case
            when (cs.meas_value).rejected then 'R'
            else ''
        end
                || case
            when (cs.meas_value).greater_than then '>'
            else ''
        end
    end as qualifiers,
    cs.validator_flags,
    cs.qa_level,
    cs.data_quality
from
        d_sampmeas as cs
inner join d_sampmain as sm on
    sm.study_id = cs.study_id
    and sm.sample_id = cs.sample_id
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
inner join e_sampmeascode as smc on
    cs.samp_measurement = smc.samp_measurement
inner join e_fieldmeasmethod as fmm on
    cs.field_meas_method = fmm.field_meas_method
left join e_loctype as lt on
    loc.loc_type = lt.loc_type
left join e_collscheme as sch on
    sc.coll_scheme = sch.coll_scheme
left join (
        select
                sd.study_id,
            sd.sample_id,
                string_agg(
                doc.authors,
                '; '
            ) as authors,
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
left join e_locmethod as locm on sl.loc_method=locm.loc_method
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
    cs.reportable
    and (loc.loc_type != 'Mooring' or loc.loc_type is null)
order by
        loc.location_id,
        sc.sample_date,
        sm.study_id,
        sm.sample_id,
        smc.description,
        fmm.description,
        cs.replicate
with data;
