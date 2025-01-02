merge `{table_ref}` as T
using `{temp_table}` as S
on T.detail_link = S.detail_link
when matched then
    update set
        monthly_salary = S.monthly_salary,
        occupation = S.occupation,
        work_type = S.work_type,
        work_location = S.work_location,
        industry = S.industry,
        job_content = S.job_content,
        required_skills = S.required_skills,
        preferred_skills = S.preferred_skills,
        programming_language = S.programming_language,
        tool = S.tool,
        framework = S.framework,
        rate_of_work = S.rate_of_work,
        number_of_recruitment_interviews = S.number_of_recruitment_interviews,
        number_of_days_worked = S.number_of_days_worked,
        number_of_applicants = S.number_of_applicants,
        job_title = S.job_title,
        listing_start_date = S.listing_start_date
when not matched then
    insert (
        monthly_salary,
        occupation,
        work_type,
        work_location,
        industry,
        job_content,
        required_skills,
        preferred_skills,
        programming_language,
        tool,
        framework,
        rate_of_work,
        number_of_recruitment_interviews,
        number_of_days_worked,
        number_of_applicants,
        job_title,
        listing_start_date,
        detail_link
    )
    values (
        S.monthly_salary,
        S.occupation,
        S.work_type,
        S.work_location,
        S.industry,
        S.job_content,
        S.required_skills,
        S.preferred_skills,
        S.programming_language,
        S.tool,
        S.framework,
        S.rate_of_work,
        S.number_of_recruitment_interviews,
        S.number_of_days_worked,
        S.number_of_applicants,
        S.job_title,
        S.listing_start_date,
        S.detail_link
    )