import json
from flask import Flask, request, Response
import language_tool_python

application = app = Flask(__name__)
my_tool = language_tool_python.LanguageTool('en-US')


class ResponseData(object):
    def __init__(self):
        self.json_data = {
          "errno": 0,
          "message": "success",
          "data": [],
        }


def convert_to_new_json_format_v2(data, original_text, response_data, corrected_text):
    for error in data:
        item_data = {"word": original_text[error.offset:(error.offset + error.errorLength)],
                     "substitute": error.replacements[0], "description": error.message,
                     "to": error.offset + error.errorLength, "explanation": error.message, "existence": True}
        if error.ruleIssueType == 'misspelling' or error.ruleIssueType == 'typographical':
            item_data['type'] = 'spelling'
        else:
            item_data['type'] = 'grammar'
        pre_error_text = original_text[:error.offset]
        post_error_text = original_text[(error.offset + error.errorLength):]
        item_data["example"] = [
            {
                "correct": [pre_error_text + replacement + post_error_text for replacement in error.replacements],
                "incorrect": original_text
            }
        ]
        response_data.json_data["data"].append(item_data)
    return response_data


def check_for_errors(text):
    matches = my_tool.check(text)
    corrections = language_tool_python.utils.correct(text, matches)
    return matches, corrections


def validate_request(req_json):
    try:
        original_text = req_json['text']
    except (TypeError, KeyError):
        return json.dumps({"error": "Please send the parameter 'text' with your request."}), None
    if len(original_text) == 0:
        return json.dumps({"error": "Input text too short."}), None
    return None, original_text


@app.route("/api/v1/textCheck", methods=['POST'])
def check_grammar():
    req_json = request.get_json()

    # RETURN ERROR IF BAD VALIDATION
    validation_result, original_text = validate_request(req_json)
    if validation_result:
        return Response(validation_result,
                        status=200, mimetype='application/json')

    # RESPONSE DATA CLASS
    response_data = ResponseData()
    results, corrected_text = check_for_errors(original_text)

    response_data = convert_to_new_json_format_v2(results, original_text, response_data, corrected_text)

    # SEND RES TO CLIENT
    res = json.dumps(response_data.json_data)
    res = Response(res, status=200, mimetype='application/json')
    return res


@app.errorhandler(404)
def not_found(error):
    return Response(json.dumps({'error': 'Not found'}), status=404, mimetype='application/json')


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=3000,
    )
