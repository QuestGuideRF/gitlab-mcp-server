import logging
from mcp .types import TextContent
from gitlab_api import get_merge_request_pipeline as api_get_merge_request_pipeline
from gitlab_api import get_pipeline_jobs
from utils import format_date ,get_pipeline_status_icon
async def get_merge_request_pipeline (gitlab_url ,project_id ,access_token ,args ):
    logging .info (f"get_merge_request_pipeline called with args: {args }")
    mr_iid =args ["merge_request_iid"]
    try :
        status ,pipeline_data ,error =await api_get_merge_request_pipeline (
        gitlab_url ,project_id ,access_token ,mr_iid
        )
    except Exception as e :
        logging .error (f"Error fetching pipeline: {e }")
        raise Exception (f"Error fetching merge request pipeline: {e }")
    if status !=200 :
        logging .error (f"Error fetching pipeline: {status } - {error }")
        raise Exception (f"Error fetching merge request pipeline: {status } - {error }")
    if not pipeline_data :
        result =f"# 🔧 Pipeline for Merge Request !{mr_iid }\n\n"
        result +="ℹ️ Для этого мерж-реквеста не найден конвейер.\n\n"
        result +="Это может означать:\n"
        result +="• Для этого проекта не настроен CI/CD\n"
        result +="• Конвейер еще не запущен\n"
        result +="• Ветка мерж-реквеста не имеет коммитов\n"
        return [TextContent (type ="text",text =result )]
    pipeline_id =pipeline_data .get ("id")
    jobs_data =[]
    if pipeline_id :
        try :
            jobs_status ,jobs_data ,jobs_error =await get_pipeline_jobs (
            gitlab_url ,project_id ,access_token ,pipeline_id
            )
            if jobs_status !=200 :
                logging .warning (f"Could not fetch jobs: {jobs_status } - {jobs_error }")
                jobs_data =[]
        except Exception as e :
            logging .warning (f"Error fetching jobs: {e }")
            jobs_data =[]
    pipeline_status =pipeline_data .get ("status","unknown")
    pipeline_icon =get_pipeline_status_icon (pipeline_status )
    result =f"# {pipeline_icon } Pipeline for Merge Request !{mr_iid }\n\n"
    result +="## 📊 Обзор конвейера\n"
    result +=f"**🆔 Pipeline ID**: #{pipeline_data .get ('id','N/A')}\n"
    result +=f"**📊 Status**: {pipeline_icon } {pipeline_status }\n"
    result +=f"**🔗 SHA**: `{pipeline_data .get ('sha','N/A')[:8 ]}`\n"
    result +=f"**🌿 Ref**: `{pipeline_data .get ('ref','N/A')}`\n"
    if pipeline_data .get ("source"):
        result +=f"**📍 Source**: {pipeline_data ['source']}\n"
    if pipeline_data .get ("created_at"):
        result +=f"**📅 Created**: {format_date (pipeline_data ['created_at'])}\n"
    if pipeline_data .get ("updated_at"):
        result +=f"**🔄 Updated**: {format_date (pipeline_data ['updated_at'])}\n"
    if pipeline_data .get ("started_at"):
        result +=f"**▶️ Started**: {format_date (pipeline_data ['started_at'])}\n"
    if pipeline_data .get ("finished_at"):
        result +=f"**⏹️ Finished**: {format_date (pipeline_data ['finished_at'])}\n"
    if pipeline_data .get ("duration"):
        duration_mins =pipeline_data ["duration"]//60
        duration_secs =pipeline_data ["duration"]%60
        result +=f"**⏱️ Duration**: {duration_mins }m {duration_secs }s\n"
    if pipeline_data .get ("queued_duration"):
        queued_mins =pipeline_data ["queued_duration"]//60
        queued_secs =pipeline_data ["queued_duration"]%60
        result +=f"**⏳ Queued**: {queued_mins }m {queued_secs }s\n"
    result +="\n"
    if pipeline_data .get ("user"):
        user =pipeline_data ["user"]
        result +="## 👤 Активировано\n"
        result +=f"**Name**: {user .get ('name','N/A')}\n"
        result +=f"**Username**: @{user .get ('username','N/A')}\n"
        result +="\n"
    if pipeline_data .get ("coverage"):
        result +="## 📈 Покрытие кода\n"
        result +=f"**Coverage**: {pipeline_data ['coverage']}%\n"
        result +="\n"
    if pipeline_data .get ("web_url"):
        result +="## 🔗 Действия\n"
        result +=f"• [View Pipeline Details]({pipeline_data ['web_url']})\n"
        result +="\n"
    if jobs_data :
        result +="## 🔨 Задания конвейера\n\n"
        failed_jobs =[j for j in jobs_data if j .get ("status")=="failed"]
        success_jobs =[j for j in jobs_data if j .get ("status")=="success"]
        running_jobs =[j for j in jobs_data if j .get ("status")=="running"]
        other_jobs =[j for j in jobs_data if j .get ("status")not in ["failed","success","running"]]
        result +=f"**Total Jobs**: {len (jobs_data )}\n"
        result +=f"**✅ Success**: {len (success_jobs )} | "
        result +=f"**❌ Failed**: {len (failed_jobs )} | "
        result +=f"**🔄 Running**: {len (running_jobs )} | "
        result +=f"**⏳ Other**: {len (other_jobs )}\n\n"
        if failed_jobs :
            result +="### ❌ Неудачные задания\n\n"
            for job in failed_jobs :
                job_icon =get_pipeline_status_icon (job .get ("status"))
                result +=f"- {job_icon } **{job .get ('name','Неизвестная работа')}** "
                result +=f"(Job ID: `{job .get ('id')}`, Stage: {job .get ('stage','N/A')})"
                if job .get ("duration"):
                    duration_mins =int (job ["duration"])//60
                    duration_secs =int (job ["duration"])%60
                    result +=f" - {duration_mins }m {duration_secs }s"
                if job .get ("web_url"):
                    result +=f" - [View]({job ['web_url']})"
                result +="\n"
            result +="\n*💡 Совет: используйте get_job_log с идентификатором задания, чтобы увидеть полный вывод*\n"
            result +="\n"
        if running_jobs :
            result +="### 🔄 Выполнение заданий\n\n"
            for job in running_jobs :
                job_icon =get_pipeline_status_icon (job .get ("status"))
                result +=f"- {job_icon } **{job .get ('name','Неизвестная работа')}** "
                result +=f"(Job ID: `{job .get ('id')}`, Stage: {job .get ('stage','N/A')})"
                if job .get ("web_url"):
                    result +=f" - [View]({job ['web_url']})"
                result +="\n"
            result +="\n"
        if success_jobs :
            result +="### ✅ Успешные вакансии\n\n"
            for job in success_jobs :
                result +=f"- ✅ **{job .get ('name','Неизвестная работа')}** "
                result +=f"(Job ID: `{job .get ('id')}`, Stage: {job .get ('stage','N/A')})"
                if job .get ("duration"):
                    duration_mins =int (job ["duration"])//60
                    duration_secs =int (job ["duration"])%60
                    result +=f" - {duration_mins }m {duration_secs }s"
                result +="\n"
            result +="\n"
        if other_jobs :
            result +="### ⏳ Другие вакансии\n\n"
            for job in other_jobs :
                job_icon =get_pipeline_status_icon (job .get ("status"))
                result +=f"- {job_icon } **{job .get ('name','Неизвестная работа')}** "
                result +=f"(Job ID: `{job .get ('id')}`, Stage: {job .get ('stage','N/A')}, "
                result +=f"Status: {job .get ('status','N/A')})\n"
            result +="\n"
    result +="## ℹ️ Информация о статусе\n"
    status_explanations ={
    "success":"✅ Все задания пройдены успешно",
    "failed":"❌ Не удалось выполнить одно или несколько заданий.",
    "running":"🔄 Трубопровод в настоящее время работает",
    "pending":"⏳ Конвейер ожидает запуска",
    "canceled":"⏹️ Трубопровод отменен",
    "skipped":"⏭️ Конвейер был пропущен",
    "manual":"👤 Ожидание ручного действия",
    "created":"📝 Конвейер создан, но не запущен",
    "preparing":"🔧 Трубопровод готовится к запуску",
    "waiting_for_resource":"⏸️ Ждём свободных ресурсов",
    "scheduled":"📅 Запланирован запуск трубопровода",
    }
    explanation =status_explanations .get (pipeline_status ,f"Unknown status: {pipeline_status }")
    result +=f"{explanation }\n"
    return [TextContent (type ="text",text =result )]