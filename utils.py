from datetime import datetime
def format_date (iso_date_string ):
    try :
        dt =datetime .fromisoformat (iso_date_string .replace ("Z","+00:00"))
        return dt .strftime ("%Y-%m-%d %H:%M UTC")
    except ValueError :
        return iso_date_string
def get_state_explanation (state ):
    explanations ={
    "opened":"Готово к рассмотрению",
    "merged":"Успешно объединено",
    "closed":"Закрыто без слияния",
    "locked":"Locked (no new discussions)",
    "draft":"Работа в процессе",
    }
    return explanations .get (state ,state )
def get_pipeline_status_icon (status ):
    if not status :
        return "⚪"
    icons ={
    "success":"✅",
    "failed":"❌",
    "running":"🔄",
    "pending":"⏳",
    "canceled":"⏹️",
    "skipped":"⏭️",
    "manual":"👤",
    }
    return icons .get (status ,"❓")
def calculate_change_stats (changes ):
    if not changes or "changes"not in changes :
        return "Никаких изменений"
    additions =0
    deletions =0
    for change in changes ["changes"]:
        if "diff"in change :
            diff_lines =change ["diff"].split ("\n")
            for line in diff_lines :
                if line .startswith ("+")and not line .startswith ("+++"):
                    additions +=1
                elif line .startswith ("-")and not line .startswith ("---"):
                    deletions +=1
    return f"+{additions }/-{deletions }"
def analyze_mr_readiness (mr_data ,pipeline_data =None ,approvals =None ):
    blockers =[]
    if mr_data .get ("draft")or mr_data .get ("work_in_progress"):
        blockers .append ("🚧 Статус проекта/незавершенного проекта")
    if mr_data .get ("has_conflicts"):
        blockers .append ("⚠️ Объединение конфликтов")
    if pipeline_data and pipeline_data .get ("status")=="failed":
        blockers .append ("❌ Трубопровод вышел из строя")
    elif pipeline_data and pipeline_data .get ("status")=="running":
        blockers .append ("🔄 Прокладка трубопровода")
    if approvals and "approvals_required"in approvals :
        approved_count =len (approvals .get ("approved_by",[]))
        required_count =approvals .get ("approvals_required",0 )
        if approved_count <required_count :
            msg =f"👥 Needs approval ({approved_count }/{required_count })"
            blockers .append (msg )
    if mr_data .get ("merge_status")=="cannot_be_merged":
        blockers .append ("🚫 Невозможно объединить")
    if not blockers :
        return "✅ Готов к слиянию"
    else :
        return f"🚫 Blocked by: {', '.join (blockers )}"
def get_mr_priority (mr_data ):
    labels =mr_data .get ("labels",[])
    for label in labels :
        if "critical"in label .lower ()or "urgent"in label .lower ():
            return "🔴 Критический"
        elif "high"in label .lower ():
            return "🟡 Высокий"
        elif "low"in label .lower ():
            return "🟢 Низкий"
    return "⚪ Нормальный"