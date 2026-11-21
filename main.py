import asyncio
import logging
from typing import Any ,Dict ,List
from mcp .server import Server
from mcp .server .models import InitializationOptions
from mcp .server .stdio import stdio_server
from mcp .types import INTERNAL_ERROR ,INVALID_PARAMS ,METHOD_NOT_FOUND ,JSONRPCError ,TextContent ,Tool
from config import get_gitlab_config
from logging_config import configure_logging
from tools import (
create_review_comment ,
get_branch_merge_requests ,
get_commit_discussions ,
get_job_log ,
get_merge_request_details ,
get_merge_request_pipeline ,
get_merge_request_reviews ,
get_merge_request_test_report ,
get_pipeline_test_summary ,
list_merge_requests ,
reply_to_review_comment ,
resolve_review_discussion ,
)
class GitLabMCPServer :
    def __init__ (self ):
        configure_logging ()
        logging .info ("Инициализация GitLabMCPServer")
        self .config =get_gitlab_config ()
        self .server =Server (self .config ["server_name"])
        self .setup_handlers ()
    def setup_handlers (self ):
        @self .server .list_tools ()
        async def list_tools ()->List [Tool ]:
            logging .info ("list_tools вызывается")
            tools =[
            Tool (
            name ="list_merge_requests",
            description ="Получение списка мерж-реквестов для проекта GitLab",
            inputSchema ={
            "type":"object",
            "properties":{
            "state":{
            "type":"string",
            "enum":["opened","closed","merged","all"],
            "default":"opened",
            "description":"Фильтровать по состоянию мерж-реквеста",
            },
            "target_branch":{"type":"string","description":("Фильтровать по целевой ветке (необязательно)")},
            "limit":{
            "type":"integer",
            "default":10 ,
            "minimum":1 ,
            "maximum":100 ,
            "description":"Максимальное количество результатов",
            },
            },
            "additionalProperties":False ,
            },
            ),
            Tool (
            name ="get_merge_request_reviews",
            description =("Получайте отзывы и обсуждения по конкретному "  "запрос на слияние"),
            inputSchema ={
            "type":"object",
            "properties":{
            "merge_request_iid":{
            "type":"integer",
            "minimum":1 ,
            "description":("Внутренний идентификатор мерж-реквеста"),
            }
            },
            "required":["merge_request_iid"],
            "additionalProperties":False ,
            },
            ),
            Tool (
            name ="get_merge_request_details",
            description =("Получите подробную информацию о конкретном "  "запрос на слияние"),
            inputSchema ={
            "type":"object",
            "properties":{
            "merge_request_iid":{
            "type":"integer",
            "minimum":1 ,
            "description":("Внутренний идентификатор мерж-реквеста"),
            }
            },
            "required":["merge_request_iid"],
            "additionalProperties":False ,
            },
            ),
            Tool (
            name ="get_merge_request_pipeline",
            description =(
            "Получите последние данные конвейера для конкретного слияния. "
            "запрос, включая все задания и их статусы. "
            "Возвращает идентификаторы заданий, которые можно использовать с get_job_log. "
            "для получения подробного вывода."
            ),
            inputSchema ={
            "type":"object",
            "properties":{
            "merge_request_iid":{
            "type":"integer",
            "minimum":1 ,
            "description":("Внутренний идентификатор мерж-реквеста"),
            }
            },
            "required":["merge_request_iid"],
            "additionalProperties":False ,
            },
            ),
            Tool (
            name ="get_merge_request_test_report",
            description =(
            "Получите структурированный отчет о тестировании для мерж-реквеста "
            "с конкретными неудачными тестами, сообщениями об ошибках и "
            "стек следов. Показывает те же тестовые данные, что и на "
            "страница GitLab MR. Лучше всего подходит для отладки неудачных тестов."
            ),
            inputSchema ={
            "type":"object",
            "properties":{
            "merge_request_iid":{
            "type":"integer",
            "minimum":1 ,
            "description":("Внутренний идентификатор мерж-реквеста"),
            }
            },
            "required":["merge_request_iid"],
            "additionalProperties":False ,
            },
            ),
            Tool (
            name ="get_pipeline_test_summary",
            description =(
            "Получить сводку теста для мерж-реквеста — "
            "облегченный обзор, показывающий количество пройденных/неудачных результатов "
            "за набор тестов. Быстрее, чем полный отчет об испытаниях. "
            "Отлично подходит для быстрой проверки статуса."
            ),
            inputSchema ={
            "type":"object",
            "properties":{
            "merge_request_iid":{
            "type":"integer",
            "minimum":1 ,
            "description":("Внутренний идентификатор мерж-реквеста"),
            }
            },
            "required":["merge_request_iid"],
            "additionalProperties":False ,
            },
            ),
            Tool (
            name ="get_job_log",
            description =(
            "Получите выходные данные трассировки/журнала для определенного конвейера. "
            "работа. Идеально подходит для отладки неудачных тестов и "
            "понимание сбоев CI/CD."
            ),
            inputSchema ={
            "type":"object",
            "properties":{
            "job_id":{
            "type":"integer",
            "minimum":1 ,
            "description":("Идентификатор задания конвейера (полученный из "  "get_merge_request_pipeline)"),
            }
            },
            "required":["job_id"],
            "additionalProperties":False ,
            },
            ),
            Tool (
            name ="get_branch_merge_requests",
            description =("Получить все мерж-реквесты для конкретной ветки"),
            inputSchema ={
            "type":"object",
            "properties":{"branch_name":{"type":"string","description":"Название филиала"}},
            "required":["branch_name"],
            "additionalProperties":False ,
            },
            ),
            Tool (
            name ="reply_to_review_comment",
            description =("Ответить на конкретную ветку обсуждения в "  "проверка мерж-реквеста"),
            inputSchema ={
            "type":"object",
            "properties":{
            "merge_request_iid":{
            "type":"integer",
            "minimum":1 ,
            "description":("Внутренний идентификатор мерж-реквеста"),
            },
            "discussion_id":{
            "type":"string",
            "description":("Идентификатор ветки обсуждения, на которую нужно ответить"),
            },
            "body":{"type":"string","description":"Содержание ответного комментария"},
            },
            "required":["merge_request_iid","discussion_id","body"],
            "additionalProperties":False ,
            },
            ),
            Tool (
            name ="create_review_comment",
            description =("Создайте новую ветку обсуждения в "  "проверка мерж-реквеста"),
            inputSchema ={
            "type":"object",
            "properties":{
            "merge_request_iid":{
            "type":"integer",
            "minimum":1 ,
            "description":("Внутренний идентификатор мерж-реквеста"),
            },
            "body":{"type":"string","description":("Содержание нового комментария в обсуждении")},
            },
            "required":["merge_request_iid","body"],
            "additionalProperties":False ,
            },
            ),
            Tool (
            name ="resolve_review_discussion",
            description =("Разрешить или отменить решение ветки обсуждения в "  "проверка мерж-реквеста"),
            inputSchema ={
            "type":"object",
            "properties":{
            "merge_request_iid":{
            "type":"integer",
            "minimum":1 ,
            "description":("Внутренний идентификатор мерж-реквеста"),
            },
            "discussion_id":{
            "type":"string",
            "description":("ID ветки обсуждения "  "resolve/unresolve"),
            },
            "resolved":{
            "type":"boolean",
            "default":True ,
            "description":("Whether to resolve (true) or unresolve "  "(ложь) обсуждение"),
            },
            },
            "required":["merge_request_iid","discussion_id"],
            "additionalProperties":False ,
            },
            ),
            Tool (
            name ="get_commit_discussions",
            description =("Получайте обсуждения и комментарии к коммитам в течение "  "конкретный мерж-реквест"),
            inputSchema ={
            "type":"object",
            "properties":{
            "merge_request_iid":{
            "type":"integer",
            "minimum":1 ,
            "description":("Внутренний идентификатор мерж-реквеста"),
            }
            },
            "required":["merge_request_iid"],
            "additionalProperties":False ,
            },
            ),
            ]
            tool_names =[t .name for t in tools ]
            logging .info (f"Returning {len (tools )} tools: {tool_names }")
            return tools
        @self .server .call_tool ()
        async def call_tool (name :str ,arguments :Dict [str ,Any ])->List [TextContent ]:
            logging .info (f"call_tool called: {name } with arguments: {arguments }")
            try :
                if name not in [
                "list_merge_requests",
                "get_merge_request_reviews",
                "get_merge_request_details",
                "get_merge_request_pipeline",
                "get_merge_request_test_report",
                "get_pipeline_test_summary",
                "get_job_log",
                "get_branch_merge_requests",
                "reply_to_review_comment",
                "create_review_comment",
                "resolve_review_discussion",
                "get_commit_discussions",
                ]:
                    logging .warning (f"Unknown tool called: {name }")
                    raise JSONRPCError (METHOD_NOT_FOUND ,f"Unknown tool: {name }")
                if name =="list_merge_requests":
                    return await list_merge_requests (
                    self .config ["gitlab_url"],self .config ["project_id"],self .config ["access_token"],arguments
                    )
                elif name =="get_merge_request_reviews":
                    return await get_merge_request_reviews (
                    self .config ["gitlab_url"],self .config ["project_id"],self .config ["access_token"],arguments
                    )
                elif name =="get_merge_request_details":
                    return await get_merge_request_details (
                    self .config ["gitlab_url"],self .config ["project_id"],self .config ["access_token"],arguments
                    )
                elif name =="get_merge_request_pipeline":
                    return await get_merge_request_pipeline (
                    self .config ["gitlab_url"],self .config ["project_id"],self .config ["access_token"],arguments
                    )
                elif name =="get_merge_request_test_report":
                    return await get_merge_request_test_report (
                    self .config ["gitlab_url"],self .config ["project_id"],self .config ["access_token"],arguments
                    )
                elif name =="get_pipeline_test_summary":
                    return await get_pipeline_test_summary (
                    self .config ["gitlab_url"],self .config ["project_id"],self .config ["access_token"],arguments
                    )
                elif name =="get_job_log":
                    return await get_job_log (
                    self .config ["gitlab_url"],self .config ["project_id"],self .config ["access_token"],arguments
                    )
                elif name =="get_branch_merge_requests":
                    return await get_branch_merge_requests (
                    self .config ["gitlab_url"],self .config ["project_id"],self .config ["access_token"],arguments
                    )
                elif name =="reply_to_review_comment":
                    return await reply_to_review_comment (
                    self .config ["gitlab_url"],self .config ["project_id"],self .config ["access_token"],arguments
                    )
                elif name =="create_review_comment":
                    return await create_review_comment (
                    self .config ["gitlab_url"],self .config ["project_id"],self .config ["access_token"],arguments
                    )
                elif name =="resolve_review_discussion":
                    return await resolve_review_discussion (
                    self .config ["gitlab_url"],self .config ["project_id"],self .config ["access_token"],arguments
                    )
                elif name =="get_commit_discussions":
                    return await get_commit_discussions (
                    self .config ["gitlab_url"],self .config ["project_id"],self .config ["access_token"],arguments
                    )
            except JSONRPCError :
                raise
            except ValueError as e :
                logging .error (f"Validation error in {name }: {e }")
                raise JSONRPCError (INVALID_PARAMS ,f"Invalid parameters: {str (e )}")
            except Exception as e :
                logging .error (f"Unexpected error in call_tool for {name }: {e }",exc_info =True )
                raise JSONRPCError (INTERNAL_ERROR ,f"Internal server error: {str (e )}")
    async def run (self ):
        logging .info ("Запуск MCP stdio-сервера")
        try :
            async with stdio_server ()as (read_stream ,write_stream ):
                logging .info ("Контекст stdio_server введен успешно")
                await self .server .run (
                read_stream ,
                write_stream ,
                InitializationOptions (
                server_name =self .config ["server_name"],
                server_version =self .config ["server_version"],
                capabilities ={"tools":{},"logging":{}},
                ),
                )
        except Exception as e :
            logging .error (f"Error in stdio_server: {e }",exc_info =True )
            raise
async def main ():
    try :
        logging .info ("Запуск основной функции")
        server =GitLabMCPServer ()
        logging .info ("GitLabMCPServer успешно создан")
        await server .run ()
    except Exception as e :
        logging .error (f"Error starting server: {e }",exc_info =True )
        print (f"Error starting server: {e }")
        return 1
if __name__ =="__main__":
    asyncio .run (main ())