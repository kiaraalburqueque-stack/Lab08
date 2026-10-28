"""Exercise a real server with requests and save reproducible HTTP evidence."""
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time

import requests

ROOT = Path(__file__).resolve().parents[1]


def main():
    records = []
    with tempfile.TemporaryDirectory(prefix=".http-test-", dir=ROOT) as temp:
        env = {**os.environ, "DJANGO_DB_PATH": str(Path(temp) / "test.sqlite3")}
        subprocess.run([sys.executable, "manage.py", "migrate", "--noinput"],
                       cwd=ROOT, env=env, check=True, capture_output=True)
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        base = f"http://127.0.0.1:{port}"
        session = requests.Session()
        session.trust_env = False
        with open(Path(temp) / "server.log", "w") as log:
            server = subprocess.Popen(
                [sys.executable, "manage.py", "runserver", f"127.0.0.1:{port}",
                 "--noreload"], cwd=ROOT, env=env, stdout=log, stderr=log,
            )
            try:
                for _ in range(100):
                    try:
                        if session.get(base + "/api/", timeout=1).status_code == 200:
                            break
                    except requests.RequestException:
                        pass
                    time.sleep(0.1)
                else:
                    raise RuntimeError("Server did not start")

                def call(method, path, expected, body=None, html=False):
                    response = session.request(
                        method, base + path, json=body, timeout=10,
                        headers={"Accept": "text/html" if html else "application/json"},
                    )
                    try:
                        data = response.json()
                    except ValueError:
                        data = "Browsable API HTML" if html else response.text
                    records.append({"method": method, "path": path,
                                    "body": body, "expected": expected,
                                    "status": response.status_code, "response": data})
                    assert response.status_code == expected, records[-1]
                    if html:
                        assert "text/html" in response.headers["Content-Type"]
                        assert "rest_framework" in response.text
                    return data

                call("GET", "/api/", 200)
                exam = call("POST", "/api/exams/", 201, {"title": "Python"})
                eid = exam["id"]
                call("GET", "/api/exams/", 200)
                call("GET", f"/api/exams/{eid}/", 200)
                call("PATCH", f"/api/exams/{eid}/", 200, {"description": "HTTP test"})
                payload = {"exam": eid, "text": "What is Django?", "options": [
                    {"text": "Framework", "is_correct": True},
                    {"text": "Database", "is_correct": False},
                ]}
                question = call("POST", "/api/questions/", 201, payload)
                qid = question["id"]
                call("GET", "/api/questions/", 200)
                call("GET", f"/api/questions/{qid}/", 200)
                call("PATCH", f"/api/questions/{qid}/", 200, {"text": "Django framework?"})
                option = call("POST", "/api/options/", 201, {
                    "question": qid, "text": "Language", "is_correct": False,
                })
                oid = option["id"]
                call("GET", "/api/options/", 200)
                call("GET", f"/api/options/{oid}/", 200)
                call("PATCH", f"/api/options/{oid}/", 200, {"text": "Operating system"})
                call("DELETE", f"/api/options/{oid}/", 204)
                call("GET", f"/api/options/{oid}/", 404)
                call("POST", "/api/exams/", 400, {})
                call("POST", "/api/questions/", 400, {**payload, "exam": "bad"})
                call("POST", "/api/questions/", 400, {
                    **payload, "options": [{"text": "No correct answer"}],
                })
                call("DELETE", f"/api/options/{question['options'][0]['id']}/", 400)
                call("PATCH", f"/api/questions/{qid}/", 400, {"options": []})
                call("PATCH", f"/api/questions/{qid}/", 200, {"options": [
                    {"text": "New correct", "is_correct": True},
                ]})
                for i in range(6):
                    call("POST", "/api/questions/", 201, {**payload, "text": f"Django {i}"})
                page = call("GET", f"/api/questions/?exam={eid}&search=Django", 200)
                assert page["count"] == 7 and len(page["results"]) == 5 and page["next"]
                page = call("GET", "/api/questions/?page=2", 200)
                assert len(page["results"]) == 2
                page = call("GET", "/api/questions/?search=absent", 200)
                assert page["count"] == 0
                page = call("GET", "/api/questions/?exam=99999", 200)
                assert page["count"] == 0
                call("GET", "/api/questions/?exam=bad", 400)
                for resource in ("exams", "questions", "options"):
                    call("GET", f"/api/{resource}/", 200, html=True)
                call("DELETE", f"/api/questions/{qid}/", 204)
                call("GET", f"/api/questions/{qid}/", 404)
                call("DELETE", f"/api/exams/{eid}/", 204)
                call("GET", f"/api/exams/{eid}/", 404)
            finally:
                session.close()
                if os.name == "nt":
                    subprocess.run(
                        ["taskkill", "/PID", str(server.pid), "/T", "/F"],
                        check=False, capture_output=True,
                    )
                else:
                    server.terminate()
                server.wait(timeout=15)
    target = ROOT / "docs" / "http-results.json"
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"PASS: {len(records)} HTTP requests. Evidence: {target}")


if __name__ == "__main__":
    main()
