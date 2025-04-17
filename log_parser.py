from enum import Enum
import logging

class CowrieSearchStrings(Enum):
    """
    Enumerator designed to search for specific patterns in `cowrie` log files.
    """
    COWRIE_GENERAL = "[HoneyPotSSHTransport"
    COWRIE_SSH_CMD = "CMD"
    COWRIE_SSH_LOGIN = "login attemp"

def logs_into_json(lines: list[str], string_expressions: list[CowrieSearchStrings], logger: logging.Logger) -> list[str]:
    """
    Takes a list of `lines`, and a list of `string expressions`.
    For each string expression in `string expressions`, all the lines in `lines` are examined and if a line contains the string expression, 
    it is added in a `json_logs` list.

    ### Returns
    the `json_logs` list.
    """
    json_logs = []
    
    for line in lines:
        for search_string in string_expressions:
            if search_string.value in line:

                parsed_log = parse_log(line, search_string, logger)
                json_logs.append(parsed_log)

    return json_logs

def parse_log(line: str, log_type: CowrieSearchStrings, logger: logging.Logger) -> str:
    """
    Takes a `list of lines` rapresenting the raw filtered logs, and a list of `string expressions`.

    According to the type of log (defined by the SearchString enumerator), maps the values contained in the logs in a json-like structured string.

    ### JSON structure
    
    The structure of the parsed lines will be presented as follows:

    {"timestamp": \<time_data\>, "event_type": \<eventy_type_data\>, \<variable_field_depending_on_event_type\>: \<detail_data\>, "source": \<ip\>}

    ### Returns
    the list of json-like strings.
    """
    logger.debug("String being processed: " + line)
    if log_type == CowrieSearchStrings.COWRIE_SSH_LOGIN:
        try:
            line_parts = line.rstrip().split(" ", 2)
            source = line_parts[1].split(",", 2)[2]
            crafted = "{\"timestamp\": \"" + line_parts[0] + "\", \"event_type\": \"" + log_type.value + "\", \"value\" : \"" + line_parts[2] + "\", \"source\": \"" + source + "\"}"
            logger.debug("Crafted json log: " + crafted)
        except IndexError:
            logger.error("IndexError occurred, something wrong with the logs format.")

    elif log_type == CowrieSearchStrings.COWRIE_SSH_CMD:
        try:
            line_parts = line.rstrip().split(" ", 2)
            source = line_parts[1].split(",", 2)[2]
            cmd_temp = line_parts[2].split(" ", 1)
            if len(cmd_temp) > 1:
                cmd = cmd_temp[1]
            else:
                cmd = "[empty line]"
            crafted = "{\"timestamp\": \"" + line_parts[0] + "\", \"event_type\": \"" + log_type.value + "\", \"value\" : \"" + cmd + "\", \"source\": \"" + source + "\"}"
            logger.debug("Crafted json log: " + crafted)
        except IndexError:
            logger.error("IndexError occurred, something wrong with the logs format.")
    else:
        pass
    return crafted

                