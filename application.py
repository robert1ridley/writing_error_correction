import json
from flask import Flask, request, Response
import urllib.parse
import urllib.request
from urllib.error import HTTPError
from urllib.error import URLError
import re

application = app = Flask(__name__)


class ResponseData(object):
  def __init__(self):
    self.json_data = {
      "errno": 0,
      "message": "success",
      "data": []
    }

def get_ginger_url(text):
    API_KEY = "6ae0c3a0-afdc-4532-a810-82ded0054236"
    scheme = "http"
    netloc = "services.gingersoftware.com"
    path = "/Ginger/correct/json/GingerTheText"
    params = ""
    query = urllib.parse.urlencode([
        ("lang", "US"),
        ("clientVersion", "2.0"),
        ("apiKey", API_KEY),
        ("text", text)])
    fragment = ""
    return(urllib.parse.urlunparse((scheme, netloc, path, params, query, fragment)))


def get_ginger_result(text):
    url = get_ginger_url(text)
    try:
        response = urllib.request.urlopen(url)
    except HTTPError as e:
            print("HTTP Error:", e.code)
            return e.code, True
    except URLError as e:
            print("URL Error:", e.reason)
            return e.reason, True
    try:
        result = json.loads(response.read().decode('utf-8'))
    except ValueError:
        print("Value Error: Invalid server response.")
        return "Value Error: Invalid server response", True

    return result, False


def convert_to_new_json_format(data, original_text, json_data):
  responses = data["LightGingerTheTextResult"]
  if len(responses) == 0:
      return None
  fixed_text = original_text
  fix_val = 0
  for item in responses:
      if "ShouldReplace" in item:
          if item["ShouldReplace"] != "True":
              item_data = {}
              item_data["active"] = True
              item_data["word"] = original_text[item["From"]:(item["To"]+1)]
              item_data["substitute"] = item["Suggestions"][0]["Text"]
              if item["Mistakes"][0]["CanAddToDict"]:
                  item_data["type"] = "spelling"
              else:
                  item_data["type"] = "grammar"
              if "Definition" in item["Mistakes"][0]:
                  item_data["description"] = item["Mistakes"][0]["Definition"]
              else:
                  item_data["description"] = ""
              item_data["existence"] = True
              if "Definition" in item["Suggestions"][0]:
                  item_data["explanation"] = item["Suggestions"][0]["Definition"]
              else:
                  item_data["explanation"] = ""
              fixed_text = fixed_text[:item["From"]-fix_val] + item_data["substitute"] + fixed_text[(item["To"]+1)-fix_val:]
              item_data["example"] = [
                  {
                      "incorrect": original_text,
                      "correct": []
                  }
              ]
              fix_val += (item["To"]+1) - item["From"] - len(item_data["substitute"])

              json_data["data"].append(item_data)
  for row in json_data["data"]:
    if "active" in row:
      row["example"][0]["correct"].append(fixed_text)
      del row["active"]
  return True


def validate_request(req_json):
    try:
        original_text = req_json['text']
    except (TypeError, KeyError):
        return json.dumps({"error": "Please send the parameter 'text' with your request."}), None
    if len(original_text) == 0:
        return json.dumps({"error": "Input text too short."}), None
    return None, original_text


@app.route("/api/v1/textCheck", methods = ['POST'])
def check_grammar():
    req_json = request.get_json()
    validation_result, original_text = validate_request(req_json)
    if validation_result:
        return Response(validation_result,
                        status=200, mimetype='application/json')
    response_data = ResponseData()
    if len(original_text) > 600:
      original_text = re.split(r' *[\.\?!][\'"\)\]]* *', original_text)
      for text in original_text:
        results, error = get_ginger_result(text)
        if error:
            return Response(json.dumps({"error": error}), status=200, mimetype='application/json')
        convert_to_new_json_format(results, text, response_data.json_data)
    else:
      results, error = get_ginger_result(original_text)
      if error:
        return Response(json.dumps({"error": error}), status=200, mimetype='application/json')
      convert_to_new_json_format(results, original_text, response_data.json_data)
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


