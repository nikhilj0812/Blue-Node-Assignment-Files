import os
import json
import pandas as pd
import logging

# Create and configure logger
logging.basicConfig(filename="parse.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')

# Creating an object
logger = logging.getLogger()

final_result = []


def parse():
    current_path = os.getcwd()
    logger.info("reading different files ....")
    input_file   = f"{current_path}/input_file.txt"
    std_def      = f"{current_path}/standard_definition.json"
    err_code     = f"{current_path}/error_codes.json"
    std_def      = open(std_def, "r")

    data   = json.load(std_def)
    os.remove("summary.txt") if os.path.exists("summary.txt") else None
    with open(err_code, "r") as e:
        errors = json.loads(e.read())
    with open(input_file, "r") as f:
        for line in f:
            line = line.strip("\n")
            line = line.rstrip()
            inputs = line.split("&")
            inputs = remove_empty_list_element(inputs)
            for d in data:
                if d['key'] == inputs[0]:
                    for ints in range(1, len(inputs)):
                        results = {}
                        given_datatype = check_data_type(inputs, ints)
                        given_length = len(inputs[ints])
                        expected_length = d['sub_sections'][ints - 1]['max_length']
                        expected_datatype = d['sub_sections'][ints -1]['data_type']
                        sub_section = d['sub_sections'][ints -1]['key']
                        section = d["key"]
                        error_code = check_error_code(given_length, expected_length, given_datatype, expected_datatype)

                        results.update({
                            "Section": section,
                            "Sub-Section": sub_section,
                            "Given DataType": given_datatype,
                            "Expected DataType": expected_datatype,
                            "Given Length": given_length,
                            "Expected MaxLength": expected_length,
                            "Error Code": error_code
                        })
                        final_result.append(results)
                        generate_summary(error_code, errors, section, sub_section, given_datatype, given_length)


def generate_report():
    '''
    Generate excel report from parsed data.
    '''
    # Create an new Excel file and add a worksheet.
    df = pd.DataFrame(final_result)

    # saving the dataframe
    df.to_csv('report.csv')


def generate_summary(error_code, errors, section, sub_section, data_type, max_length):
    '''
    Generate summary report in txt format based error codes.
    '''
    with open("summary.txt", "a") as wf:
        for err in errors:
            if err['code'] == error_code:
                errs = err['message_template']
                errs = errs.replace("LXY", sub_section)
                errs = errs.replace("LX", section)
                errs = errs.replace("{data_type}", data_type)
                errs = errs.replace("{max_length}", str(max_length))
                wf.write(errs)
                wf.write("\n")


def remove_empty_list_element(inputs):
    '''
    To remove empty last element from the data list.
    '''
    if inputs[-1] == '':
        inputs.pop(-1)
    return inputs


def check_data_type(inputs, ints):
    '''
    To check the data type of passed input
    :return: data type i.e. digits, word character etc
    '''
    if (inputs[ints]).isalpha():
        given_datatype = 'word_characters'
    elif (inputs[ints]).isdigit():
        given_datatype = 'digits'
    else:
        given_datatype = 'others'
    return given_datatype


def check_error_code(given_length, expected_length, given_datatype, expected_datatype):
    '''
    To find out the error code.
    :return: error code
    '''
    if given_length == expected_length and given_datatype == expected_datatype:
        error_code = 'E01'
    elif given_length == expected_length and given_datatype != expected_datatype:
        error_code = 'E02'
    elif given_length != expected_length and given_datatype == expected_datatype:
        error_code = 'E03'
    elif given_length != expected_length and given_datatype != expected_datatype:
        error_code = 'E04'
    else:
        error_code = 'E05'
    return error_code


if __name__ == '__main__':
    logger.info("parse started ....")
    parse()
    logger.info("generate report ....")
    generate_report()
    logger.info("parse completed ....")
