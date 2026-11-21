import logging
from mcp .types import TextContent
from gitlab_api import get_job_trace
async def get_job_log (gitlab_url ,project_id ,access_token ,args ):
    logging .info (f"get_job_log called with args: {args }")
    job_id =args ["job_id"]
    try :
        status ,log_data ,error =await get_job_trace (gitlab_url ,project_id ,access_token ,job_id )
    except Exception as e :
        logging .error (f"Error fetching job log: {e }")
        raise Exception (f"Error fetching job log: {e }")
    if status !=200 :
        logging .error (f"Error fetching job log: {status } - {error }")
        raise Exception (f"Error fetching job log: {status } - {error }")
    if not log_data or len (log_data .strip ())==0 :
        result =f"# 📋 Job Log (Job ID: {job_id })\n\n"
        result +="ℹ️ Для этого задания нет вывода журнала.\n\n"
        result +="Это может означать:\n"
        result +="• Задание еще не началось\n"
        result +="• Задание было пропущено\n"
        result +="• Журнал заархивирован или удален\n"
        return [TextContent (type ="text",text =result )]
    result =f"# 📋 Job Log (Job ID: {job_id })\n\n"
    log_size_kb =len (log_data )/1024
    result +=f"**📊 Log Size**: {log_size_kb :.2f} KB\n"
    result +=f"**📄 Lines**: {log_data .count (chr (10 ))+1 }\n\n"
    max_chars =15000
    if len (log_data )>max_chars :
        result +="## 📝 Вывод задания (последние 15 000 символов)\n\n"
        result +="```\n"
        result +=log_data [-max_chars :]
        result +="\n```\n\n"
        result +=f"*⚠️ Note: Log truncated from {len (log_data ):,} to "
        result +=f"{max_chars :,} characters (showing last portion)*\n"
    else :
        result +="## 📝 Вывод задания\n\n"
        result +="```\n"
        result +=log_data
        result +="\n```\n"
    return [TextContent (type ="text",text =result )]