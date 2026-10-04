"""Evaluate the reviewed workflow JavaScript locally without network/credentials."""
import json
import shutil
import subprocess


def evaluate_js(module, expression, values):
    node = shutil.which("node")
    assert node, "Node.js is required to verify the actual n8n orchestration code"
    program = ("const f=require(" + json.dumps(str(module)) + ");"
               "const v=JSON.parse(require('fs').readFileSync(0,'utf8'));"
               "console.log(JSON.stringify(" + expression + "));")
    completed = subprocess.run([node, "-e", program], input=json.dumps(values),
                               text=True, encoding="utf-8", capture_output=True, check=True)
    return json.loads(completed.stdout)
